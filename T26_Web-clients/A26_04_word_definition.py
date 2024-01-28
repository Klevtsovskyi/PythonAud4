from urllib.request import Request, urlopen
from urllib.parse import urlencode
from html.parser import HTMLParser


class Parser(HTMLParser):
    """ Клас для структурного аналізу для знаходження тлумачення слова із html"""

    def __init__(self):
        super().__init__()
        self.content = False  # Чи знайшли зміст тлумачення
        self.done = False     # Чи завершили роботу
        self.result = ""      # Результат

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        if self.content and tag == "p":
            self.result += "\n"
        # Блок, де починається шуканий зміст
        if tag == "div" and ("class", "toggle-content") in attrs:
            self.content = True

    def handle_data(self, data):
        if self.content:
            self.result += data

    def handle_endtag(self, tag):
        if self.done:
            return
        # Блок, де закінчується шуканий зміст
        if tag == "div":
            if self.content:
                self.done = True
            self.content = False


def get_html(url):
    """ Повертає розкодавані дані веб-сторінки за заданою адресою."""
    request = Request(url, headers={})
    response = urlopen(request)
    enc = response.info().get_content_charset()
    html = response.read().decode(encoding=enc)
    return html


def definition(word):
    """ Повертає тлумачення вказаного українського слова"""
    site = "https://slovnyk.ua"
    path = "/"
    params = urlencode({"swrd": word})

    url = site + path + "?" + params
    html = get_html(url)
    parser = Parser()
    parser.feed(html)
    return parser.result.strip()


if __name__ == "__main__":
    word = input("Введіть слово: ")
    print(definition(word))
