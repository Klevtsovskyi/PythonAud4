""" A26.01
Скласти програму, яка читає з сайту кафедри математичної фізики
http://matfiz.univ.kiev.ua та завантажує у заданий каталог усі
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
# Шаблон для знахолдження файлу розширення .py та .pyw
PYFILE = r'"(.+\.pyw*)"'


def download_examples(n, folder):
    """ З сайту http://matfiz.univ.kiev.ua завантажує
    усі python-файли за номером теми n у директорію folder.
    """
    url = "http://matfiz.univ.kiev.ua"
    # Отримуємо дані веб-сторінки з темами
    topics_html = get_html(url + "/pages/13")
    # Шукаємо посилання на веб-сторінку з n-тою темою
    # та отримуємо її повну адресу
    topic_url = url + find_topic_url(topics_html, n)
    # Отримуємо сторінку n-тою темою
    topic_html = get_html(topic_url)
    # Створюємо каталог для збереження файлів
    if not os.path.exists(folder):
        os.mkdir(folder)
    # Знаходимо список відносних посилань на python-файли та
    # ітеруємо по всім таким посиланням
    for example in re.findall(PYFILE, topic_html):
        example_url = url + example           # Повне посилання на файл
        filename = os.path.basename(example)  # Визначаємо ім`я файлу
        # Завантажуємо файл і зберігаємо їх у директорії folder
        urlretrieve(example_url, os.path.join(folder, filename))


def get_html(url):
    """ Повертає розкодавані дані веб-сторінки за заданою адресою."""
    return str(urlopen(url).read(), encoding="utf-8", errors="ignore")


def find_topic_url(html, n):
    """ Шукає і повертає посилання на тему з номером n у заданому рядку.

    :param html: рядок html-типу
    :param n: номер шуканої теми
    """
    m = re.search(A_TAG_TOPIC.format(n), html)
    if m is None:
        raise RuntimeError("Заданої теми немає!")
    return m.group("URL")


if __name__ == "__main__":
    topic = 2
    download_examples(topic, f"examples{topic}")
