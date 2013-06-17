class Hello3(object):
    pass


import unittest

import Hello


class _TestBuiltinDir(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testNamesInTheCurrentLocalScope(self):
        names_in_the_current_local_scope = dir()
        self.assertEqual(['self'], names_in_the_current_local_scope)

    def testHello(self):
        attributes_of_Hello_module = dir(Hello)
        self.assertIsInstance(attributes_of_Hello_module, list)
        for x in attributes_of_Hello_module:
            self.assertIsInstance(x, str)
            if x == "__doc__":
                self.assertIsNone(getattr(Hello, x))
            elif x == "__file__":
                self.assertRegexpMatches(getattr(Hello, x), ".+Hello.pyc$")
            elif x == "__name__":
                self.assertEqual("Hello", getattr(Hello, x))
            elif x == "__package__":
                self.assertIsNone(getattr(Hello, x))
            else:
                print (x, getattr(Hello, x))


if __name__ == "__main__":
    unittest.main()
