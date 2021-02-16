

import cgi
from currencies import obtain_rate
from string import Template


if __name__ == '__main__':
    data = "data/currencies.xlsx"          # Файл з даними валют
    html = "templates/exchange_rate.html"  # Шаблон для побудови сторінки
    # Отримуємо дані з форми
    form = cgi.FieldStorage()
    cur1 = form.getfirst("from", "")
    cur2 = form.getfirst("to", "")
    amount = form.getfirst("amount", "")
    # Якщо дані заповнено повністю, будуємо результат
    res = ""
    if cur1 and cur2 and amount:
        rate = obtain_rate(cur1, cur2, float(amount), data)
        rate = round(rate, 2)
        res = "{} {} = {} {}".format(amount, cur1, rate, cur2)
    # Відкриваємо шаблон та підставляємо результат
    with open(html, encoding="utf-8") as file:
        page = Template(file.read()).substitute(result=res)

    import os
    if os.name == "nt":
        import sys, codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

    print("Content-type: text/html charset=utf-8\n")
    print(page)
