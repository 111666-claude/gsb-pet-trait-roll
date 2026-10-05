import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pettrait.roller import Roller, load_traits  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RollerTest(unittest.TestCase):
    def test_load_traits(self):
        self.assertEqual(len(load_traits(os.path.join(HERE, "data", "traits.csv"))), 4)

    def test_roll_returns_known_trait(self):
        book = Roller(load_traits(os.path.join(HERE, "data", "traits.csv")), 1, 3)
        self.assertIn(book.roll("r1"), [item["trait"] for item in book.traits])

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Roller([], 1, 3).scanned, 0)


if __name__ == "__main__":
    unittest.main()
