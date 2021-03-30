"""
У файлі MS Excel на 2 робочих аркушах записано дані про
робітників підприємства. На першому аркуші – дані про робітників:
    Табельний номер
    Прізвище
    Ім’я
    По батькові
    Паспорт
    Заробітна платня
    Код підрозділу

На другому аркуші – дані про підрозділи:
    Код підрозділу
    Назва підрозділу

Описати програму яка створює базу даних з 2 таблиць для
робітників та підрозділів та додає усі дані з MS Excel до цієї бази.
"""

import sqlite3
import openpyxl
import os


def from_excel(xlsx_filename) -> dict:
    """ Зчитує дані з Excel-файлу та повертає словник з
    ключами - ім'я аркуша та значеннями - список рядків
    (список клітинок) аркуша.

    :param xlsx_filename: назва Excel-файлу
    :return: словник робочих аркушів Excel
    """
    wb = openpyxl.load_workbook(xlsx_filename)
    sheets = {}
    for ws in wb:
        sheets[ws.title] = [
            [cell.value for cell in row]
            for row in ws.rows
        ]
    return sheets


def to_database(db_filename, sheets):
    """
    Зберігає дані підприємства з робочих аркуші у БД.

    :param db_filename: назва БД
    :param sheets: словник робочих аркушів Excel-файлу
    :return:
    """
    if os.path.exists(db_filename):
        os.remove(db_filename)

    # Створюємо зв'язок з базою даних
    conn = sqlite3.connect(db_filename)
    curs = conn.cursor()

    # Створюємо таблицю departments
    curs.execute(
        """
        CREATE TABLE departments (
            department_id INTEGER NOT NULL,
            title TEXT UNIQUE,
            PRIMARY KEY (department_id AUTOINCREMENT)
        );
        """
    )

    for row in sheets["departments"][1:]:
        # додати рядок row в таблицю departments
        curs.execute(
            """
            INSERT INTO departments
            VALUES (?, ?);
            """,
            row
        )

    # Створюємо таблицю staff
    curs.execute(
        """
        CREATE TABLE staff (
            id INTEGER NOT NULL,
            personnel_number TEXT UNIQUE,
            last_name TEXT,
            first_name TEXT,
            second_name TEXT,
            passport TEXT,
            salary REAL,
            department_id INTEGER,
            PRIMARY KEY (id AUTOINCREMENT),
            FOREIGN KEY (department_id)
                REFERENCES departments (department_id)
        );
        """
    )

    for row in sheets["staff"][1:]:
        # додати рядок row в таблицю staff
        curs.execute(
            """
            INSERT INTO staff (
                personnel_number,
                last_name,
                first_name,
                second_name,
                passport,
                salary,
                department_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            row
        )

    conn.commit()  # Фіксуємо транзакцію
    conn.close()   # Закриваємо зв'язок з БД


def print_data(db_filename):
    """
    Виводись всі дані з БД підприємства.

    :param db_filename: назва БД
    :return:
    """
    conn = sqlite3.connect(db_filename)
    curs = conn.cursor()

    curs.execute(
        """
        SELECT * FROM "staff";
        """
    )
    table = curs.fetchall()
    print("staff:")
    for row in table:
        print(*row)

    curs.execute(
        """
        SELECT * FROM "departments";
        """
    )
    table = curs.fetchall()
    print("departments:")
    for row in table:
        print(*row)

    conn.close()


if __name__ == "__main__":
    xlsx = "enterprise.xlsx"
    db = "enterprise.db"
    sheets = from_excel(xlsx)
    to_database(db, sheets)
    print_data(db)


# Отримати табельні номери всіх працівників,
# в яких заробітня платня в межах від 20000.00 до 30000.00
"""
SELECT personnel_number FROM staff
WHERE salary>20000.00 AND salary<30000.00;
"""

# Отримати ПІБ всіх працівників, які працюють у Архіві
"""
SELECT last_name, first_name, second_name FROM staff
WHERE department_id=(
    SELECT department_id FROM departments
    WHERE title='Архів'
);
"""

# Отримати кількість працівників,
# які працюють у Бухгалтерії або на Виробництві
"""
SELECT COUNT(*) FROM staff
WHERE department_id IN (
    SELECT department_id FROM departments
    WHERE title='Бухгалтерія' OR title='Виробництво'
);
"""
