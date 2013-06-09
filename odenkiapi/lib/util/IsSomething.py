__author__ = 'sasaki'
isiterable = lambda obj: isinstance(obj, basestring) or hasattr(obj, '__iter__')


def isEqualIfExists(o1, o2, a):
    if not hasattr(o1, a) and not hasattr(o2, a): return True
    if not hasattr(o1, a): return False
    if not hasattr(o2, a): return False
    assert (isinstance(o1, object))
    assert (isinstance(o2, object))
    if getattr(o1, a) != getattr(o2, a): return False
    return True


import unittest


class _TestCase(unittest.TestCase):
    class classA(object):
        x = 1

    class classB(object):
        y = 1

    class classC(object):
        x = 1
        y = 1

    def setUp(self):
        self.a1 = _TestCase.classA()
        self.a2 = _TestCase.classA()
        self.b1 = _TestCase.classB()
        self.b2 = _TestCase.classB()
        self.c1 = _TestCase.classC()
        self.c2 = _TestCase.classC()

    def testClassMemberIsNotAttribute(self):
        self.assertFalse(isEqualIfExists(self.a1, self.b1, "x"))
        self.assertFalse(isEqualIfExists(self.a1, self.b1, "y"))
        self.assertTrue(isEqualIfExists(self.a1, self.c1, "x"))
        self.assertFalse(isEqualIfExists(self.a1, self.c1, "y"))
        self.assertFalse(isEqualIfExists(self.b1, self.c1, "x"))
        self.assertTrue(isEqualIfExists(self.b1, self.c1, "y"))

    def testClassMemberIsClassAttribute(self):
        self.assertTrue(hasattr(_TestCase.classA, "x"))

    def testClassMember(self):
        self.assertEqual(_TestCase.classA.x, 1)

    def testClassMemberViaInstance(self):
        self.assertEqual(self.a1.x, 1)

    def testClassMemberIsInstanceAttribute(self):
        self.assertTrue(hasattr(self.a1, "x"))

    def testClassMemberIsNotOverridden(self):
        self.assertEqual(_TestCase.classA.x, 1)
        self.assertEqual(self.a1.x, 1)

        self.assertIs(_TestCase.classA.x, self.a1.x)
        self.a1.x = 2
        self.assertIsNot(_TestCase.classA.x, self.a1.x)

        self.assertIs(_TestCase.classA.x, self.a2.x)
        self.a2.x = 3
        self.assertIsNot(_TestCase.classA.x, self.a2.x)

        self.assertEqual(_TestCase.classA.x, 1)
        self.assertEqual(self.a1.x, 2)
        self.assertEqual(self.a2.x, 3)


if __name__ == "__main__":
    unittest.main()
