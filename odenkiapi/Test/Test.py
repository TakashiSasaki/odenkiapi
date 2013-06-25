__author__ = 'TakashiSasaki'
import unittest


class _TestCase(unittest.TestCase):
    def test(self):
        self.assertIsNone(None)
        pass

if __name__ == "__main__":
    print (dir())