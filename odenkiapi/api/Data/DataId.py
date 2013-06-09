from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data

class DataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            data_id = int(jrequest.getPathInfo()[3])
        except: return
        data_key = Data.getByDataId(data_id)
        if data_key is None:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "dataId %s not found" % data_id)
            return
        data = data_key.get()
        assert isinstance(data, Data)
        jresponse.addResult(data)
        jresponse.setExtraValue("key_id", data.key.id())

map = ("/api/Data/dataId/[0-9]+", DataId)
import UrlMap
UrlMap.UrlMap.append(map)

import unittest
class _TestCase(unittest.TestCase):
    def setUp(self):
        import webapp2, webtest
        #app = webapp2.WSGIApplication([map])
        import google.appengine.ext.webapp
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        from google.appengine.ext import webapp
        app = webapp.WSGIApplication([map], debug=True)
        self.testapp = webtest.TestApp(app)
        from google.appengine.ext import testbed
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def test(self):
        d = Data.prepare("f1", "s1")
        data_id = d.dataId
        self.assertEqual(data_id, 1)
        response = self.testapp.get(b"/api/Data/dataId/%s" % data_id)
        print (response)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    import unittest
    unittest.main()
