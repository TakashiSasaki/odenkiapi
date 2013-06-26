from __future__ import unicode_literals, print_function
import unittest
import os

from google.appengine.ext import testbed, webapp
import webtest
import simplejson

import gaesessions
import api.OdenkiUser
import model.OdenkiUser


class TestCase(unittest.TestCase):
    __slots__ = ["testbed"]

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        wsgi_application = webapp.WSGIApplication(api.OdenkiUser.paths, debug=True)
        gaesessions_application = gaesessions.SessionMiddleware(wsgi_application, os.urandom(64))
        #self.cookie_jar = cookielib.CookieJar()
        self.testapp = webtest.TestApp(gaesessions_application)

    def get(self, path):
        response = self.testapp.get(path)
        if response.headers.has_key("Set-Cookie"):
            os.environ["HTTP_COOKIE"] = response.headers["Set-Cookie"]
        return response

    def post(self, path, params=""):
        response = self.testapp.post(path, params)
        if response.headers.has_key("Set-Cookie"):
            os.environ["HTTP_COOKIE"] = response.headers["Set-Cookie"]
        return response

    def tearDown(self):
        self.testbed.deactivate()

    def test(self):
        response = self.get(b"/api/OdenkiUser?method=create&odenkiName=odenki1")
        json_object = simplejson.loads(response.body)
        odenki_id = json_object["result"][0]["odenkiId"]
        self.assertEqual(odenki_id, 1)
        odenki_user = model.OdenkiUser.OdenkiUser.getByOdenkiId(odenki_id)
        self.assertIsInstance(odenki_user, model.OdenkiUser.OdenkiUser)

        response = self.post(b"/api/OdenkiUser/CurrentOdenkiId", {"odenkiId": odenki_id})
        json_object = simplejson.loads(response.body)
        self.assertEqual(1, json_object["result"]["odenkiId"])
        response = self.get(b"/api/OdenkiUser/CurrentOdenkiId")
        json_object = simplejson.loads(response.body)
        self.assertEqual(1, json_object["result"]["odenkiId"])


if __name__ == "__main__":
    unittest.main()