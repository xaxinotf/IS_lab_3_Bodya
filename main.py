import csv
import random
import copy

# Константи для розкладу
DAYS_PER_WEEK = 5
SLOTS_PER_DAY = 4
WEEKS = ['Парний', 'Непарний']
TOTAL_SLOTS = DAYS_PER_WEEK * SLOTS_PER_DAY * len(WEEKS)

# Часові слоти з урахуванням парних/непарних тижнів
TIMESLOTS = [f"{week}, День {day+1}, Пара {slot+1}" for week in WEEKS for day in range(DAYS_PER_WEEK) for slot in range(SLOTS_PER_DAY)]

# Завантаження даних
def load_groups(filename):
    groups = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            group_id = row['GroupID']
            groups[group_id] = {
                'NumStudents': int(row['NumStudents']),
                'Subgroups': row['Subgroups'].split(';') if row['Subgroups'] else []
            }
    return groups

def load_subjects(filename):
    subjects = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subjects.append({
                'SubjectID': row['SubjectID'],
                'SubjectName': row['SubjectName'],
                'GroupID': row['GroupID'],
                'NumLectures': int(row['NumLectures']),
                'NumPracticals': int(row['NumPracticals']),
                'RequiresSubgroups': row['RequiresSubgroups'] == 'Yes',
                'WeekType': row['WeekType'] if 'WeekType' in row else 'Both'  # 'Парний', 'Непарний' або 'Both'
            })
    return subjects

def load_lecturers(filename):
    lecturers = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lecturer_id = row['LecturerID']
            lecturers[lecturer_id] = {
                'LecturerName': row['LecturerName'],
                'SubjectsCanTeach': row['SubjectsCanTeach'].split(';'),
                'TypesCanTeach': row['TypesCanTeach'].split(';'),
                'MaxHoursPerWeek': int(row['MaxHoursPerWeek'])
            }
    return lecturers

def load_auditoriums(filename):
    auditoriums = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            auditorium_id = row['AuditoriumID']
            auditoriums[auditorium_id] = int(row['Capacity'])
    return auditoriums

# Клас для подій розкладу
class Event:
    def __init__(self, timeslot, group_ids, subject_id, subject_name, lecturer_id, auditorium_id, event_type, subgroup_ids=None, week_type='Both'):
        self.timeslot = timeslot
        self.group_ids = group_ids  # Можливо, декілька груп
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.lecturer_id = lecturer_id
        self.auditorium_id = auditorium_id
        self.event_type = event_type
        self.subgroup_ids = subgroup_ids  # Словник групи: підгрупа
        self.week_type = week_type  # 'Парний', 'Непарний', 'Both'

# Клас для розкладу
class Schedule:
    def __init__(self):
        self.events = []

    def add_event(self, event):
        if event:
            self.events.append(event)

    # Оцінка розкладу (функція оцінки №1)
    def fitness(self, groups, lecturers, auditoriums):
        hard_constraints_violations = 0
        soft_constraints_score = 0

        lecturer_times = {}
        group_times = {}
        auditorium_times = {}
        lecturer_hours = {}

        for event in self.events:
            # Жорсткі обмеження
            lt_key = (event.lecturer_id, event.timeslot)
            if lt_key in lecturer_times:
                hard_constraints_violations += 1
            else:
                lecturer_times[lt_key] = event

            # Для кожної групи в події
            for group_id in event.group_ids:
                subgroup_id = event.subgroup_ids.get(group_id) if event.subgroup_ids else 'all'
                gt_key = (group_id, subgroup_id, event.timeslot)
                if gt_key in group_times:
                    hard_constraints_violations += 1
                else:
                    group_times[gt_key] = event

            # Обмеження на аудиторії
            at_key = (event.auditorium_id, event.timeslot)
            if at_key in auditorium_times:
                # Якщо це лекція та той самий викладач, дозволяємо об'єднувати
                existing_event = auditorium_times[at_key]
                if event.event_type == 'Лекція' and existing_event.event_type == 'Лекція' and event.lecturer_id == existing_event.lecturer_id:
                    # Дозволено
                    pass
                else:
                    hard_constraints_violations += 1
            else:
                auditorium_times[at_key] = event

            # Обмеження по максимальній кількості годин викладача
            week = event.timeslot.split(', ')[0]
            lecturer_hours_key = (event.lecturer_id, week)
            lecturer_hours[lecturer_hours_key] = lecturer_hours.get(lecturer_hours_key, 0) + 1.5
            if lecturer_hours[lecturer_hours_key] > lecturers[event.lecturer_id]['MaxHoursPerWeek']:
                hard_constraints_violations += 1

            # Нежорсткі обмеження
            total_group_size = sum(groups[g]['NumStudents'] // 2 if event.subgroup_ids and event.subgroup_ids.get(g) else groups[g]['NumStudents'] for g in event.group_ids)
            if auditoriums[event.auditorium_id] < total_group_size:
                soft_constraints_score += 1

            if event.subject_id not in lecturers[event.lecturer_id]['SubjectsCanTeach']:
                soft_constraints_score += 1

            if event.event_type not in lecturers[event.lecturer_id]['TypesCanTeach']:
                soft_constraints_score += 1

        # Функціонал якості №1: Мінімізуємо кількість порушень
        total_score = hard_constraints_violations * 1000 + soft_constraints_score
        return total_score

    # Альтернативна функція оцінки (функція оцінки №2)
    def fitness_alternative(self, groups, lecturers, auditoriums):
        # Враховуємо баланс навантаження викладачів та кількість вікон у розкладі
        total_penalty = self.fitness(groups, lecturers, auditoriums)  # Використовуємо першу функцію як базу

        # Додаємо м'яке обмеження на кількість вікон
        lecturer_windows = {}
        group_windows = {}

        for event in self.events:
            day_slot = event.timeslot.split(', ')
            day = day_slot[1]
            slot = int(day_slot[2].split(' ')[1])
            week = day_slot[0]

            # Для викладачів
            lecturer_key = (event.lecturer_id, week)
            if lecturer_key not in lecturer_windows:
                lecturer_windows[lecturer_key] = {}
            if day not in lecturer_windows[lecturer_key]:
                lecturer_windows[lecturer_key][day] = []
            lecturer_windows[lecturer_key][day].append(slot)

            # Для груп
            for group_id in event.group_ids:
                subgroup_id = event.subgroup_ids.get(group_id) if event.subgroup_ids else 'all'
                group_key = (group_id, subgroup_id, week)
                if group_key not in group_windows:
                    group_windows[group_key] = {}
                if day not in group_windows[group_key]:
                    group_windows[group_key][day] = []
                group_windows[group_key][day].append(slot)

        # Підраховуємо кількість вікон для викладачів
        for lecturer, days in lecturer_windows.items():
            for slots in days.values():
                slots.sort()
                windows = sum([1 for i in range(len(slots)-1) if slots[i+1] - slots[i] > 1])
                total_penalty += windows

        # Підраховуємо кількість вікон для груп
        for group, days in group_windows.items():
            for slots in days.values():
                slots.sort()
                windows = sum([1 for i in range(len(slots)-1) if slots[i+1] - slots[i] > 1])
                total_penalty += windows

        return total_penalty

# Генерація початкової популяції
def generate_initial_population(pop_size, groups, subjects, lecturers, auditoriums):
    population = []
    for _ in range(pop_size):
        schedule = Schedule()
        for subj in subjects:
            # Визначаємо, на які тижні проводиться предмет
            weeks = [subj['WeekType']] if subj['WeekType'] in WEEKS else WEEKS
            for week in weeks:
                # Лекції
                for _ in range(subj['NumLectures']):
                    event = create_random_event(subj, groups, lecturers, auditoriums, 'Лекція', week)
                    schedule.add_event(event)
                # Практичні/Лабораторні
                for _ in range(subj['NumPracticals']):
                    if subj['RequiresSubgroups']:
                        # Додаємо події для кожної підгрупи
                        for subgroup_id in groups[subj['GroupID']]['Subgroups']:
                            event = create_random_event(subj, groups, lecturers, auditoriums, 'Практика', week, {subj['GroupID']: subgroup_id})
                            schedule.add_event(event)
                    else:
                        event = create_random_event(subj, groups, lecturers, auditoriums, 'Практика', week)
                        schedule.add_event(event)
        population.append(schedule)
    return population

def create_random_event(subj, groups, lecturers, auditoriums, event_type, week_type, subgroup_ids=None):
    timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])
    suitable_lecturers = [lid for lid, l in lecturers.items()
                          if subj['SubjectID'] in l['SubjectsCanTeach'] and event_type in l['TypesCanTeach']]
    if not suitable_lecturers:
        return None
    lecturer_id = random.choice(suitable_lecturers)
    auditorium_id = random.choice(list(auditoriums.keys()))
    group_ids = [subj['GroupID']]
    return Event(timeslot, group_ids, subj['SubjectID'], subj['SubjectName'],
                 lecturer_id, auditorium_id, event_type, subgroup_ids, week_type)

# Відбір популяції
def select_population(population, groups, lecturers, auditoriums, fitness_function):
    population.sort(key=lambda x: fitness_function(x, groups, lecturers, auditoriums))
    return population[:len(population)//2] if len(population) > 1 else population

# Реалізація "травоїдного" згладжування
def herbivore_smoothing(population, best_schedule, lecturers, auditoriums):
    # Додаємо невеликі випадкові варіації навколо найкращого розкладу
    new_population = []
    for _ in range(len(population)):
        new_schedule = copy.deepcopy(best_schedule)
        mutate(new_schedule, lecturers, auditoriums, intensity=0.1)
        new_population.append(new_schedule)
    return new_population

# Реалізація "хижака"
def predator_approach(population, groups, lecturers, auditoriums, fitness_function):
    # Видаляємо найгірші розклади
    population = select_population(population, groups, lecturers, auditoriums, fitness_function)
    return population

# Реалізація "дощу"
def rain(population_size, groups, subjects, lecturers, auditoriums):
    # Додаємо нові випадкові розклади до популяції
    new_population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    return new_population

# Нетривіальна мутація
def mutate(schedule, lecturers, auditoriums, intensity=0.3):
    num_events_to_mutate = int(len(schedule.events) * intensity)
    if num_events_to_mutate < 1:
        num_events_to_mutate = 1
    events_to_mutate = random.sample(schedule.events, num_events_to_mutate)
    for event in events_to_mutate:
        # З випадковою ймовірністю змінюємо різні параметри
        if random.random() < 0.5:
            week_type = event.week_type if event.week_type in WEEKS else random.choice(WEEKS)
            event.timeslot = random.choice([t for t in TIMESLOTS if t.startswith(week_type)])
        if random.random() < 0.5:
            event.auditorium_id = random.choice(list(auditoriums.keys()))
        if random.random() < 0.5:
            suitable_lecturers = [lid for lid, l in lecturers.items()
                                  if event.subject_id in l['SubjectsCanTeach'] and event.event_type in l['TypesCanTeach']]
            if suitable_lecturers:
                event.lecturer_id = random.choice(suitable_lecturers)

# Генетичний алгоритм
def genetic_algorithm(groups, subjects, lecturers, auditoriums, generations=100):
    population_size = 50  # Стабільний розмір популяції
    population = generate_initial_population(population_size, groups, subjects, lecturers, auditoriums)
    fitness_function = Schedule.fitness  # Можна переключитися на fitness_alternative

    for generation in range(generations):
        # Оцінка популяції
        population = select_population(population, groups, lecturers, auditoriums, fitness_function)
        if not population:
            print("Популяція пуста після відбору. Завершення алгоритму.")
            break
        best_schedule = population[0]
        best_fitness = fitness_function(best_schedule, groups, lecturers, auditoriums)
        print(f"Покоління {generation+1}, Найкраща оцінка: {best_fitness}")

        # Якщо досягли оптимуму
        if best_fitness == 0:
            break

        new_population = []

        # Реалізація "хижака"
        population = predator_approach(population, groups, lecturers, auditoriums, fitness_function)

        # Реалізація "травоїдного" згладжування
        smoothed_population = herbivore_smoothing(population, best_schedule, lecturers, auditoriums)

        # Реалізація "дощу"
        rain_population = rain(len(population), groups, subjects, lecturers, auditoriums)

        # Об'єднуємо популяції
        new_population.extend(population)
        new_population.extend(smoothed_population)
        new_population.extend(rain_population)

        # Мутація
        for schedule in new_population:
            if random.random() < 0.3:
                mutate(schedule, lecturers, auditoriums)

        # Зберігаємо стабільний розмір популяції
        population = new_population[:population_size]

    return best_schedule

# Вивід розкладу
def print_schedule(schedule, lecturers):
    schedule_dict = {}
    for event in schedule.events:
        if event.timeslot not in schedule_dict:
            schedule_dict[event.timeslot] = []
        schedule_dict[event.timeslot].append(event)

    for timeslot in TIMESLOTS:
        print(f"{timeslot}:")
        if timeslot in schedule_dict:
            for event in schedule_dict[timeslot]:
                group_info = ', '.join([f"Група {gid}" + (f" (Підгрупа {event.subgroup_ids[gid]})" if event.subgroup_ids and gid in event.subgroup_ids else '') for gid in event.group_ids])
                print(f"  {group_info}, {event.subject_name} ({event.event_type}), "
                      f"Викладач: {lecturers[event.lecturer_id]['LecturerName']}, Аудиторія: {event.auditorium_id}")
        else:
            print("  Вільно")
        print()

# Основна функція
def main():
    # Завантажуємо дані
    groups = load_groups('groups.csv')
    subjects = load_subjects('subjects.csv')
    lecturers = load_lecturers('lecturers.csv')
    auditoriums = load_auditoriums('auditoriums.csv')

    # Запускаємо генетичний алгоритм
    best_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)
    print("\nНайкращий знайдений розклад:\n")
    print_schedule(best_schedule, lecturers)

if __name__ == "__main__":
    main()
