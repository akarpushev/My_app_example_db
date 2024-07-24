from datetime import datetime


class Employee:
    def __init__(self, full_name, birth_date, gender):
        """
        Инициализация объекта Employee.
        :param full_name: Полное имя сотрудника.
        :param birth_date: Дата рождения сотрудника в формате 'YYYY-MM-DD'.
        :param gender: Пол сотрудника, 'Male' для мужского, 'Female' для женского).
        """
        self.full_name = full_name
        self.birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
        self.gender = gender

    def __str__(self):
        """
        Возвращает строковое представление объекта Employee.
        :return: Строка с информацией о сотруднике в формате 'Employee(ФИО, дата рождения, пол)'.
        """
        return f"{self.full_name}, {self.birth_date.strftime('%Y-%m-%d')}, {self.gender}"

    def save_to_db(self, db):
        """
        Сохраняет текущий объект Employee в базу данных.
        :param db: Объект базы данных для сохранения сотрудника.
        """
        if db.save_employee(self):
            return True
        return False

    def calculate_age(self):
        """
        Рассчитывает возраст сотрудника на основе его даты рождения.
        :return: Возраст сотрудника в полных годах.
        """
        today = datetime.today()
        age = today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)  # возвращает True или False
        )
        return age
