""" A28.01 client
1. Скласти програму, що читає слова з заданого html-документу
у мережі (url) та зберігає їх разом з кількістю входжень
кожного слова у файлі у форматі JSON. Слова розділяються
пропусками та розділовими знаками. Структура JSON:
[
    {
        "word": слово,
        "count": кількість
    },
    ...
]

2. Скласти програму, що працює в оточенні веб-сервера,
отримує від клієнта url, виконує завдання 1 та повертає клієнту JSON.
"""

import re
from collections import Counter
from urllib.request import urlopen
from urllib.error import HTTPError
from html.parser import HTMLParser
import json


WORD = r'\b([a-zа-яіїєґ]+)\b'


class WordsCounterHTMLParser(HTMLParser):
    """ Клас, який дозволяє виконати аналіз html-файлу з метою
    підрахунку кількості входжень кожного слова.
    Результат зберігається у полі counter
    у форматі Counter (словник: слово - кількість входжень).
    """

    def __init__(self):
        super().__init__()
        self.in_body = False
        self.in_script = False
        self.counter = Counter()

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        elif tag == "script":
            self.in_script = True

    def handle_data(self, data):
        if self.in_body and not self.in_script:
            words = re.findall(WORD, data, re.I)
            words = [word.lower() for word in words]
            self.counter.update(words)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False


def words_counter(string: str) -> Counter:
    """ Рахує кількість слів з деякого рядка та повертає результат
    у форматі Counter (словник: слово - кількість входжень).
    """
    words = re.findall(WORD, string, re.I)
    words = [word.lower() for word in words]
    return Counter(words)


def words_counter_to_json(counter: Counter, filename: str):
    """ Зберігає результат кількості слів у форматі JSON.

    :param counter: об'єкт типу Counter (словник)
    :param filename: ім'я JSON-файлу для збереження результату
    """
    lst = [
        {"word": word, "count": counter[word]}
        for word in sorted(counter)
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=4, ensure_ascii=False)


def words_counter_from_url_to_json(url: str, filename: str):
    """ Читає слова з заданого html-документу у мережі (url) та зберігає
    їх разом з кількістю входжень кожного слова у файлі у форматі JSON.

    :param url: URL-запит
    :param filename: ім'я JSON-файлу для збереження результату
    """
    try:
        request = urlopen(url)
        data = str(request.read(), encoding="utf-8", errors="ignore")
        info = request.info()
        if info.get("Content-type", "").startswith("text/html"):
            wc = WordsCounterHTMLParser()
            wc.feed(data)
            counter = wc.counter
        else:
            counter = words_counter(data)
        words_counter_to_json(counter, filename)
    except HTTPError as e:
        print(e)


if __name__ == "__main__":
    test_data = [
        "http://matfiz.univ.kiev.ua/pages/15",
        "http://matfiz.univ.kiev.ua/userfiles/files/t01_01_polynom.py",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"
    ]
    for i, url in enumerate(test_data, 1):
        filename = "data/test{}.json".format(i)
        words_counter_from_url_to_json(url, filename)
