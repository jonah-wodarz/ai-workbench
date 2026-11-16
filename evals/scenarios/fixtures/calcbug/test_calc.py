import unittest

from calc import average, clamp, percent


class CalcTests(unittest.TestCase):
    def test_average_empty_is_zero(self):
        self.assertEqual(average([]), 0.0)

    def test_average(self):
        self.assertEqual(average([1, 2, 3]), 2.0)

    def test_percent_rounds_to_one_decimal(self):
        self.assertEqual(percent(1, 3), 33.3)

    def test_clamp(self):
        self.assertEqual(clamp(15, 0, 10), 10)


if __name__ == "__main__":
    unittest.main()
