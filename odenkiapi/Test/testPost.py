from __future__ import unicode_literals, print_function
import unittest
import json

import post
from model.DataNdb import Data


class _TestCase(unittest.TestCase):
    __slots__ = ["testapp"]

    def setUp(self):
        import webtest
        from google.appengine.ext import webapp
        #app = webapp2.WSGIApplication([map])
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        wsgi_application = webapp.WSGIApplication(post.paths, debug=True)
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
        keys = Data.fetchByField("a")
        self.assertEqual(len(keys), 0)
        response = self.testapp.get("/post?a=bb&c=dd&a=x")
        self.assertEqual(json.loads(response.body), [[4, "a", "bb"], [5, "a", "x"], [6, "c", "dd"]])
        keys = Data.fetchByField("a")
        self.assertEqual(len(keys), 2)
        self.assertTrue(keys[0].get().field == "a")
        self.assertTrue(keys[1].get().field == "a")
        self.assertTrue(keys[0].get().string in ["bb", "x"])
        self.assertTrue(keys[1].get().string in ["bb", "x"])


        #json_object = simplejson.loads(response.body)
        # self.assertEqual(json_object["result"].__len__(), 1)
        # self.assertEqual(json_object["result"][0]["field"], "f1")
        # self.assertEqual(json_object["result"][0]["string"], "s1")
        # self.assertEqual(json_object["result"][0]["dataId"], 1)
        #self.assertEqual(json_object["result"][1]["field"], "f1")
        #self.assertEqual(json_object["result"][1]["string"], "s11")
        #self.assertEqual(json_object["result"][1]["dataId"], 2)

    def _testFailed(self):
        response = self.testapp.get("/api/Data/f3/s2", status=500)

        # json_object = simplejson.loads(response.body)
        # self.assertEqual(json_object["error"]["code"], EntityNotFound.code)

    def tearDown(self):
        keys = Data.query().fetch(keys_only=True)
        for key in keys:
            key.delete_async()
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()
