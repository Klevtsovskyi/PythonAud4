

from main import *
import unittest
import sqlite3
import os
import re
import random
from test.test_wsgiref import run_amock
""" run_amock(app, data)
Функція, яка створює фіктивний веб-сервер WSGI для обробки одного запиту.
Приймає запит клієнта (байти): метод + можливі заголовки + можливі дані
Повертає відповідь (байти): статус + заголовки + сторінка, помилки (ящко є)

:param app: функція обробки запитів
:param data: дані запиту клієнта
"""


class TestExchangeRateDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mock_data = {
            "currencies": [
                ("id", "name"),
                ("FLN", "Флорен"),
                ("KRN", "Крона"),
                ("ORN", "Орен")
            ],
            "rate": [
                ("cur1", "cur2", "rate"),
                ("ORN", "FLN", 11),
                ("KRN", "FLN", 1.69),
                ("ORN", "KRN", 6.5)
            ]
        }
        cls.exchange_rate = ExchangeRateDB("_test.db")

    def setUp(self) -> None:
        restore_db(self.mock_data, "_test.db")

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("_test.db")

    def test_01_get_currencies(self):
        expected_result = [
            ("FLN", "Флорен"),
            ("KRN", "Крона"),
            ("ORN", "Орен")
        ]
        result = self.exchange_rate.get_currencies()
        self.assertIsInstance(result, list)
        self.assertCountEqual(expected_result, result)
        self.assertListEqual(expected_result, result)

    def test_02_obtain_rate(self):
        expected_result = 100
        result = self.exchange_rate.obtain_rate("FLN", "FLN", 100)
        self.assertAlmostEqual(expected_result, result)
        expected_result = 99
        result = self.exchange_rate.obtain_rate("ORN", "FLN", 9)
        self.assertAlmostEqual(expected_result, result)
        expected_result = 10
        result = self.exchange_rate.obtain_rate("FLN", "ORN", 110)
        self.assertAlmostEqual(expected_result, result)
        expected_result = 169
        result = self.exchange_rate.obtain_rate("KRN", "FLN", 100)
        self.assertAlmostEqual(expected_result, result)
        expected_result = 100
        result = self.exchange_rate.obtain_rate("FLN", "KRN", 169)
        self.assertAlmostEqual(expected_result, result)

    def test_03_get_currency_name(self):
        self.assertEqual(
            "Флорен", self.exchange_rate.get_currency_name("FLN")
        )
        self.assertEqual(
            "Крона", self.exchange_rate.get_currency_name("KRN")
        )

    def test_04_currency_exists(self):
        self.assertTrue(self.exchange_rate.currency_exists("KRN", ""))
        self.assertTrue(self.exchange_rate.currency_exists("", "Крона"))
        self.assertTrue(self.exchange_rate.currency_exists("KRN", "Крона"))
        self.assertFalse(self.exchange_rate.currency_exists("GRN", ""))
        self.assertFalse(self.exchange_rate.currency_exists("", "Гривня"))

    def test_05_add_currency(self):
        self.exchange_rate.add_currency("GRN", "Гривня", "FLN", 60)
        self.assertTrue(self.exchange_rate.currency_exists("GRN", "Гривня"))
        self.assertEqual(
            [
                ("FLN", "Флорен"),
                ("KRN", "Крона"),
                ("ORN", "Орен"),
                ("GRN", "Гривня")
            ],
            self.exchange_rate.get_currencies()
        )
        self.assertAlmostEqual(
            120, self.exchange_rate.obtain_rate("GRN", "FLN", 2)
        )
        self.assertAlmostEqual(
            2, self.exchange_rate.obtain_rate("FLN", "GRN", 120)
        )
        self.assertAlmostEqual(
            5.4545454545, self.exchange_rate.obtain_rate("GRN", "ORN", 1)
        )
        self.assertAlmostEqual(
            5.63333333, self.exchange_rate.obtain_rate("KRN", "GRN", 200)
        )

    def test_06_update_currency_name(self):
        self.assertFalse(self.exchange_rate.currency_exists("", "Дукат"))
        self.exchange_rate.update_currency_name("ORN", "Дукат")
        self.assertTrue(self.exchange_rate.currency_exists("", "Дукат"))
        self.assertFalse(self.exchange_rate.currency_exists("", "Орен"))
        with self.assertRaises(sqlite3.Error):
            self.exchange_rate.update_currency_name("KRN", "Флорен")

    def test_07_update_currency_rate(self):
        self.exchange_rate.update_currency_rate("ORN", "FLN", 12)
        self.assertAlmostEqual(
            120, self.exchange_rate.obtain_rate("ORN", "FLN", 10)
        )
        self.assertAlmostEqual(
            10, self.exchange_rate.obtain_rate("FLN", "ORN", 120)
        )
        self.assertAlmostEqual(
            7.1005917, self.exchange_rate.obtain_rate("ORN", "KRN", 1)
        )
        self.assertAlmostEqual(
            1, self.exchange_rate.obtain_rate("KRN", "ORN", 7.1005917)
        )

    def test_08_delete_currency(self):
        self.exchange_rate.delete_currency("GRN")
        self.assertEqual(3, len(self.exchange_rate.get_currencies()))
        self.exchange_rate.delete_currency("KRN")
        self.assertEqual(2, len(self.exchange_rate.get_currencies()))
        self.assertFalse(self.exchange_rate.currency_exists("KRN", ""))
        self.assertEqual(
            0, self.exchange_rate.obtain_rate("KRN", "ORN", 1)
        )
        self.exchange_rate.add_currency("GRN", "Гривня", "FLN", 60)
        self.exchange_rate.delete_currency("GRN")
        self.assertFalse(self.exchange_rate.currency_exists("GRN", ""))
        self.exchange_rate.delete_currency("ORN")
        self.exchange_rate.delete_currency("FLN")
        self.assertListEqual([], self.exchange_rate.get_currencies())


def get_status(response):
    """ Повертає http статус відповіді: код і короткий опис"""
    return re.search(r"(?P<STATUS>\d{3} .+?)\n", response).group("STATUS").rstrip()


class TestExchangeRateResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.mock_data = {
            "currencies": [
                ("id", "name"),
                ("FLN", "Флорен"),
                ("KRN", "Крона"),
                ("ORN", "Орен")
            ],
            "rate": [
                ("cur1", "cur2", "rate"),
                ("ORN", "FLN", 11),
                ("KRN", "FLN", 1.69),
                ("ORN", "KRN", 6.5)
            ]
        }
        cls.exchange_rate = ExchangeRateDB("_test.db")
        restore_db(cls.mock_data, "_test.db")

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("_test.db")

    def test_01_correct_path_status(self):
        """ Коректність статусу відповіді при правильному шляху.
        Намагаємося відкрити головну сторінку "/" .
        Очікуємо, що статус відповіді буде "200 OK".
        """
        #       метод  шлях  версія протоколу
        #           |   |    |
        #           v   v    v
        request = b"GET / HTTP/1.0\n"  # Запит на відкриття головної сторінки
        # Намагаємося отримати відповідь
        out, err = run_amock(self.exchange_rate, request)
        response = str(out, encoding="utf-8")  # Розкодовуємо відповідь
        # print(response)  # <-- Так виглядає відповідь
        status = get_status(response)  # Шукаємо статус у відповіді
        # Перевіряємо чи справді статус відповіді є коректним
        self.assertEqual("200 OK", status)

    def test_02_incorrect_path_status(self):
        """ Коректність статусу відповіді при неправильному шляху.
        Намагаємося відкрити сторінку "/incorrect/path".
        Очікуємо, що статус відповіді буде "404 NOT FOUND".
        """
        request = b"GET /incorrect/path HTTP/1.0\n"
        out, err = run_amock(self.exchange_rate, request)
        response = str(out, encoding="utf-8")
        status = get_status(response)
        self.assertEqual("404 NOT FOUND", status)

    def test_03_correct_path_without_data(self):
        """ Коректність відповіді, якщо надіслати форму з неповними даними.
        Намагаємося відкрити сторінку "/currencies" за допомогою метода POST.
        Очікуємо, що відбудеться перенаправдлення,
        при цьому статус відповіді повинен бути "303 SEE OTHER",
        а до заголовків додано направлення "Location: /"
        """
        request = (
            b"POST /exchange_rate HTTP/1.0\n"
            # Наступний рядок потрібен для методу POST:
            # Тип даних, які насилаються
            b"Content-Type: application/x-www-form-urlencoded\n\n"
            # Дані, які надсилаються
            b"amount=&from=&to="
        )
        out, err = run_amock(self.exchange_rate, request)
        response = str(out, encoding="utf-8")
        self.assertEqual("303 SEE OTHER", get_status(response))
        # Шукаємо в заголовок з ім'ям "Location" і отримуємо його вміст
        match = re.search("Location: (?P<LOCATION>.+?)\n", response)
        self.assertFalse(match is None)
        location = match.group("LOCATION").rstrip()
        # Перевіряємо чи здійснюється перенаправлення на головну сторінку
        self.assertEqual(location, "/")

    def test_04_correct_currencies_in_page(self):
        """ Коректність відораження валют на головній сторінці.
        Намагаємося відкрити головну сторінку "/" .
        Очікуємо, що статус відповіді буде "200 OK".
        Очікуємо, що кількість валют на сторінці дорівнює кількості валют в базі.
        Очікуємо, що коди валют співпадають з кодами валют в базі.
        Очікуємо, що назви валют співпадають з назвами валют в базі.
        """
        request = b"GET / HTTP/1.0\n"
        out, err = run_amock(self.exchange_rate, request)
        response = str(out, encoding="utf-8")
        # Перевіряємо чи відкрилась сторінка
        self.assertEqual("200 OK", get_status(response))
        # Отримуємо з фіктивної бази список кодів і назв валют
        expected_currencies = self.exchange_rate.get_currencies()
        # Множимо на 2, бо на сторінці вони дублюються
        expected_currencies_codes = [cur for cur, name in expected_currencies] * 2
        expected_currencies_names = [name for cur, name in expected_currencies] * 2
        # Шукаємо на сторінці коди і назви валют
        match_iter = re.finditer(
            r"<option value=\"(?P<code>.+?)\">(?P<name>.+?)</option>",
            response
        )
        currencies_codes = []
        currencies_names = []
        for match in match_iter:
            currencies_codes.append(match.group("code"))
            currencies_names.append(match.group("name"))
        # Перевіряємо чи дорівнює кількість валют на сторінці кількості валют в базі
        self.assertCountEqual(expected_currencies_codes, currencies_codes)
        # Порівнюємо коди і назви валют на сторінці з відповідними в базі
        self.assertListEqual(expected_currencies_codes, currencies_codes)
        self.assertListEqual(expected_currencies_names, currencies_names)

    def test_05_correct_exchange_rate_in_page(self):
        """ Коректність відображення курсу валют на сторінці валют.
        Робимо тест 3 рази.
        Вибираємо кількість одинись валюти.
        Вибираємо дві довільні валюти з фіктивної бази.
        Намагаємося відкрити сторінку валют "/currencies" за допомоою методу POST
        з даними про кількість і валюти.
        Очікуємо, що статус відповіді буде "200 OK".
        Очікуємо, що на сторінці буде присутній результат.
        Очікуємо, що значення отриманого курсу буде коректним.
        """
        # Беремо з бази список валют
        currencies = [
            cur for cur, name in self.exchange_rate.get_currencies()
        ]
        for _ in range(3):
            # Вибираємо значення і дві довільні валюти
            amount = random.randint(1, 100)
            cur1 = random.choice(currencies)
            cur2 = random.choice(currencies)
            # Створюємо рядок байті запиту для метода POST
            form_args = bytes(
                "amount={}&from={}&to={}".format(amount, cur1, cur2),
                encoding="utf-8"
            )
            request = (
                b"POST /exchange_rate HTTP/1.0\n"
                b"Content-Type: application/x-www-form-urlencoded\n\n" +
                form_args
            )
            out, err = run_amock(self.exchange_rate, request)
            response = str(out, encoding="utf-8")
            # Перевіряємо чи відкрилась сторінка
            self.assertEqual("200 OK", get_status(response))
            # Намагаємося знайти на сторінці результат
            match = re.search(r"<p>.+? = (?P<RESULT>\d+\.?\d*) .+?</p>", response)
            self.assertFalse(match is None)  # Перевіряємо чи знайшли результат
            rate = float(match.group("RESULT"))
            # Знаходимо коректний курс валют
            expected_rate = round(self.exchange_rate.obtain_rate(cur1, cur2, amount), 2)
            # Перевіряємо  рівність курсу валюти на сторінці з коректним курсом
            self.assertAlmostEqual(expected_rate, rate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
