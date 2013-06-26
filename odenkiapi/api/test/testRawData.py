from __future__ import unicode_literals, print_function
import unittest
import webtest
import simplejson

from google.appengine.ext import webapp
from google.appengine.ext import testbed

import api.RawData
import post


class Recent(unittest.TestCase):
    def setUp(self):
        paths = []
        paths.extend(api.RawData.paths)
        paths.extend(post.paths)
        wsgi_application = webapp.WSGIApplication(paths, debug=True)

        self.testapp = webtest.TestApp(wsgi_application)

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        self.testapp.get("/post?a=b&c=d")
        self.testapp.get("/post?x=y&z=w")

    def tearDown(self):
        self.testbed.deactivate()

    def test(self):
        response = self.testapp.get("/api/RawData")
        json_object = simplejson.loads(response.body)
        self.assertEqual(json_object["result"][1]["query"], "a=b&c=d")
        self.assertEqual(json_object["result"][0]["query"], "x=y&z=w")


if __name__ == "__main__":
    unittest.main()
