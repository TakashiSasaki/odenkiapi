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


map = ("/api/Relays/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+", _Relays)

import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest

        app = webapp.WSGIApplication([map], debug=True)
        self.testapp = webtest.TestApp(app)
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def testSucceeded(self):
        response = self.testapp.get("/api/Relays/product1/serial1/module1")
        print(response.body)
        j = simplejson.loads(response.body)


    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    import unittest

    unittest.main()
