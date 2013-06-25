from __future__ import unicode_literals
import unittest

from google.appengine.ext import webapp
import simplejson

from model.DataNdb import Data
from api.Data.DataId import paths


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest
        #app = webapp2.WSGIApplication([map])
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        app = webapp.WSGIApplication(paths, debug=True)
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
        print(j)
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
    unittest.main()