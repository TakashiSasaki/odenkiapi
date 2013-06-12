#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
import datetime

from google.appengine.ext import ndb

import dateutil.parser


def _awareToNative(dt_aware):
    assert isinstance(dt_aware.tzinfo, datetime.tzinfo)
    utc_time_tuple = dt_aware.utctimetuple()
    dt_native = datetime.datetime(utc_time_tuple.tm_year, utc_time_tuple.tm_mon, utc_time_tuple.tm_mday,
                                  utc_time_tuple.tm_hour, utc_time_tuple.tm_min, utc_time_tuple.tm_sec)
    return dt_native


def isoToNative(iso_string):
    dt_aware = dateutil.parser.parse(iso_string)
    dt_native = _awareToNative(dt_aware)
    assert dt_native.tzinfo is None
    return dt_native


def nativeToEpoch(dt_native):
    assert dt_native.tzinfo is None
    utc_time_tuple = dt_native.utctimetuple()
    import calendar

    epoch = calendar.timegm(utc_time_tuple)
    return epoch


class Relay(ndb.Model):
    productName = ndb.StringProperty(indexed=True, required=True)
    serialNumber = ndb.StringProperty(indexed=True, required=True)
    moduleId = ndb.StringProperty(indexed=True, required=True)
    relayId = ndb.StringProperty(required=True)
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
    def fetchRelayKeys(cls, product_name, serial_number, module_id):
        q = Relay.query()
        q = q.filter(Relay.productName == product_name)
        q = q.filter(Relay.serialNumber == serial_number)
        q = q.filter(Relay.moduleId == module_id)
        keys = q.fetch(keys_only=True)
        return keys

    def setIsoString(self, iso_string):
        dt_native = isoToNative(iso_string)
        self.scheduledDateTime = dt_native

    def getEpoch(self):
        return nativeToEpoch(self.scheduledDateTime)


class Relays(dict):
    def setExpectedState(self, relay_id, scheduled_date_time, expected_state=None):
        relay = self.get(relay_id)
        if relay is None:
            relay = Relay()
            relay.productName = self.productName
            relay.serialNumber = self.serialNumber
            relay.moduleId = self.moduleId
            self[relay_id] = relay
        assert isinstance(relay, Relay)
        if not isinstance(scheduled_date_time, datetime.datetime):
            scheduled_date_time = isoToNative(scheduled_date_time)
        assert isinstance(scheduled_date_time, datetime.datetime)
        assert scheduled_date_time.tzinfo is None
        relay.relayId = relay_id
        relay.scheduledDateTime = scheduled_date_time
        relay.expectedState = expected_state
        relay.put()

    def __init__(self, product_name, serial_number, module_id):
        self.productName = product_name
        self.serialNumber = serial_number
        self.moduleId = module_id
        keys = Relay.fetchRelayKeys(product_name, serial_number, module_id)
        #relays = Relays()
        for key in keys:
            relay = key.get()
            if self.get(relay.relayId) is None:
                self[relay.relayId] = relay
            else:
                key.delete()
                #return relays


import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def testDateTime(self):
        iso_string = "2013-06-13T21:33:44+09:00"
        datetime = dateutil.parser.parse(iso_string)
        time_tuple = datetime.utctimetuple()
        self.assertEqual(time_tuple.tm_year, 2013)
        self.assertEqual(time_tuple.tm_mon, 6)
        self.assertEqual(time_tuple.tm_mday, 13)
        self.assertEqual(time_tuple.tm_hour, 12)
        self.assertEqual(time_tuple.tm_min, 33)
        self.assertEqual(time_tuple.tm_sec, 44)
        native = isoToNative(iso_string)
        self.assertIsNone(native.tzinfo)
        time_tuple = native.utctimetuple()
        self.assertEqual(time_tuple.tm_year, 2013)
        self.assertEqual(time_tuple.tm_mon, 6)
        self.assertEqual(time_tuple.tm_mday, 13)
        self.assertEqual(time_tuple.tm_hour, 12)
        self.assertEqual(time_tuple.tm_min, 33)
        self.assertEqual(time_tuple.tm_sec, 44)

    def testRelay(self):
        dt_native = isoToNative("2013-06-13T20:00:01+09:00")
        Relay.putRelay("product1", "serial1", "module1", "relay1", dt_native, True)
        Relay.putRelay("product1", "serial1", "module2", "relay1", dt_native, True)
        Relay.putRelay("product1", "serial1", "module1", "relay1", dt_native, True)
        relays = Relays("product1", "serial1", "module1")
        #keys = Relay.fetchRelayKeys("product1", "serial1", "module1")
        self.assertEqual(len(relays), 1)
        relays = Relays("product1", "serial1", "module1")
        self.assertEqual(len(relays), 1)

    def testRelays(self):
        iso_string = "2013-06-13T19:01:00+09:00"
        utc_string = "2013-06-13 10:01:00"
        self.assertEqual(utc_string, unicode(isoToNative(iso_string)))
        #this epoch is calculated on http://www.infobyip.com/epochtimeconverter.php
        self.assertEqual(1371117660, nativeToEpoch(isoToNative(iso_string)))

        relays_before = Relays("product1", "serial1", "module2")
        relays_before.setExpectedState("relay2", iso_string, True)
        datetime_before = relays_before["relay2"].scheduledDateTime
        self.assertEqual(utc_string, unicode(datetime_before))

        relays_after = Relays("product1", "serial1", "module2")
        relay_after = relays_after["relay2"]
        self.assertIsInstance(relay_after, Relay)
        self.assertEqual(relay_after.relayId, "relay2")

        epoch_before = nativeToEpoch(isoToNative(iso_string))
        epoch_after = relay_after.getEpoch()
        self.assertEqual(epoch_before, epoch_after)
        self.assertTrue(relay_after.expectedState)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()

