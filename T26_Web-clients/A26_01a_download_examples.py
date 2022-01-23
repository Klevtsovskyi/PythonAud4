""" A26.01
Скласти програму, яка читає з сайту кафедри математичної фізики
(http://matfiz.univ.kiev.ua) та завантажує у заданий каталог усі
приклади програм із заданої теми.
Сторінка з адресами тем - http://matfiz.univ.kiev.ua/pages/13
Посилання на сторінку теми на сторінці з адресами має вигляд:
<a href=[url-шлях]/pages/YY" >Тема XX
де [url-шлях] – відносний шлях до сторінки (по відношенню до
http://matfiz.univ.kiev.ua) YY – номер сторінки, XX – номер теми

Посилання на приклади на сторінці теми має вигляд:
href="/userfiles/files/[файл]"
де [файл] – ім’я файлу прикладу.
Файли прикладів можуть мати розширення .py або .pyw
"""


from urllib.request import urlopen      # Функція для отримання веб-сторінки з мережі
from urllib.request import urlretrieve  # Функція для завантаження файлу з мережі
import re
import os


# Шаблон для отримання адреси відповідної теми
A_TAG_TOPIC = r'<a href="(?P<URL>.+)" >Тема {}\..+?</a>'
# Шаблон для файлу розширення .py та .pyw
PYFILE = r'"(.+\.pyw*)"'
# Шаблон для отрримання назви файлу з його URL-адреси
FILENAME = r'.+/(?P<NAME>.+)'


def download_examples(n, dirname=""):
    """ З сайту http://matfiz.univ.kiev.ua завантажує
    усі python-файли за номером теми n в папку dirname,
    якщо dirname не вказано, то завантажує файли у поточну папку.
    """
    main_url = "http://matfiz.univ.kiev.ua"
    # Отримуємо дані веб-сторінки з темами
    topics_html = get_html(main_url + "/pages/13")
    # Шукаємо посилання на веб-сторінку з n-тою темою
    # та отримуємо її повну адресу
    topic_url = main_url + find_topic_url(topics_html, n)
    # Отримуємо сторінку n-тою темою
    topic_html = get_html(topic_url)
    # Створюємо каталог для збереження файлів
    if dirname and not os.path.exists(dirname):
        os.mkdir(dirname)
    # Знаходимо список відносних посилань на python-файли та
    # ітеруємо по всім таким посиланням
    for example in find_examples_urls(topic_html):
        example_url = main_url + example # Повне посилання на файл
        filename = get_filename(example) # Визначаємо ім'я файлу
        # Завантажуємо файл і зберігаємо їх у папці dirname
        urlretrieve(example_url, os.path.join(dirname, filename))


def get_html(url):
    """ Повертає розкодавані дані веб-сторінки за заданою адресою."""
    return str(urlopen(url).read(), encoding="utf-8", errors="ignore")


def find_topic_url(html, n):
    """ Шукає і повертає посилання на тему з номером n
    у заданому рядку.

    :param html: рядок html-типу
    :param n: номер шуканої теми
    """
    return re.search(A_TAG_TOPIC.format(n), html).group("URL")


def find_examples_urls(html):
    """ Повертає список усіх відносних посилань у заданому
    рядку на файли з розширенням .py або .pyw
    """
    return re.findall(PYFILE, html)


def get_filename(example):
    """ Повертає у заданій віносній URL-адресі ім'я python-файлу"""
    return re.search(FILENAME, example).group("NAME")


if __name__ == '__main__':
    download_examples(2, "examples")
