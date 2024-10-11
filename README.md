

1. **Список груп G з N студентів, кількість не змінюється, поділ на підгрупи заданий наперед:**

   - **Реалізація:** У коді використовується функція `load_groups`, яка завантажує інформацію про групи з файлу `groups.csv`. Для кожної групи зберігається кількість студентів (`NumStudents`) та список підгруп (`Subgroups`). Кількість студентів та підгрупи є стабільними протягом усього процесу розкладання.

2. **Програма для кожної групи: перелік предметів Pi з визначеною кількістю годин T на семестр, вказано час для лекцій та практичних/лабораторних, деякі предмети можуть вимагати поділ на групи:**

   - **Реалізація:** Функція `load_subjects` завантажує предмети з файлу `subjects.csv`. Для кожного предмету вказано кількість лекцій та практичних занять (`NumLectures`, `NumPracticals`), а також чи вимагає предмет поділу на підгрупи (`RequiresSubgroups`).

3. **Список L лекторів з обмеженнями: які предмети та типи занять можуть проводити:**

   - **Реалізація:** Використовується функція `load_lecturers`, яка зчитує дані з `lecturers.csv`. У файлі вказано, які предмети та типи занять може вести кожен викладач (`SubjectsCanTeach`, `TypesCanTeach`).

4. **Список A аудиторій з місткістю m студентів (кількість аудиторій трохи більша за кількість груп):**

   - **Реалізація:** Функція `load_auditoriums` завантажує дані про аудиторії з файлу `auditoriums.csv`, де для кожної аудиторії зазначена її місткість (`Capacity`).

5. **Максимум на тиждень 4х5 = 20 пар, 1 пара = 1.5 години, семестр ~14 тижнів:**

   - **Реалізація:** У коді встановлено константи `DAYS_PER_WEEK = 5` та `SLOTS_PER_DAY = 4`, що відповідає 20 парам на тиждень. Кожна пара вважається як 1.5 години. Семестр розглядається з урахуванням парних та непарних тижнів.

6. **Списки генеруються випадково на розсуд розробника, щоб можна було змінювати кількість:**

   - **Реалізація:** Дані зберігаються у CSV-файлах, які можна легко змінювати без потреби редагувати код. Це дозволяє гнучко змінювати кількість груп, предметів, викладачів та аудиторій.

7. **Більш-менш читабельний вивід розкладу:**

   - **Реалізація:** Функція `print_schedule` форматує та виводить розклад у зручному для читання форматі, включаючи інформацію про день, пару, групи, підгрупи, предмети, типи занять, викладачів та аудиторії.

8. **Дані зберігаються у людино-орієнтованих форматах (наприклад, CSV), щоб можна було легко змінювати дані ззовні:**

   - **Реалізація:** Всі вхідні дані (`groups.csv`, `subjects.csv`, `lecturers.csv`, `auditoriums.csv`) зберігаються у форматі CSV, що полегшує їх редагування та оновлення.

9. **Розклад як у КНУ (не американський чи шкільний):**

   - **Реалізація:** Розклад організовано за днями та парами, що відповідає типовому розкладу університету, з урахуванням парних та непарних тижнів.

10. **Жорсткі обмеження:**

    - **Один лектор повинен одночасно проводити заняття тільки в одній аудиторії:**
      - **Реалізація:** У функції `fitness` перевіряється, що викладач не має більше одного заняття в один часовий слот.

    - **Одна група може мати лише одне заняття в один період часу:**
      - **Реалізація:** Перевіряється, що кожна група або підгрупа не має більше одного заняття в один часовий слот.

    - **Одна аудиторія може використовуватися одночасно лише під одне заняття (але для лекцій дозволено декілька груп з одним лектором):**
      - **Реалізація:** Для лекцій дозволяється об'єднання груп в одній аудиторії з одним викладачем. В інших випадках аудиторія використовується лише для одного заняття.

11. **Нежорсткі вимоги:**

    - **Щоб було якомога менше “вікон” в індивідуальних розкладах викладачів та студентів:**
      - **Реалізація:** У функції `fitness_alternative` враховується кількість вікон у розкладах та додається штраф за кожне вікно.

    - **Заняття не може проводитися, якщо група більша за кількість місць в аудиторії:**
      - **Реалізація:** Перевіряється місткість аудиторії відносно розміру групи або підгрупи. Якщо місткість недостатня, додається штраф.

    - **Обмеження по викладачам: список предметів та типів занять, що викладач може вести:**
      - **Реалізація:** Перевіряється відповідність предмету та типу заняття можливостям викладача.

12. **Підгрупи стабільні. Наприклад, "ТТП 1п/г" не міняє склад протягом навчання:**

    - **Реалізація:** Підгрупи визначені у файлі `groups.csv` та залишаються незмінними протягом всього процесу складання розкладу.

13. **Базовий алгоритм лише забезпечує стабільність розміру популяції:**

    - **Реалізація:** У генетичному алгоритмі підтримується стабільний розмір популяції шляхом відбору та обмеження кількості особин.

14. **Парні/непарні тижні:**

    - **Реалізація:** У коді додано підтримку парних та непарних тижнів. Часові слоти генеруються з урахуванням типу тижня, а предмети можуть бути призначені на конкретний тип тижня.

15. **Обмеження по викладачам: список предметів та типів занять, що викладач може вести, та кількість годин на тиждень:**

    - **Реалізація:** У файлі `lecturers.csv` додано поле `MaxHoursPerWeek`. У функції `fitness` контролюється загальна кількість годин викладача на тиждень.

16. **Реалізація "травоїдного" згладжування навколо оптимуму:**

    - **Реалізація:** Функція `herbivore_smoothing` генерує нові розклади на основі найкращого, вносячи незначні зміни для дослідження локального простору рішень.

17. **Реалізація "хижого" підходу:**

    - **Реалізація:** Функція `predator_approach` видаляє найгірші розклади з популяції, зберігаючи лише найкращі для подальшої еволюції.

18. **Реалізація "дощу":**

    - **Реалізація:** Функція `rain` додає до популяції нові випадкові розклади, підвищуючи генетичну різноманітність.

19. **Різні функціонали якості (принаймні 2):**

    - **Реалізація:** У класі `Schedule` реалізовано дві функції оцінки: `fitness` та `fitness_alternative`. Перша функція фокусується на жорстких та м'яких обмеженнях, друга додатково враховує кількість вікон у розкладі.

20. **Нетривіальна мутація:**

    - **Реалізація:** Функція `mutate` реалізує складну мутацію з регульованою інтенсивністю. Під час мутації випадковим чином змінюються різні параметри подій (часовий слот, аудиторія, викладач), що дозволяє ефективніше досліджувати простір можливих розкладів.

