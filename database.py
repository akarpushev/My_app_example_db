import psycopg2
from psycopg2 import sql
from employee import Employee
import time


class Database:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """
        Инициализация объекта Database и подключение к базе данных PostgreSQL.
        :param dbname: Имя базы данных.
        :param user: Имя пользователя для подключения.
        :param password: Пароль пользователя.
        :param host: Хост сервера базы данных (по умолчанию 'localhost').
        :param port: Порт сервера базы данных (по умолчанию '5432').
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.conn.cursor()

    def create_table(self):
        """
        Создание таблицы employees, если она еще не существует.
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100),
            birth_date DATE,
            gender CHAR(6)
        )
        ''')
        self.conn.commit()

    def save_employee(self, employee):
        """
        Сохранение одного объекта Employee в таблицу employees.
        :param employee: Объект Employee для сохранения.
        """
        if not self.employee_exists(employee.full_name, employee.birth_date):
            self.cursor.execute(
                sql.SQL("INSERT INTO employees (full_name, birth_date, gender) VALUES (%s, %s, %s)"),
                [employee.full_name, employee.birth_date, employee.gender]
            )
            self.conn.commit()
            return True
        return False

    def employee_exists(self, full_name, birth_date):
        """
        Проверяет, существует ли сотрудник с указанным ФИО и датой рождения в базе данных.
        :param full_name: ФИО сотрудника для проверки.
        :param birth_date: Дата рождения сотрудника для проверки.
        :return: True, если сотрудник существует в базе данных, иначе False.
        """
        self.cursor.execute(
            sql.SQL("SELECT 1 FROM employees WHERE full_name = %s AND birth_date = %s"),
            [full_name, birth_date]
        )
        # Если запись найдена, возвращаем True, иначе False
        return self.cursor.fetchone() is not None

    def save_employees_batch(self, employees):
        """
        Пакетное сохранение списка объектов Employee в таблицу employees.
        :param employees: Список объектов Employee для сохранения.
        """
        data = [(emp.full_name, emp.birth_date, emp.gender) for emp in employees if
                not self.employee_exists(emp.full_name, emp.birth_date)]
        if data:
            self.cursor.executemany(
                sql.SQL("INSERT INTO employees (full_name, birth_date, gender) VALUES (%s, %s, %s)"), data)
            self.conn.commit()

    def get_all_employees(self):
        """
        Извлечение всех уникальных сотрудников из таблицы employees, отсортированных по ФИО и дате рождения.
        :return: Список объектов Employee.
        """
        self.cursor.execute('''
        SELECT DISTINCT ON (full_name, birth_date) full_name, birth_date, gender
        FROM employees
        ORDER BY full_name, birth_date
        ''')
        rows = self.cursor.fetchall()
        employees = [Employee(row[0], row[1].strftime('%Y-%m-%d'), row[2]) for row in rows]
        return employees

    def get_male_employees_with_f_lastname(self):
        """
        Извлечение всех сотрудников мужского пола с фамилией, начинающейся на букву 'F'.
        :return: Список объектов Employee.
        """
        start_time = time.time()
        self.cursor.execute('''
        SELECT full_name, birth_date, gender
        FROM employees
        WHERE gender = 'Male' AND full_name LIKE 'F%'
        ''')
        rows = self.cursor.fetchall()
        employees = [Employee(row[0], row[1].strftime('%Y-%m-%d'), row[2]) for row in rows]
        end_time = time.time()
        elapsed_time = end_time - start_time
        return employees, elapsed_time

    def create_index(self):
        """
        Создание индекса для ускорения запросов.
        """
        self.cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_gender_fullname ON employees (gender, full_name);
        ''')
        self.conn.commit()

    def close(self):
        """
        Закрытие курсора и соединения с базой данных.
        """
        self.cursor.close()
        self.conn.close()
