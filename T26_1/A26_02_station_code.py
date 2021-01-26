""" A26.02 (T26.15*)
Скласти програму, яка отримує <Код Експрес-3> відповідної
станції зі сторінки Вікіпедії за запитом
https://uk.wikipedia.org/wiki/Список_залізничних_станцій_і_роз'їздів_України_(<перша літера назви міста>)
Наприклад, для станції Київ-Пасажирський відповідний запит на отримання сторінки з кодами -
https://uk.wikipedia.org/wiki/Список_залізничних_станцій_і_роз'їздів_України_(К)
В такому випадку код буде мати такий вигляд:
2200001
"""

from urllib.request import urlopen  # Функція для отримання веб-сторінки з мережі
from urllib.parse import quote      # Функція для кодування кирилиці в url
from urllib.error import HTTPError  # Виключення, яке може виникати при відповіді веб-сервера
import re
from string import Template  # Клас для форматування рядків


# Шаблон для отримання вмісту тегу <tr>
TR_TAG = r"<tr>(.*?)<\/tr>"
# Шаблон для отримання експрес-коду станції
# Замість $station підставляється потрібна станція
CODE_PATTERN = r"<a.*?>$station<\/a>.*?<td>(?P<CODE>\d{7})<\/td>"


def get_station_code(station):
    """
    Повертає Код Експрес-3 заданої станції.

    :param station: назва станції
    :return: код станції
    """
    # Будуємо URL-запит
    url = "https://uk.wikipedia.org/wiki/"
    path = ("Список_залізничних_станцій_і_роз'їздів_України_({})"
            .format(station[0]))
    # Кодуємо кирилицю в URL-запиті та визначаємо остаточний URL-запит
    full_url = url + quote(path, encoding="utf-8")
    try:
        # Отримуємо веб-сторінку з мережі
        request = urlopen(full_url)
        # Розкодовуємо веб-сторінку
        html = str(request.read(), encoding="utf-8", errors="ignore")
        # Підставляємо у шаблон задану станцію
        CODE = Template(CODE_PATTERN).substitute({"station": station})
        # Пробігаємо по всім тегам <tr>
        for row_html in re.findall(TR_TAG, html, re.S):
            # Отримуємо вміст тегу <tr>
            # Шукаємо у цьому вмісті код потрібної станції
            code_match = re.search(CODE, row_html, re.S)
            # Якщо код знайдено, повертаємо його
            if code_match:
                return code_match.group("CODE")
    # У випадку помилки (неуспішного статусу відповіді), друкуємо її значення
    except HTTPError as e:
        print(e)


if __name__ == '__main__':
    stations = ["Київ-Пасажирський",
                "Львів",
                "Київ"]
    for station in stations:
        code = get_station_code(station)
        if code:
            print(station, ":", code)
        else:
            print("Для", station, "кода не знайдено")
