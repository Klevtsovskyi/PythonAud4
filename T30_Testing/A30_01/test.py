"""
Описати функцію, що повертає суму всіх доданків при заданому значенні x,
що за абсолютною величиною не перевищують заданого ε > 0.
Скласти програму для тестування цієї функції при декількох значеннях x та ε.
y = ln(1 + x) = x - x^2/2 + x^3/3 - ... (|x| < 1)
"""


import unittest
from function import function
from math import log
import random


class TestFunction(unittest.TestCase):  # Клас для тестів

    def test_01_equal(self):
        x = 0
        eps = 0.1
        expected_value = 0
        value = function(x, eps)
        self.assertAlmostEqual(expected_value, value)

    def test_02_equal(self):
        x = 0.5
        eps = 1e-3
        value = function(x, eps)
        expected_value = log(1 + x)
        self.assertAlmostEqual(expected_value, value, delta=0.001)

    def test_03_equal(self):
        x = -0.1
        eps = 1e-10
        expected_value = log(1 + x)
        value = function(x, eps)
        self.assertAlmostEqual(expected_value, value)

    def test_04_equal(self):
        x = -0.5
        eps = 1e-15
        expected_value = log(1 + x)
        value = function(x, eps)
        self.assertAlmostEqual(expected_value, value)

    def test_05_true(self):
        x = 0.87
        eps = 1e-15
        expected_value = log(1 + x)
        value = function(x, eps)
        self.assertTrue(abs(expected_value - value) < 1e-15)

    def test_06_true(self):
        x = 0.00023
        eps = 1e-15
        expected_value = log(1 + x)
        value = function(x, eps)
        self.assertTrue(abs(expected_value - value) < 1e-15)

    def test_07_false(self):
        x = 0.00023
        eps = 1e-15
        expected_value = log(1 + x)
        value = function(x, eps)
        self.assertFalse(abs(expected_value - value) > 1e-15)

    def test_08_less(self):
        x1 = 0.8888
        x2 = 0.9999
        eps = 1e-6
        value1 = function(x1, eps)
        value2 = function(x2, eps)
        self.assertLess(value1, value2)

    def test_09_equal_100_random_values(self):
        for _ in range(100):
            x = random.random() * 2 - 1
            x *= random.choice((-1, 1))
            eps = 1e-15
            expected_value = log(1 + x)
            value = function(x, eps)
            self.assertAlmostEqual(expected_value, value)

    def test_10_raise(self):
        with self.assertRaises(AssertionError):
            function(-1, 0.1)
        with self.assertRaises(AssertionError):
            function(0, 0)
        with self.assertRaises(AssertionError):
            function(20, -20)


if __name__ == '__main__':
    unittest.main(verbosity=2)
