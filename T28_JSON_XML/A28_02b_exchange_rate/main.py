"""
Скласти програму, яка працює в оточенні веб-сервера, для конвертування
валют. Поточні курси валют містяться у файлі у форматі
b) XML
на сервері у форматі: <код валюти 1> <код валюти 2> <курс>.
Код валюти – це рядок з 3 символів, наприклад UAH, USD, EUR тощо.
Currency1 Currency2 Rate
USD       UAH       24,81
EUR       UAH       27,75
…	      …	        …
Програма повинна забезпечити вибір двох валют зі списків кодів валют на
сторінці, введення суми у першій валюті та показ суми у другій валюті.
Результат показувати у форматі XML.
"""

import xml.etree.ElementTree as Et
import cgi
from string import Template
from wsgiref.simple_server import make_server


OPTION = """
      <option value="$cur_id">$cur_name</option>
"""


class ExchangeRateXML:

    def __init__(self, data):
        self.data = data

    def get_currencies(self):
        """ Повертає список валют з файлу XML"""
        # Читаємо дані і перетворюємо їх в екземляр класу ElementTree
        etree = Et.parse(self.data)
        # Знаходимо перше входження піделементу "currencies"
        currencies_el = etree.find("currencies")
        currencies = []
        # Пробігаємо по всім піделементам елементу "currencies"
        for currency_el in currencies_el:
            # Створюємо кортеж, куди додаємо значення атрибуту "id"
            # та вміст заданого елемента
            currency = (
                currency_el.get("id"),
                currency_el.text.strip()
            )
            # Додаємо кортеж до списку валют
            currencies.append(currency)
        return currencies

    def obtain_rate(self, cur1_id, cur2_id, amount):
        """ Повертає курс валюти cur1_id відносно валюти cur2_id"""
        if cur1_id == cur2_id:
            return amount

        etree = Et.parse(self.data)
        # Рядок-шлях до елемента: наделемент/елемент[@атрибут='значення']
        xpath = "exchange_rates/rate[@currency1='{}'][@currency2='{}']"
        # Підставляємо id валют і шукаємо заданий елемент
        rate_el = etree.find(xpath.format(cur1_id, cur2_id))
        # Якщо знайшли, повертаємо результат
        if rate_el is not None:
            rate = float(rate_el.text)
            return amount / rate
        # Інакше шукаємо елемент з оберненими параметрами
        rate_el = etree.find(xpath.format(cur2_id, cur1_id))
        if rate_el is not None:
            rate = float(rate_el.text)
            return amount * rate

    def get_currency_name(self, currency_id):
        """ Повертає ім`я валюти згідно її id"""
        etree = Et.parse(self.data)
        xpath = f"currencies/currency[@id='{currency_id}']"
        currency_el = etree.find(xpath)
        return currency_el.text

    def create_xml(self, cur1_id, cur2_id, amount, filename):
        """ Створює XML-файл з відповіддю для конвертування amount
        грошей у валюті cur1 до валюти cur2

        :param cur1_id: валюта, з якої конвертуємо
        :param cur2_id: валюта, в яку конвертуємо
        :param amount: кількість грошей для конвертування
        :param filename: ім`я XML-файлу
        :return:
        """
        rate = round(self.obtain_rate(cur1_id, cur2_id, amount), 2)
        cur1_name = self.get_currency_name(cur1_id)
        cur2_name = self.get_currency_name(cur2_id)
        # Створюємо корневий елемент
        root = Et.Element("exchange_rate")
        # Створюємо елемент з 1-ою валютою
        cur_el = Et.Element("currency", {"id": cur1_id, "name": cur1_name})
        cur_el.text = str(amount)
        root.append(cur_el)  # Додаємо до корневого елемента
        # Створюємо елемент з 2-ою валютою
        cur_el = Et.Element("currency", id=cur2_id, name=cur2_name)
        cur_el.text = str(rate)
        root.append(cur_el)  # Додаємо до корневого елемента

        etree = Et.ElementTree(root)
        etree.write(filename, encoding="utf-8", xml_declaration=True)

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "").lstrip("/")
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        params = {"currencies": ""}
        status = "200 OK"
        headers = [("Content-Type", "text/html; charset=utf-8")]
        file = "templates/currencies.html"

        # http://localhost:8000/
        if path == "":
            for ID, name in self.get_currencies():
                params["currencies"] += Template(OPTION).substitute(cur_id=ID, cur_name=name)

        # http://localhost:8000/exchange_rate.xml
        elif path == "exchange_rate.xml":
            cur1_id = form.getfirst("from", "")
            cur2_id = form.getfirst("to", "")
            amount = form.getfirst("amount", "")

            if cur1_id and cur2_id and amount:
                file = "data/result.xml"
                self.create_xml(cur1_id, cur2_id, float(amount), file)
                # Змінюємо заголовок, оскільки результатом є не HTML, а XML
                headers[0] = ("Content-Type", "application/xml; charset=utf-8")
            # Якщо у формі задано недостатньо параметрів,
            # перенаправляємо на головну сторінку
            else:
                status = "303 SEE OTHER"
                headers.append(("Location", "/"))

        # http://localhost:8000/<будь-який інший запит>
        else:
            status = "404 NOT FOUND"
            file = "templates/error_404.html"

        start_response(status, headers)
        with open(file, encoding="utf-8") as f:
            page = Template(f.read()).substitute(params)
        return [bytes(page, encoding="utf-8")]


HOST = ""
PORT = 8000

if __name__ == '__main__':
    app = ExchangeRateXML("data/currencies.xml")
    print(f"Локальний веб-сервер запущено на http://localhost:{PORT}")
    make_server(HOST, PORT, app).serve_forever()
