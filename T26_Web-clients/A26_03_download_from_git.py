from urllib.request import Request, urlopen, urlretrieve
from urllib.parse import quote
import os
import re


TOPIC = r'"path":"([TТ]{:0>2} - .*?)"'  # Шаблон знаходження назви теми
FILES = r'"path":"{}/(.+?)"'            # Шаблон знаходження назв файлів
EXT = (".py", ".pyw", ".pdf")           # Розширення файлів для завантаження


def get_html(url):
    """ Повертає розкодавані дані веб-сторінки за заданою адресою."""
    request = Request(url, headers={})
    response = urlopen(request)
    enc = response.info().get_content_charset()
    html = response.read().decode(encoding=enc)
    return html


def download_from_git(n):
    """
    Завантажує файли певної теми (1-30) з репозиторія
    https://github.com/krenevych/informatics/ у поточний каталог
    """
    site = "https://github.com"                  # Основний сайт
    rsite = "https://raw.githubusercontent.com"  # Сайт з файлами
    path = "/krenevych/informatics/"             # Репозиторій

    # Відкриваємо головну сторінку репозиторія та шукаємо назву теми
    url = site + path
    html = get_html(url)
    m = re.search(TOPIC.format(n), html)
    if m is None:
        raise RuntimeError(f"Теми {n} немає")
    topic = m.group(1)
    print(topic)

    # Відкриваємо сторінку з темою
    # Шлях необхідно закодувати, оскільки в ньому міститься кирилиця
    url = site + path + quote(f"blob/main/{topic}")
    html = get_html(url)

    # Створюємо каталог для збереження файлів
    if not os.path.isdir(topic):
        os.mkdir(topic)

    # Шукаємо та завантажуємо файли
    url = rsite + path + quote(f"main/{topic}/")
    for filename in re.findall(FILES.format(topic), html):
        if not filename.lower().endswith(EXT):
            continue
        print(filename)
        fileurl = url + filename
        downloadpath = os.path.join(topic, filename)
        urlretrieve(fileurl, downloadpath)


if __name__ == "__main__":
    no = int(input("Введіть номер теми: "))
    download_from_git(no)
