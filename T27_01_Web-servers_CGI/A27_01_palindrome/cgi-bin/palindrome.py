""" A27.01
Скласти програму, яка працює в оточенні веб-сервера,
для введення рядка та перевірки, чи є цей рядок паліндромом.
Показати результат перевірки.

а) використати CGI
"""
# Цей файл знаходиться у директорії /cgi-bin/

import cgi
from string import Template


def is_palindrome(string):
    """ Повертає True, якщо рядок string є паліндромом,
    або False в іншому випадку.
    """
    s = ""
    for char in string:
        if char.isalpha():
            s += char.lower()
    return s == s[::-1]


if __name__ == '__main__':
    form = cgi.FieldStorage()  # Створюємо контейнер і отримуємо дані з форми
    # Беремо перше значення (атрибут value) з ім'ям (атрибут name) "string"
    # якщо такого поля в формі немає, то беремо пустий рядок
    string = form.getfirst("string", "")
    answer = 'це паліндром!' if is_palindrome(string) else 'це не паліндром!'
    result = string + ' - ' + answer  # Визначаємо результат
    # Відкриваємо шаблон
    with open("result.html", encoding="utf-8") as f:
        # Зчитуємо дані і підставляємо результат
        page = Template(f.read()).substitute(result=result)

    import os  # Якщо у нас операційна система Windows, то змінюємо кодування
    if os.name == "nt":
        import sys, codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

    # додаємо заголовок та друкуємо сторінку в веб-браузер
    print("Content-type: text/html charset=utf-8\n")
    print(page)
