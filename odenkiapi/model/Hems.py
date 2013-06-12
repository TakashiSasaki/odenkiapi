#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
import datetime

from google.appengine.ext import ndb

import dateutil.parser


class Relay(ndb.Model):
    productName = ndb.StringProperty(indexed=True, required=True)
    serialNumber = ndb.StringProperty(indexed=True, required=True)
    moduleId = ndb.StringProperty(indexed=True, required=True)
    relayId = ndb.IntegerProperty(required=True)
    scheduledDateTime = ndb.DateTimeProperty(required=True)
    expectedState = ndb.BooleanProperty(required=False)

    @classmethod
    def putRelay(cls, product_name, serial_number, module_id, relay_id, scheduled_date_time, expected_state=None):
        relay = Relay()
        relay.productName = product_name
        relay.serialNumber = serial_number
        relay.moduleId = module_id
        relay.relayId = relay_id
        relay.scheduledDateTime = scheduled_date_time
        relay.expectedState = expected_state
        relay.put()
        return relay

    @classmethod
    def fetchRelays(cls, product_name, serial_number, module_id):
        q = Relay.query()
        q = q.filter(Relay.productName == product_name)
        q = q.filter(Relay.serialNumber == serial_number)
        q = q.filter(Relay.moduleId == module_id)
        keys = q.fetch(keys_only=True)
        return keys

    @classmethod
    def getRelays(cls, product_name, serial_number, module_id):
        keys = cls.fetchRelay(product_name, serial_number, module_id)
        relays = [None] * len(keys)
        for i in range(len(keys)):
            relays[i] = keys[i].get()
        return relays


import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def test(self):
        dt_aware = dateutil.parser.parse("2013-06-13T19:00:00+09:00")
        self.assertEqual("2013-06-13 19:00:00+09:00", str(dt_aware))
        self.assertIsInstance(dt_aware.tzinfo, datetime.tzinfo)

        utc_time_tuple = dt_aware.utctimetuple()
        dt_native = datetime.datetime(utc_time_tuple.tm_year, utc_time_tuple.tm_mon, utc_time_tuple.tm_mday,
                                      utc_time_tuple.tm_hour, utc_time_tuple.tm_min, utc_time_tuple.tm_sec)
        self.assertEqual("2013-06-13 10:00:00", str(dt_native))
        self.assertIsNone(dt_native.tzinfo)

        Relay.putRelay("product1", "serial1", "module1", 1, dt_native, True)
        keys = Relay.fetchRelays("product1", "serial1", "module1")
        self.assertIsInstance(keys, list)
        self.assertEqual(len(keys), 1)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()

