__author__ = 'sasaki'


def getMainModule():
    from sys import modules

    return modules["__main__"]


def getMainModuleName():
    from os.path import basename, splitext

    b = basename(getMainModule().__file__)
    (stem, ext) = splitext(b)
    return stem


import unittest
import types


class _TestCase(unittest.TestCase):
    def testGetMainModule(self):
        m = getMainModule()
        self.assertIsInstance(m, types.ModuleType)

    def testGetMainModuleName(self):
        self.assertEqual(getMainModuleName(), "MainModule")


if __name__ == "__main__":
    unittest.main()
