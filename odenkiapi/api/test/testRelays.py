# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
import datetime

from google.appengine.ext import webapp
import simplejson

from model.Hems import isoToNative
import api.Relays


class _Hello(webapp.RequestHandler):
    def get(self):
        request = self.request
        assert isinstance(request, webapp.Request)
        _Hello.body = self.request.body
        _Hello.arguments = self.request.arguments()
        _Hello.headers = self.request.headers

    def post(self):
        request = self.request
        assert isinstance(request, webapp.Request)
        _Hello.body = self.request.body
        _Hello.arguments = self.request.arguments()
        _Hello.headers = self.request.headers


class _TestCase(unittest.TestCase):
    __slots__ = ["paths", "app", "testapp"]

    def setUp(self):
        import webtest

        self.paths = []
        self.paths.extend(api.Relays.paths)
        self.paths.append(("/hello", _Hello))
        self.app = webapp.WSGIApplication(self.paths, debug=True)
        self.testapp = webtest.TestApp(self.app)
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        relays = api.Relays.Relays("product1", "serial1", "module1")
        relays.setExpectedState("relay111", datetime.datetime.utcnow() + datetime.timedelta(1), False)
        relays.setExpectedState("relay222", datetime.datetime.utcnow() + datetime.timedelta(1), True)

    def testSucceeded(self):
        response_before = self.testapp.get("/api/Relays/product1/serial1/module1")
        json_object_before = simplejson.loads(response_before.body)
        self.assertFalse(json_object_before["result"][0]["relay111"]["expectedState"])
        self.assertTrue(json_object_before["result"][0]["relay222"]["expectedState"])

        relays = api.Relays.Relays("product1", "serial1", "module1")
        relays.setExpectedState("relay111", datetime.datetime.utcnow() + datetime.timedelta(1), True)
        relays.setExpectedState("relay222", datetime.datetime.utcnow() + datetime.timedelta(1), False)
        response_after = self.testapp.get("/api/Relays/product1/serial1/module1")
        json_object_after = simplejson.loads(response_after.body)
        self.assertTrue(json_object_after["result"][0]["relay111"]["expectedState"])
        self.assertFalse(json_object_after["result"][0]["relay222"]["expectedState"])

    def testPost(self):
        iso_string = "2013-06-13T19:31:10+09:00"
        response = self.testapp.post(b"/api/Relays/product1/serial1/module1",
                                     {"scheduledDateTime": iso_string,
                                      "expectedState": True,
                                      "relayId": "relay5677"})
        response_json = simplejson.loads(response.body)
        self.assertEqual(response_json["result"][0][0]["relayId"], "relay111")
        self.assertEqual(response_json["result"][0][1]["relayId"], "relay222")
        self.assertEqual(response_json["result"][0][2]["relayId"], "relay5677")
        relays = api.Relays.Relays("product1", "serial1", "module1")
        self.assertEqual(relays["relay5677"].scheduledDateTime, isoToNative(iso_string))
        self.assertTrue(relays["relay5677"].expectedState)

    def testPostJson(self):
        iso_string = "2013-06-13T19:41:10+09:00"
        response = self.testapp.post_json(b"/api/Relays/product1/serial1/module1",
                                          {"scheduledDateTime": iso_string,
                                           "expectedState": True,
                                           "relayId": "relay456"})
        relays = api.Relays.Relays("product1", "serial1", "module1")
        #print(relays)
        self.assertEqual(relays["relay456"].scheduledDateTime, isoToNative(iso_string))
        self.assertTrue(relays["relay456"].expectedState)

    def testHelloGet(self):
        #response = self.testapp.get("/hello?a=b&a=c", headers=[("Content-Type", ';charset="utf-8"')])
        # As of WebOb 1.2,charset is not required for utf-8
        response = self.testapp.get("/hello?a=b&a=c")
        self.assertEqual(_Hello.body, "")
        self.assertEqual(_Hello.arguments, ["a"])
        try:
            self.assertEqual(_Hello.headers["Content-Type"], '; charset="utf-8"')
        except KeyError, e:
            pass

    def testHelloPost(self):
        response = self.testapp.post(b"/hello?v=b&a=z", {"c": "d"})
        self.assertEqual(_Hello.body, "c=d")
        self.assertEqual(_Hello.arguments, ["a", "c", "v"])
        self.assertIn(_Hello.headers["Content-Type"],
                      ('application/x-www-form-urlencoded; charset="utf-8"', 'application/x-www-form-urlencoded'))

    def testHelloPostJson(self):
        response = self.testapp.post_json(b"/hello?v=b&a=z", {"c": "d", "s": False})
        self.assertEqual(_Hello.body, '{"c": "d", "s": false}')
        self.assertEqual(_Hello.arguments, ["a", "v"])
        self.assertIn(_Hello.headers["Content-Type"], ('application/json; charset="utf-8"', 'application/json'))

    # def testPost(self):
    #     response = self.testapp.post_json(b"/api/Relays/product1/serial1/module1", {"a": "b"})

    def testDict(self):
        xx = {"1": "2", "3": "4"}
        for x, y in xx.iteritems():
            print(x, y)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()