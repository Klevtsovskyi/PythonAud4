"""
Скласти програму, яка працює в оточенні веб-сервера, для
конвертування валют. Поточні курси валют містяться у базі даних
на сервері. База даних містить 2 таблиці: таблиця валют та
таблиця курсів валют. Таблиця валют містить 2 поля:
<код валюти> <назва валюти>,
наприклад, UAH та Українська гривня. Таблиця курсів валют має такий вигляд:
<код валюти 1> <код валюти 2> <курс>.
Код валюти – це рядок з 3 символів, наприклад UAH, USD, EUR тощо.
Currency1 Currency2 Rate
UAH       USD       24,81
UAH       EUR       27,75
…         …         …
Програма повинна забезпечити вибір двох валют зі списків  валют на
сторінці, введення суми у першій валюті та показ суми у другій валюті.

Надати можливість додавання/зміну/видалення валюти.
"""

from wsgiref.simple_server import make_server
from string import Template
import cgi
import sqlite3
import openpyxl
import os


OPTION = """
      <option value="$cur_id">$cur_name</option>
"""


class ExchangeRateDB:

    def __init__(self, database):
        self.database = database

    def get_currencies(self):
        """ Повертає список валют з БД"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute("""SELECT * FROM "currencies";""")
        currencies = curs.fetchall()
        conn.close()
        return currencies

    def obtain_rate(self, cur1_id, cur2_id, amount):
        """ Повертає курс валюти cur1_id відносно валюти cur2_id"""
        if cur1_id == cur2_id:
            return amount

        conn = sqlite3.connect(self.database)
        curs = conn.cursor()

        query = """
        SELECT "rate" FROM "exchange_rates"
        WHERE "cur1_id"=? AND "cur2_id"=?;
        """
        result = 0
        curs.execute(query, (cur1_id, cur2_id))
        rate = curs.fetchone()
        if rate is not None:
            result = amount * rate[0]
        curs.execute(query, (cur2_id, cur1_id))
        rate = curs.fetchone()
        if rate is not None:
            result = amount / rate[0]
        conn.close()
        return result

    def get_currency_name(self, currency_id):
        """ Повертає ім`я валюти згідно її id"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute(
            """SELECT "name" FROM "currencies" WHERE "id"=?""",
            (currency_id, )
        )
        name = curs.fetchone()
        conn.close()
        return name[0]

    def currency_exists(self, currency_id, currency_name):
        """ Перевіряє чи існує валюта з заданим кодом або назвою"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        result = True
        curs.execute(
            """SELECT * FROM "currencies" WHERE "id"=? OR "name"=?""",
            (currency_id, currency_name)
        )
        if curs.fetchone() is None:
            result = False
        conn.close()
        return result

    def add_currency(self, new_cur_id, new_cur_name, reg_cur_id, rate):
        """ Додає нову валюту до БД.

        :param new_cur_id: код нової валюти
        :param new_cur_name: назва нової валюти
        :param reg_cur_id: код валюти, відносно якої надається курс
        :param rate: курс валюти
        :return:
        """
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute("""SELECT "id" FROM "currencies";""")
        currencies_id = curs.fetchall()  # Поточні валюти в БД
        # Додаємо валюту в БД
        curs.execute(
            """INSERT INTO "currencies" VALUES (?, ?);""",
            (new_cur_id, new_cur_name)
        )
        # Якщо окрім нової валюти в БД є ще валюти, встановлюємо курс
        if len(currencies_id) > 0:
            query = """INSERT INTO "exchange_rates" VALUES (?, ?, ?);"""
            curs.execute(query, (new_cur_id, reg_cur_id, rate))
            currencies_id.remove((reg_cur_id, ))
            for cur_id in currencies_id:
                reg_rate = self.obtain_rate(reg_cur_id, cur_id[0], rate)
                curs.execute(query, (new_cur_id, cur_id[0], reg_rate))

        conn.commit()
        conn.close()

    def update_currency_name(self, cur_id, new_cur_name):
        """ Надає нове ім`я new_cur_name валюті з кодом cur_id"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute(
            """UPDATE "currencies" SET "name"=? WHERE "id"=?;""",
            (new_cur_name, cur_id)
        )
        conn.commit()
        conn.close()

    def update_currency_rate(self, upd_cur_id, reg_cur_id, upd_rate):
        """ Змінює курс валюти upd_cur_id відносно валюти reg_cur_id
        на upd_rate. Змінює курси інших валют відносно upd_cur_id.
        """
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute(
            """SELECT "id" FROM "currencies" WHERE "id"<>?;""",
            (upd_cur_id, )
        )
        currencies_id = curs.fetchall()  # Всі валюти окрім поточної
        # Якщо окрім поточної валюти в БД є ще валюти, оновлюємо курс
        if len(currencies_id) > 0:
            query = """
            UPDATE "exchange_rates" SET "rate"=?
                WHERE "cur1_id"=? AND "cur2_id"=?;
            """
            # Виконається лише один з двох наступних запитів
            curs.execute(query, (upd_rate, upd_cur_id, reg_cur_id))
            curs.execute(query, (1 / upd_rate, reg_cur_id, upd_cur_id))
            currencies_id.remove((reg_cur_id, ))
            for cur_id in currencies_id:
                reg_rate = self.obtain_rate(reg_cur_id, cur_id[0], upd_rate)
                # Виконається лише один з двох наступних запитів
                curs.execute(query, (reg_rate, upd_cur_id, cur_id[0]))
                curs.execute(query, (1 / reg_rate, cur_id[0], upd_cur_id))

        conn.commit()
        conn.close()

    def delete_currency(self, currency_id):
        """ Видаляє з БД валюту з кодом currency_id"""
        conn = sqlite3.connect(self.database)
        curs = conn.cursor()
        curs.execute(
            """DELETE FROM "currencies" WHERE "id"=?;""",
            (currency_id, )
        )
        curs.execute(
            """
            DELETE FROM "exchange_rates"
                WHERE "cur1_id"=? OR "cur2_id"=?;
            """,
            (currency_id, currency_id)
        )
        conn.commit()
        conn.close()

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "").lstrip("/")
        params = {"currencies": "", "result": ""}
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        file = "templates/currencies.html"
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)

        # http://localhost:8000/
        if path == "":
            for ID, name in self.get_currencies():
                params["currencies"] += Template(OPTION).substitute(cur_id=ID, cur_name=name)

        # http://localhost:8000/exchange_rate
        elif path == "exchange_rate":
            cur1_id = form.getfirst("from", "")
            cur2_id = form.getfirst("to", "")
            amount = form.getfirst("amount", "")

            if cur1_id and cur2_id and amount:
                file = "templates/exchange_rate.html"
                rate = round(self.obtain_rate(cur1_id, cur2_id, float(amount)), 2)
                cur1_name = self.get_currency_name(cur1_id)
                cur2_name = self.get_currency_name(cur2_id)
                params["result"] = f"{amount} {cur1_name} = {rate} {cur2_name}"
            # Якщо у формі задано недостатньо параметрів,
            # перенаправляємо на головну сторінку
            else:
                status = "303 SEE OTHER"
                headers.append(("Location", "/"))

        # http://localhost:8000/add_currency
        elif path == "add_currency":
            cur_id = form.getfirst("cur_id", "")
            cur_name = form.getfirst("cur_name", "")
            reg_cur_id = form.getfirst("reg_cur_id", "")
            rate = form.getfirst("rate", "")
            # Якщо запит до стрінки надійшов з форми для додавання
            if cur_id and cur_name and rate:
                if self.currency_exists(cur_id, cur_name):
                    params["result"] = f"Валюта з кодом \"{cur_id}\" або назвою \"{cur_name}\" вже існує!"
                elif float(rate) <= 0:
                    params["result"] = "Неправильне знаачення курсу!"
                else:
                    self.add_currency(cur_id, cur_name, reg_cur_id, float(rate))
                    params["result"] = f"Валюта \"{cur_name}\" успішно додана!"
            elif cur_id or cur_name or reg_cur_id or rate:
                params["result"] = "Введено недостатньо параметрів!"

            for ID, name in self.get_currencies():
                params["currencies"] += Template(OPTION).substitute(cur_id=ID, cur_name=name)
                file = "templates/add_currency.html"

        # http://localhost:8000/update_currency
        elif path == "update_currency":
            cur_id = form.getfirst("cur_id", "")
            cur_name = form.getfirst("cur_name", "")
            reg_cur_id = form.getfirst("reg_cur_id", "")
            rate = form.getfirst("rate", "")
            # Якщо запит до стрінки надійшов з форми для зміни
            if cur_id:
                # зміна імені валюти "cur_id"
                if cur_name:
                    if self.currency_exists("", cur_name):
                        params["result"] += f"Валюта з назвою \"{cur_name}\" вже існує! "
                    else:
                        old_cur_name = self.get_currency_name(cur_id)
                        self.update_currency_name(cur_id, cur_name)
                        params["result"] += (
                            f"Назву валюту \"{old_cur_name}\" успішно змінено на \"{cur_name}\"! "
                        )
                # зміна курсу валюти "cur_id" відносно "reg_cur_id"
                if rate:
                    if cur_id == reg_cur_id or float(rate) <= 0:
                        params["result"] += "Неправильне значення курсу!"
                    else:
                        self.update_currency_rate(cur_id, reg_cur_id, float(rate))
                        cur_name = self.get_currency_name(cur_id)
                        params["result"] += f"Курс валюти \"{cur_name}\" успішно змінено!"
                if not (cur_name or rate):
                    params["result"] = "Введено недостатньо параметрів!"

            for ID, name in self.get_currencies():
                params["currencies"] += Template(OPTION).substitute(cur_id=ID, cur_name=name)
                file = "templates/update_currency.html"

        # http://localhost:8000/delete_currency
        elif path == "delete_currency":
            cur_id = form.getfirst("currency_id", "")
            # Якщо запит до стрінки надійшов з форми для видалення
            if cur_id:
                cur_name = self.get_currency_name(cur_id)
                self.delete_currency(cur_id)
                params["result"] = f"Валюта \"{cur_name}\" успішно видалена!"

            for ID, name in self.get_currencies():
                params["currencies"] += Template(OPTION).substitute(cur_id=ID, cur_name=name)
                file = "templates/delete_currency.html"

        # http://localhost:8000/<будь-який інший запит>
        else:
            status = "404 NOT FOUND"
            file = "templates/error_404.html"

        start_response(status, headers)
        with open(file, encoding="utf-8") as f:
            page = Template(f.read()).substitute(params)
        return [bytes(page, encoding="utf-8")]


def from_excel(xlsx_filename) -> dict:
    """ Зчитує дані з Excel-файлу та повертає словник з
    ключами - ім`я аркуша та значеннями - список рядків
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


def restore_db(xlsx_filename, db_filename):
    """ Створює або оновлює БД для "Обміну валют" з заданого Excel-файлу.

    :param xlsx_filename: назва Excel-файлу
    :param db_filename: назва БД
    :return:
    """
    if os.path.exists(db_filename):
        os.remove(db_filename)

    conn = sqlite3.connect(db_filename)
    curs = conn.cursor()
    # Створюємо таблицю валют та таблицю курсів
    curs.executescript(
        """
        CREATE TABLE "currencies" (
            "id" TEXT NOT NULL,
            "name" TEXT UNIQUE NOT NULL,
            PRIMARY KEY ("id")
        );
        CREATE TABLE "exchange_rates" (
            "cur1_id" TEXT NOT NULL,
            "cur2_id" TEXT NOT NULL,
            "rate" REAL NOT NULL,
            CHECK ("cur1_id"<>"cur2_id"),
            CHECK ("rate">0),
            PRIMARY KEY ("cur1_id", "cur2_id"),
            FOREIGN KEY ("cur1_id") REFERENCES "currencies" ("id"),
            FOREIGN KEY ("cur2_id") REFERENCES "currencies" ("id")
        );
        """
    )
    # Записуємо дані з робочої книги Excel до БД
    sheets = from_excel(xlsx_filename)
    curs.executemany(
        """INSERT INTO "currencies" VALUES (?, ?)""",
        sheets["currencies"][1:]
    )
    curs.executemany(
        """INSERT INTO "exchange_rates" VALUES (?, ?, ?)""",
        sheets["rate"][1:]
    )
    conn.commit()
    conn.close()


HOST = ""
PORT = 8000

if __name__ == "__main__":
    xlsx = "data/currencies.xlsx"
    db = "data/currencies.db"
    restore_db(xlsx, db)
    app = ExchangeRateDB(db)
    print(f"Локальний сервер запущено на http://localhost:{PORT}")
    make_server(HOST, PORT, app).serve_forever()
