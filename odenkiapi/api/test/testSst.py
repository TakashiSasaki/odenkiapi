from __future__ import unicode_literals, print_function
from sst.actions import *
from sst import runtests


class Test1(runtests.SSTTestCase):
    def test1(self):
        go_to("http://localhost:8080/post?x=y&x=u")


import unittest

if __name__ == "__main__":
    unittest.main()

