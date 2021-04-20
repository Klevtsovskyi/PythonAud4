"""
Описати функцію, що повертає суму всіх доданків при заданому значенні x,
що за абсолютною величиною не перевищують заданого ε > 0.
Скласти програму для тестування цієї функції при декількох значеннях x та ε.
y = ln(1 + x) = x - x^2/2 + x^3/3 - ... (|x| < 1)

Doctest

>>> from function import function
>>> function(0, 0.1)
0
>>> function(0.9, 0.0001) > function(0.8, 0.0001)
True
>>>
"""


def function(x, eps):
    assert abs(x) < 1
    assert eps > 0

    a = x
    s = a
    i = 1
    while abs(a) > eps:
        a *= - x * i / (i + 1)
        s += a
        i += 1
    return s
