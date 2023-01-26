""" A26.02 (T26.15*)
Скласти програму, яка отримує <Код Експрес-3> відповідної
станції зі сторінки Вікіпедії за запитом
https://uk.wikipedia.org/wiki/Список_залізничних_станцій_і_роз'їздів_України_(<перша літера назви міста>)
Наприклад, для станції Київ-Пасажирський відповідний запит на отримання сторінки з кодами -
https://uk.wikipedia.org/wiki/Список_залізничних_станцій_і_роз'їздів_України_(К)
В такому випадку код буде мати такий вигляд:
2200001

Використати структурний аналіз HTML за допомогою класу HTMLParser
з модуля html.parser.
"""

from urllib.request import urlopen  # Функція для отримання веб-сторінки з мережі
from urllib.parse import quote      # Функція для кодування кирилиці в url
from urllib.error import HTTPError  # Виключення, яке може виникати при відповіді веб-сервера
from html.parser import HTMLParser


class StationViewParser(HTMLParser):
    """ Клас, який дозволяє виконати аналіз html-файлу та знайти
    код експрес 3 за заданою залізничною станцією.

    Щоб запустити пошук, потрібно викликати
    метод StationViewParser.feed(self, data),
    де data - дані з html-файлу.
    """

    def __init__(self, station):
        super().__init__()
        self.station = station    # Назва станції
        self.station_code = None  # Шуканий код станції
        self.entered_tr = False   # Чи увійшли в тег <tr>
        self.in_first_a = False   # Чи знаходимося в першому тегу <a>?
        self.found_a = False      # Чи знайшли тег <a> з шуканю назвою станції?
        # Лічильник тегів <td>, які потрібно відрахувати щоб знайти потрібний
        self.td_count = 0
        # Чи знайшли потрібний тег <td>, в якому знаходить код станції?
        self.in_code_td = False

    def handle_starttag(self, tag, attrs):
        """ Метод, який викликається,
        коли зустрічаємо відкриття тегу (<tag>).

        :param tag: назва тегу (напр., для <a> маємо tag == 'a')
        :param attrs: список кортежів ключ-значення атрибутів тегу
                      (напр., для <a href="/wiki/" title="name">
                       маємо attrs == [('href', '/wiki/'), ('title', 'name')]).
        """
        if not self.station_code:
            # Якщо входимо в тег <tr>
            if tag == "tr":
                self.entered_tr = True
            # Якщо зустрічаємо перший тег <a> після <tr>
            elif self.entered_tr and tag == "a":
                self.in_first_a = True
            # Якщо знайшли потрібний тег <a>, починаєто відраховувати теги <td>
            elif self.found_a and tag == 'td':
                # Якщо відрахували потрібну кількість тегів <td>,
                if self.td_count == 4:
                    self.in_code_td = True  # то знаходимося в порібному тегу
                else:
                    self.td_count += 1

    def handle_endtag(self, tag):
        """ Метод, який викликається,
        коли зустрічаємо закриття тегу (</tag>).

        :param tag: назва тегу (напр., для </a> маємо tag == 'a').
        """
        if not self.station_code:
            if tag == "a" and self.in_first_a:  # Якщо виходимо з тегу <a>
                self.in_first_a = False
                self.entered_tr = False

    def handle_data(self, data):
        """ Метод, який викликається,
        коли зустрічаємо дані (тобто все за винятком тегів).

        :param data: рядок даних
        """
        if not self.station_code:
            # Якщо дані в першому тегу <a> співпадають з потрібною станцією
            if self.in_first_a and data == self.station:
                self.found_a = True  # Шуканий тег <a> знайдено
            elif self.in_code_td:    # Якщо знаходимося в потрібному тегу <td>,
                self.station_code = data  # присвоюємо дані і завершуємо пошук


def get_station_code(station):
    """
    Повертає Код Експрес-3 заданої станції.

    :param station: назва станції
    :return: код станції
    """
    # Будуємо URL-запит
    url = "https://uk.wikipedia.org"
    path = f"/wiki/Список_залізничних_станцій_і_роз'їздів_України_({station[0]})"
    # Кодуємо кирилицю в URL-запиті та визначаємо остаточний URL-запит
    full_url = url + quote(path, encoding="utf-8")
    try:
        # Отримуємо веб-сторінку з мережі
        request = urlopen(full_url)
        # Розкодовуємо веб-сторінку
        html = str(request.read(), encoding="utf-8", errors="ignore")
        # Створюємо об`єкт для структурного аналізу html
        svp = StationViewParser(station)
        svp.feed(html)           # Передаємо дані
        code = svp.station_code  # Отримаємо результат
        svp.close()              # Звільняємо буфер
        return code
    # У випадку помилки (неуспішного статусу відповіді), друкуємо її значення
    except HTTPError as e:
        print(e)


if __name__ == "__main__":
    stations = [
        "Київ-Пасажирський",
        "Львів",
        "Київ",
        "Орлівщина"
    ]
    for station in stations:
        code = get_station_code(station)
        if code:
            print(station, ":", code)
        else:
            print("Для", station, "кода не знайдено")
