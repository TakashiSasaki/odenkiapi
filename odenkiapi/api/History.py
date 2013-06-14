# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json as simplejson
from google.appengine.ext import webapp
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.Hems import Relays, isoToNative
from model.DataNdb import Data


class _History(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)
        field = jrequest.getPathInfo(6)

        product_name_data = Data.getByFieldAndString("productName", product_name)
        serial_number_data = Data.getByFieldAndString("serialNumber", serial_number)
        module_id_data = Data.getByFieldAndString("moduleId", module_id)

        relays = Relays(product_name, serial_number, module_id)
        jresponse.addResult(relays)

    def POST(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)
        #self.response.headers.add_header(b"Set-Cookie", b"productName=%s" % product_name.encode())
        #self.response.headers.add_header(b"Set-Cookie", b"serialNumber=%s" % serial_number.encode())
        #self.response.headers.add_header(b"Set-Cookie", b"moduleId=%s" % module_id.encode())

        relays = Relays(product_name, serial_number, module_id)
        assert isinstance(relays, Relays)
        for relay in jrequest.list:
            relays.setExpectedState(relay["relayId"], relay["scheduledDateTime"], relay["expectedState"])
        if jrequest.dict:
            if isinstance(jrequest.dict["relayId"], list) and len(jrequest.dict["relayId"]) == 1:
                relay_id = jrequest.dict["relayId"][0]
            else:
                relay_id = jrequest.dict["relayId"]
            if isinstance(jrequest.dict["scheduledDateTime"], list) and len(jrequest.dict["scheduledDateTime"]) == 1:
                scheduled_date_time = jrequest.dict["scheduledDateTime"][0]
            else:
                scheduled_date_time = jrequest.dict["scheduledDateTime"]
            if isinstance(jrequest.dict["expectedState"], list) and len(jrequest.dict["expectedState"]) == 1:
                expected_state = jrequest.dict["expectedState"][0]
            else:
                expected_state = jrequest.dict["expectedState"]
            relays.setExpectedState(relay_id, scheduled_date_time, expected_state)
            assert isinstance(jrequest.request, webapp.Request)

        relays = Relays(product_name, serial_number, module_id)
        assert isinstance(relays, dict)
        l = []
        for k, v in relays.iteritems():
            l.append(v)
        jresponse.addResult(l)


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


maps = [("/api/Relays/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+", _Relays),
        ("/api/Relays/", _Index)]

import unittest
import datetime


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest

        maps.append(("/hello", _Hello))
        app = webapp.WSGIApplication(maps, debug=True)
        self.testapp = webtest.TestApp(app)
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        relays = Relays("product1", "serial1", "module1")
        relays.setExpectedState("relay111", datetime.datetime.utcnow() + datetime.timedelta(1), False)
        relays.setExpectedState("relay222", datetime.datetime.utcnow() + datetime.timedelta(1), True)

    def testSucceeded(self):
        response_before = self.testapp.get("/api/Relays/product1/serial1/module1")
        json_object_before = simplejson.loads(response_before.body)
        #print(response_before.body)
        self.assertFalse(json_object_before["result"][0]["relay111"]["expectedState"])
        self.assertTrue(json_object_before["result"][0]["relay222"]["expectedState"])

        relays = Relays("product1", "serial1", "module1")
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
        relays = Relays("product1", "serial1", "module1")
        self.assertEqual(relays["relay5677"].scheduledDateTime, isoToNative(iso_string))
        self.assertTrue(relays["relay5677"].expectedState)

    def testPostJson(self):
        iso_string = "2013-06-13T19:41:10+09:00"
        response = self.testapp.post_json(b"/api/Relays/product1/serial1/module1",
                                          {"scheduledDateTime": iso_string,
                                           "expectedState": True,
                                           "relayId": "relay456"})
        relays = Relays("product1", "serial1", "module1")
        print(relays)
        self.assertEqual(relays["relay456"].scheduledDateTime, isoToNative(iso_string))
        self.assertTrue(relays["relay456"].expectedState)


    def testHelloGet(self):
        response = self.testapp.get("/hello?a=b&a=c")
        self.assertEqual(_Hello.body, "")
        self.assertEqual(_Hello.arguments, ["a"])
        self.assertEqual(_Hello.headers["Content-Type"], '; charset="utf-8"')

    def testHelloPost(self):
        response = self.testapp.post(b"/hello?v=b&a=z", {"c": "d"})
        self.assertEqual(_Hello.body, "c=d")
        self.assertEqual(_Hello.arguments, ["a", "c", "v"])
        self.assertEqual(_Hello.headers["Content-Type"], 'application/x-www-form-urlencoded; charset="utf-8"')

    def testHelloPostJson(self):
        response = self.testapp.post_json(b"/hello?v=b&a=z", {"c": "d", "s": False})
        self.assertEqual(_Hello.body, '{"c": "d", "s": false}')
        self.assertEqual(_Hello.arguments, ["a", "v"])
        self.assertEqual(_Hello.headers["Content-Type"], 'application/json; charset="utf-8"')

    # def testPost(self):
    #     response = self.testapp.post_json(b"/api/Relays/product1/serial1/module1", {"a": "b"})

    def testDict(self):
        xx = {"1": "2", "3": "4"}
        for x, y in xx.iteritems():
            print(x, y)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    import os

    if os.environ.get("APPENGINE_RUNTIME"):
        from google.appengine.ext.webapp.util import run_wsgi_app
        from google.appengine.ext.webapp import WSGIApplication

        wsgi_application = WSGIApplication(maps, debug=True)
        run_wsgi_app(wsgi_application)
    else:
        import unittest

        unittest.main()
