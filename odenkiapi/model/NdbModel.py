from __future__ import unicode_literals, print_function
from google.appengine.ext.ndb import Model as _Model
#from logging import debug
#from model.Columns import Column, Columns
#from model.DataNdb import Data

class NdbModel(_Model):
    def to_list(self):
        raise RuntimeError("NdbModel.to_dict is obsoleted. Use CsvMixin")

    def to_row(self):
        raise RuntimeError("NdbModel.to_row is obsoleted. Use DataTableMixin")


import unittest


class _TestCase(unittest.TestCase):
    def test(self):
        n = NdbModel()
        self.assertRaises(RuntimeError, n.to_list)
        self.assertRaises(RuntimeError, n.to_row)


if __name__ == "__main__":
    unittest.main()