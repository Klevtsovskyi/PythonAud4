

import openpyxl
from string import Template

# Рядок радіокнопок (<tr> - table row) для таблиці (тег <table>)
RADIO = """
    <tr>
      <td>
        <input type="radio" id="from$cur" name="from" value="$cur">
        <label for="from$cur">$cur</label>
      </td>
      <td>
        <input type="radio" id="to$cur" name="to" value="$cur">
        <label for="to$cur">$cur</label>
      </td>
    <tr>
"""


def get_currencies(xlsx_file):
    """ Повертає список кодів валют з xlsx-файлу"""
    wb = openpyxl.open(xlsx_file)
    ws = wb["currencies"]
    return [ws.cell(i, 1).value for i in range(1, ws.max_row + 1)]


def get_exchange_rate(xlsx_file):
    """ Повертає список трійок:
    коду 1-ої валюти, коду 2-ої валюти, курс обміну
    з xlsx-файлу"""
    wb = openpyxl.open(xlsx_file)
    ws = wb["rate"]
    return [[cell.value for cell in row] for row in ws.rows][1:]


def obtain_rate(cur1, cur2, amount, xlsx_file):
    """ Повертає amount кількість одиниць валюти 1 у валюті 2
    згідно xlsx-файлу"""
    if cur1 == cur2:
        return amount
    for c1, c2, rate in get_exchange_rate(xlsx_file):
        if c1 == cur1 and c2 == cur2:
            return amount * rate
        elif c2 == cur1 and c1 == cur2:
            return amount / rate


if __name__ == '__main__':
    data = "data/currencies.xlsx"       # Файл з даними валют
    html = "templates/currencies.html"  # Шаблон для побудови сторінки
    # Заповнюємо таблицю рядками радіо-кнопоками
    table_rows = ""
    for cur in get_currencies(data):
        table_rows += Template(RADIO).substitute(cur=cur)
    # Відкриваємо шаблон та підставляємо рядки до таблиці
    with open(html, encoding="utf-8") as f:
        page = Template(f.read()).substitute(currencies=table_rows)

    import os
    if os.name == "nt":
        import sys, codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

    print("Content-type: text/html charset=utf-8\n")
    print(page)
