""" A28.01 server
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

from words_counter_client import words_counter_from_url_to_json
import cgi


def app(environ, start_response):
    """ Метод для обробки даних сервером"""
    path = environ.get("PATH_INFO", "").lstrip("/")
    status = "200 OK"
    headers = [("Content-Type", "text/html; charset=utf-8")]
    file = "templates/words_count.html"

    # http://127.0.0.1:8000/
    if path == "":
        pass

    # http://127.0.0.1:8000/words_count.json
    elif path == "words_count.json":
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        url = form.getfirst("url", "")
        if url:
            # Рахуємо кількість слів у заданому URL-запиті
            # і записуємо результат в JSON-файл
            file = "data/words_count.json"
            words_counter_from_url_to_json(url, file)
            # Оскільки будемо видавати в браузері JSON-файл,
            # змінюємо перший заголовок
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
        page = f.read()
    return [bytes(page, encoding="utf-8")]


HOST = ""
PORT = 8000

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    print(" === Local webserver === ")
    make_server(HOST, PORT, app).serve_forever()
