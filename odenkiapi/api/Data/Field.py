from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.DataNdb import Data


class Field(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            field = unicode(jrequest.getPathInfo(3))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        data_keys = Data.fetchByField(field)
        jresponse.setResult([])
        for data_key in data_keys:
            data = data_key.get()
            jresponse.addResult(data)


map = ("/api/Data/[^/]+", Field)

import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest
        from google.appengine.ext import webapp
        #app = webapp2.WSGIApplication([map])
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        wsgi_application = webapp.WSGIApplication([map], debug=True)
        self.testapp = webtest.TestApp(wsgi_application)

        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.data1 = Data.prepare("f1", "s1")
        self.data1 = Data.prepare("f1", "s11")
        self.data2 = Data.prepare("f2", "s2")

    def testSucceeded(self):
        response = self.testapp.get("/api/Data/f1")
        import simplejson

        json_object = simplejson.loads(response.body)
        self.assertEqual(json_object["result"][0]["field"], "f1")
        self.assertEqual(json_object["result"][0]["string"], "s1")
        self.assertEqual(json_object["result"][0]["dataId"], 1)
        self.assertEqual(json_object["result"][1]["field"], "f1")
        self.assertEqual(json_object["result"][1]["string"], "s11")
        self.assertEqual(json_object["result"][1]["dataId"], 2)

    def testFailed(self):
        response = self.testapp.get("/api/Data/f3")
        import simplejson

        json_object = simplejson.loads(response.body)
        self.assertIsInstance(json_object["result"], list)
        self.assertEqual(len(json_object["result"]), 0)

    def tearDown(self):
        keys = Data.query().fetch(keys_only=True)
        for key in keys:
            key.delete_async()
        self.testbed.deactivate()


if __name__ == "__main__":
    import unittest

    unittest.main()
