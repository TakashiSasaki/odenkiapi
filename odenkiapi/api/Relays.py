from __future__ import unicode_literals, print_function
import simplejson
from google.appengine.ext import webapp
#import  webapp2
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.Hems import Relays


class _Relays(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)

        relays = Relays(product_name, serial_number, module_id)
        jresponse.addResult(relays)

    def POST(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)

        relays = Relays(product_name, serial_number, module_id)
        assert isinstance(jrequest.request, webapp.Request)
        #json_object = simplejson.loads(jrequest.)

        jresponse.addResult(relays)


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


map = ("/api/Relays/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+", _Relays)

import unittest
import datetime


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest

        app = webapp.WSGIApplication([map, ("/hello", _Hello)], debug=True)
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

    def testGet(self):
        response = self.testapp.get("/hello?a=b&a=c")
        self.assertEqual(_Hello.body, "")
        self.assertEqual(_Hello.arguments, ["a"])
        self.assertEqual(_Hello.headers["Content-Type"], '; charset="utf-8"')

    def testPost(self):
        response = self.testapp.post(b"/hello?v=b&a=z", {"c": "d"})
        self.assertEqual(_Hello.body, "c=d")
        self.assertEqual(_Hello.arguments, ["a", "c", "v"])
        self.assertEqual(_Hello.headers["Content-Type"], 'application/x-www-form-urlencoded; charset="utf-8"')

    def testPostJson(self):
        response = self.testapp.post_json(b"/hello?v=b&a=z", {"c": "d"})
        self.assertEqual(_Hello.body, '{"c": "d"}')
        self.assertEqual(_Hello.arguments, ["a", "v"])
        self.assertEqual(_Hello.headers["Content-Type"], 'application/json; charset="utf-8"')

    # def testPost(self):
    #     response = self.testapp.post_json(b"/api/Relays/product1/serial1/module1", {"a": "b"})

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    import unittest

    unittest.main()
