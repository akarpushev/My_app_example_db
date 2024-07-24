import sys
from database import Database
from employee import Employee
from faker import Faker
from transliterate import translit
import random


class Processor:
    def __init__(self, db):
        """
        Инициализация объекта Processor.
        :param db: Объект базы данных для взаимодействия с таблицей сотрудников.
        """
        self.db = db  # Сохранение объект базы данных в атрибуте self.db

    def process(self):
        """
        Обрабатывает команду, переданную в аргументах командной строки, и выполняет соответствующее действие.
        Метод process сначала проверяет, есть ли аргументы командной строки.
        Если нет, он вызывает метод show_help для отображения справки.
        """
        if len(sys.argv) < 2:
            self.show_help()
            return

        mode = sys.argv[1]

        if mode == "1":
            self.create_table()
        elif mode == "2":
            self.add_employee()
        elif mode == "3":
            self.list_employees()
        elif mode == "4":
            self.populate_employees()
        elif mode == "5":
            self.filter_employees()
        elif mode == "6":
            self.optimize_database()
        else:
            print(f"Неизвестный режим: {mode}")
            self.show_help()

    def create_table(self):
        """
        Создает таблицу 'employees' в базе данных, если она еще не существует.
        """
        self.db.create_table()
        print("Таблица 'employees' создана.")

    def add_employee(self):
        """
        Добавляет нового сотрудника в базу данных на основе аргументов командной строки.
        """
        if len(sys.argv) != 5:
            print("Командная строка должна быть следующего вида: python app.py 2 \"ФИО\" <Дата рождения> <Пол>")
            # Проверка правильности аргументов и вывод сообщения о неправильной командной строке
        else:
            full_name = sys.argv[2]  # ФИО сотрудника из аргументов командной строки
            birth_date = sys.argv[3]  # Дата рождения сотрудника из аргументов командной строки
            gender = sys.argv[4]  # Пол сотрудника из аргументов командной строки
            employee = Employee(full_name, birth_date, gender)  # Создание объекта сотрудника
            if employee.save_to_db(self.db):
                age = employee.calculate_age()  # Расчет возраста сотрудника
                print(f"{full_name} добавлен в базу данных. Возраст: {age} лет.")
            else:
                print(f"Сотрудник {full_name} уже существует в базе данных.")

    def list_employees(self):
        """
        Выводит список всех уникальных сотрудников из базы данных.
        """
        employees = self.db.get_all_employees()  # Извлечение всех сотрудников из базы данных
        for employee in employees:
            age = employee.calculate_age()  # Расчет возраста сотрудника
            print(f"{employee.full_name:<50} {employee.birth_date.strftime('%Y-%m-%d'):<15} {employee.gender}"
                  f" кол-во полных лет: {age}")

    def populate_employees(self):
        """
        Автоматически заполняет базу данных 100,000 сотрудников и 100 сотрудников с фамилией на 'F'.
        """
        faker = Faker('ru_RU')
        employees = []

        def transliterate_name(name):
            """
            Транслитерация фамилии на латиницу
            """
            return translit(name, language_code='ru', reversed=True)

        def generate_last_name_with_F():
            """
            Отбор фамилий, начинающихся с буквы 'Ф'
            """
            while True:
                last_name_ = faker.last_name()
                if last_name_.startswith('Ф'):
                    return transliterate_name(last_name_)

        # Создание 1,000,000 сотрудников
        for _ in range(1000000):
            full_name_ru = faker.name()  # Создание русских имен
            full_name_lat = transliterate_name(full_name_ru)  # Транслитерация на латиницу
            birth_date = faker.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
            gender = random.choice(['Male', 'Female'])
            employees.append(Employee(full_name_lat, birth_date, gender))

        # Создание 100 сотрудников с полом «Male» и фамилией, начинающейся с буквы 'F'
        for _ in range(100):
            last_name = generate_last_name_with_F()
            first_name = faker.first_name()
            patronymic = faker.middle_name()
            full_name_ru = f"{last_name} {first_name} {patronymic}"  # Русские фамилия, имя и отчество
            full_name_lat = transliterate_name(full_name_ru)  # Транслитерация на латиницу
            birth_date = faker.date_of_birth(minimum_age=18, maximum_age=65).strftime('%Y-%m-%d')
            gender = 'Male'
            employees.append(Employee(full_name_lat, birth_date, gender))

        self.db.save_employees_batch(employees)  # Пакетное сохранение всех сотрудников в базу данных
        print("1,000,000 сотрудников и 100 сотрудников с фамилией на букву 'F' добавлены в базу данных.")

    def filter_employees(self):
        """
        Извлекает и выводит сотрудников мужского пола с фамилией, начинающейся на 'F' и время выполнения запроса.
        """
        employees, elapsed_time = self.db.get_male_employees_with_f_lastname()
        print(f"Сотрудники мужского пола с фамилией, начинающейся на букву 'F':")
        for employee in employees:
            age = employee.calculate_age()  # Расчет возраста сотрудника
            print(f"{employee.full_name:<50} {employee.birth_date.strftime('%Y-%m-%d'):<15} {employee.gender}"
                  f" кол-во полных лет: {age}")  # Вывод информации о каждом сотруднике
        print(f"Время выполнения запроса: {elapsed_time:.3f} секунд")  # Вывод времени выполнения запроса

    def optimize_database(self):
        """
        Оптимизация базы данных путем создания индексов.
        """
        self.db.create_index()
        print("Индексы созданы для оптимизации базы данных.")

    def show_help(self):
        """
        Выводит справку по использованию приложения.
        """
        print("Доступны следующие режимы:")
        print("  1                               Создание таблицы сотрудников")
        print("  2 \"ФИО\" <Дата рождения> <Пол>   Добавление нового сотрудника")
        print("  3                               Вывод всех сотрудников")
        print("  4                               Автозаполнение 100 сотрудников и 100 сотрудников с фамилией на 'F'")
        print("  5                               Выборка сотрудников мужского пола с фамилией на 'F' и замер времени")
        print("  6                               Оптимизация базы данных")


def main():
    """
    Основная функция, которая запускает приложение.
    1. Создает объект базы данных с заданными параметрами подключения.
    2. Создает объект CommandProcessor, передавая ему объект базы данных.
    3. Запускает процесс обработки команд с помощью CommandProcessor.
    4. Закрывает соединение с базой данных.
    """
    # Конфигурация подключения к базе данных
    db = Database(
        dbname="example_db",  # Имя базы данных
        user="postgres",  # Имя пользователя базы данных
        password="password_example"  # Пароль пользователя базы данных
    )

    # Создание объекта Processor, который будет использовать объект базы данных
    processor = Processor(db)
    # Запуск обработки команд, переданных в аргументах командной строки
    processor.process()

    db.close()


if __name__ == "__main__":
    main()
