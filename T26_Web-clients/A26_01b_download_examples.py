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

Використати структурний аналіз HTML за допомогою класу HTMLParser
з модуля html.parser.
"""


from urllib.request import urlopen      # Функція для отримання веб-сторінки з мережі
from urllib.request import urlretrieve  # Функція для завантаження файлу з мережі
from html.parser import HTMLParser
import os


class TopicsViewParser(HTMLParser):
    """ Клас для знаходження посилання на тему з номером n.
    """

    def __init__(self, n):
        super().__init__()
        self.topic = "Тема {}.".format(n)  # Номер теми
        self.in_a = False  # Чи знаходимось в тегу <a>
        self.attrs = None  # Атрибути тегу
        self.url = None    # Посилання на веб-сторінку теми номер n

    def handle_starttag(self, tag, attrs):
        if not self.url:
            # Якщо заходимо в тег <a> з класом "list-group-item"
            # (class="list-group-item")
            if tag == "a" and ("class", "list-group-item") in attrs:
                self.in_a = True
                self.attrs = attrs

    def handle_data(self, data):
        if not self.url:
            # Якщо знаходимося в тегу <a> та
            # його дані починаються з рядка "Тема {}."
            if self.in_a and data.strip().startswith(self.topic):
                # Отримуємо атрибут з посиланням (href="...")
                self.url = dict(self.attrs)["href"]

    def handle_endtag(self, tag):
        if not self.url:
            # Якщо виходимо з тегу <a>
            if tag == "a":
                self.in_a = False


class PyFilesViewParser(HTMLParser):
    """ Клас для знаходження всіх python-файлів з html-документу.
    """

    def __init__(self):
        super().__init__()
        self.pyfiles = []  # Список знайдених python-файлів

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs)["href"]
            # Якщо посилання закінчується на .py чи .pyw, то
            # додаємо його до списку
            if href.endswith((".py", ".pyw")):
                self.pyfiles.append(href)


def get_html(url):
    """ Повертає розкодавані дані веб-сторінки за заданою адресою."""
    return str(urlopen(url).read(), encoding="utf-8", errors="ignore")


def download_examples(n, folder):
    """ З сайту http://matfiz.univ.kiev.ua завантажує
    усі python-файли за номером теми n у директорію folder.
    """
    main_url = "http://matfiz.univ.kiev.ua"
    # Отримуємо дані веб-сторінки з темами
    topics_html = get_html(main_url + "/pages/13")
    # Шукаємо посилання на веб-сторінку з n-тою темою
    # та отримуємо її повну адресу
    tvp = TopicsViewParser(n)
    tvp.feed(topics_html)
    topic_url = main_url + tvp.url
    tvp.close()
    # Отримуємо сторінку n-тою темою
    topic_html = get_html(topic_url)
    # Створюємо каталог для збереження файлів
    if folder and not os.path.exists(folder):
        os.mkdir(folder)
    # Знаходимо список відносних посилань на python-файли
    pfvp = PyFilesViewParser()
    pfvp.feed(topic_html)
    pyfiles = pfvp.pyfiles
    pfvp.close()
    # Ітеруємо по всім посиланням на python-файли
    for example in pyfiles:
        example_url = main_url + example      # Повне посилання на файл
        filename = os.path.basename(example)  # Визначаємо ім`я файлу
        # Завантажуємо файл і зберігаємо їх у директорії folder
        urlretrieve(example_url, os.path.join(folder, filename))


if __name__ == "__main__":
    topic = 30
    download_examples(30, f"examples{topic}")
