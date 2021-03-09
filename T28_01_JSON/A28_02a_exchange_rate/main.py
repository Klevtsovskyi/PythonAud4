"""
Скласти програму, яка працює в оточенні веб-сервера, для конвертування
валют. Поточні курси валют містяться у файлі у форматі
a) JSON
на сервері у форматі: <код валюти 1> <код валюти 2> <курс>.
Код валюти – це рядок з 3 символів, наприклад UAH, USD, EUR тощо.
Currency1 Currency2 Rate
USD       UAH       24,81
EUR       UAH       27,75
…	  …	    …
Програма повинна забезпечити вибір двох валют зі списків кодів валют на
сторінці, введення суми у першій валюті та показ суми у другій валюті.
Результат показувати у форматі JSON.
"""

import cgi
import json
from string import Template

OPTION = """
      <option value="$cur">$cur</option>
"""


class ExchangeRateJSON:

    def __init__(self, currencies, exchange_rates):
        self.currencies = currencies
        self.exchange_rates = exchange_rates

    def get_currencies(self):
        """ Повертає список валют з файлу JSON"""
        with open(self.currencies) as f:
            lst = json.load(f)
        return [dct["currency"] for dct in lst]

    def get_exchange_rates(self):
        """ Повертає список курсу валют з файлу JSON"""
        with open(self.exchange_rates) as f:
            lst = json.load(f)
        return [(dct["currency1"],
                 dct["currency2"],
                 dct["rate"]) for dct in lst]

    def obtain_rate(self, cur1, cur2, amount):
        """ Повертає курс валюти cur1 відносно валюти cur2"""
        if cur1 == cur2:
            return amount
        for c1, c2, rate in self.get_exchange_rates():
            if c1 == cur1 and c2 == cur2:
                return amount / rate
            elif c1 == cur2 and c2 == cur1:
                return amount * rate

    def create_json_response(self, cur1, cur2, amount, filename):
        """ Створює JSON-файл з відповіддю для конвертування amount
        грошей у валюті cur1 до валюти cur2

        :param cur1: валюта, з якої конвертуємо
        :param cur2: валюта, в яку конвертуємо
        :param amount: кількість грошей для конвертування
        :param filename: ім'я JSON-файлу
        :return:
        """
        # Обчислюємо курс
        rate = round(self.obtain_rate(cur1, cur2, amount), 2)
        # Створюємо список - вигляд результату у форматі json
        lst = [
            {"currency": cur1, "amount": amount},
            {"currency": cur2, "amount": rate}
        ]
        # Записуємо результат у файл (тут можна було би використати
        # функцію dumps для повернення результату у вигляді рядка)
        with open(filename, "w") as f:
            json.dump(lst, f, indent=4)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "").lstrip("/")
        params = {"currencies": ""}
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        file = "templates/currencies.html"

        # http://127.0.0.1:8000/
        if path == "":
            currencies = ""
            for cur in self.get_currencies():
                currencies += Template(OPTION).substitute(cur=cur)
            params["currencies"] = currencies

        # http://127.0.0.1:8000/exchange_rate.json
        elif path == "exchange_rate.json":
            form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
            cur1 = form.getfirst("from", "")
            cur2 = form.getfirst("to", "")
            amount = form.getfirst("amount", "")
            if cur1 and cur2 and amount:
                file = "data/result.json"
                self.create_json_response(cur1, cur2, float(amount), file)
                # Змінюємо заголовок, оскільки результатом є не HTML, а JSON
                headers[0] = ("Content-Type", "text/json; charset=utf-8")
            # Якщо у формі задано недостатньо параметрів,
            # перенаправляємо на головну сторінку
            else:
                status = "303 SEE OTHER"
                headers.append(("Location", "/"))

        # http://127.0.0.1:8000/<будь-який інший запит>
        else:
            status = "404 NOT FOUND"
            file = "templates/error_404.html"

        start_response(status, headers)
        with open(file, encoding="utf-8") as f:
            page = Template(f.read()).substitute(params)
        return [bytes(page, encoding="utf-8")]


HOST = ""
PORT = 8000

if __name__ == "__main__":
    app = ExchangeRateJSON("data/currencies.json",
                           "data/exchange_rates.json")
    from wsgiref.simple_server import make_server
    print(" === Local webserver === ")
    make_server(HOST, PORT, app).serve_forever()
