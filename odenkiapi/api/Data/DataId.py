from __future__ import unicode_literals, print_function
import simplejson
from google.appengine.ext import webapp
#import  webapp2
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data


class DataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            data_id_string = jrequest.getPathInfo(4)
            data_id = int(data_id_string)
        except:
            return
        try:
            data = Data.getByDataId(data_id)
        except:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "dataId %s not found" % data_id)
            return
            #data = data_key.get()
        assert isinstance(data, Data)
        jresponse.addResult(data)
        jresponse.setExtraValue("key_id", data.key.id())


map = ("/api/Data/dataId/[0-9]+", DataId)

import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest
        #app = webapp2.WSGIApplication([map])
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        app = webapp.WSGIApplication([map], debug=True)
        self.testapp = webtest.TestApp(app)
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def testSucceeded(self):
        d = Data.prepare("f1", "s1")
        data_id = d.dataId
        self.assertEqual(data_id, 1)
        response = self.testapp.get("/api/Data/dataId/%s" % data_id)
        j = simplejson.loads(response.body)
        self.assertEqual(j["result"][0]["field"], "f1")
        self.assertEqual(j["result"][0]["string"], "s1")
        self.assertEqual(j["result"][0]["dataId"], 1)

    def testFailed(self):
        d = Data.prepare("f1", "s1")
        data_id = d.dataId
        self.assertEqual(data_id, 1)
        response = self.testapp.get("/api/Data/dataId/%s" % (data_id + 1), status=500)
        json_object = simplejson.loads(response.body)
        self.assertEqual(json_object["error"]["code"], -32099)
        self.assertIsNone(json_object["error"]["data"])
        self.assertIsNone(json_object["error"]["name"])

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    import unittest

    unittest.main()
