from __future__ import unicode_literals

import unittest
import model.Counter


class TestCase(unittest.TestCase):
    __slots__ = ["testbed"]

    def setUp(self):
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test(self):
        counter = model.Counter.Counter.getCurrentId("testcounter")
        self.assertEqual(counter, 0)
        counter = model.Counter.Counter.GetNextId("testcounter")
        self.assertEqual(counter, 1)
        counter = model.Counter.Counter.getCurrentId("testcounter")
        self.assertEqual(counter, 1)
        model.Counter.Counter.setCurrentId("testcounter", 10)
        counter = model.Counter.Counter.getCurrentId("testcounter")
        self.assertEqual(counter, 10)


if __name__ == "__main__":
    unittest.main()
