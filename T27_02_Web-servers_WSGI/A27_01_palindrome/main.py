"""
Скласти програму, яка працює в оточенні веб-сервера, для введення рядка та
перевірки, чи є цей рядок паліндромом. Показати результат перевірки.

b) використати WSGI
"""

import cgi
from string import Template


def is_palindrome(string):
    """ Повертає True, якщо рядок string є паліндромом,
    або False в іншому випадку.
    """
    s = ""
    for ch in string:
        if ch.isalpha():
            s += ch.lower()
    return s == s[::-1]


def application(environ, start_response):
    """ Функція веб-сервера обробки запитів веб-клієнта.

    :param environ: словник параметрів, які клієнт відправляє серверу
    :param start_response: функція, яку сервер викликає для відповіді клієнту
    :return: список байтів закодованої html-сторінки відповіді
    """
    # Якщо шлях URL-запиту є пустим
    if environ.get("PATH_INFO", "").lstrip("/") == "":
        # Створюємо контейнер і передаємо йому дані з форми
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        string = form.getfirst("string", "")
        # Визначаємо результат
        if string == "":
            result = ""
        else:
            answer = "це паліндром!" if is_palindrome(string) else "це не паліндром!"
            result = "<h1>{} - {}</h1>".format(string, answer)
        # Створюємо успішну відповідь
        start_response("200 OK", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/palindrome.html", encoding="utf-8") as f:
            page = Template(f.read()).substitute(result=result)
    else:
        # У випадку помилки, відправляємо відповідь-повідомлення з описом помилки
        start_response("404 NOT FOUND", [("Content-type", "text/html; charset=utf-8"), ])
        with open("templates/error_404.html", encoding="utf-8") as f:
            page = f.read()

    return [bytes(page, encoding="utf-8")]


HOST = ""
PORT = 8000

if __name__ == '__main__':
    # Створюємо та запускаємо веб-сервер
    from wsgiref.simple_server import make_server
    print(" === Local webserver === ")
    make_server(HOST, PORT, application).serve_forever()
