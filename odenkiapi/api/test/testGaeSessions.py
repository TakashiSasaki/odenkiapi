from __future__ import unicode_literals, print_function
import unittest
import os

from google.appengine.ext import webapp, testbed
import simplejson
import webtest

import gaesessions


class GaeSession(webapp.RequestHandler):
    def get(self):
        current_session = gaesessions.get_current_session()
        if current_session.has_key("key1"):
            if current_session["key1"] == "value1":
                current_session["key1"] = "value2"
            elif current_session["key1"] == "value2":
                current_session["key1"] = "value3"
        else:
            current_session["key1"] = "value1"
        current_session.save()
        self.response.out.write(simplejson.dumps(["key1", current_session["key1"]]))


class TestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

        paths = [("/test/GaeSession", GaeSession)]
        wsgi_application = webapp.WSGIApplication(paths, debug=True)
        gaesessions_application = gaesessions.SessionMiddleware(wsgi_application, os.urandom(64))
        #self.cookie_jar = cookielib.CookieJar()
        self.testapp = webtest.TestApp(gaesessions_application)


    def tearDown(self):
        self.testbed.deactivate()

    def test(self):
        response1 = self.testapp.get("/test/GaeSession")
        #print(self.testapp.cookies)
        #print (response1.headers["Set-Cookie"])
        os.environ["HTTP_COOKIE"] = response1.headers["Set-Cookie"]
        self.assertEqual(["key1", "value1"], simplejson.loads(response1.body))
        #print(response1.body)
        response2 = self.testapp.get("/test/GaeSession")
        self.assertEqual(["key1", "value2"], simplejson.loads(response2.body))
        os.environ["HTTP_COOKIE"] = response2.headers["Set-Cookie"]
        #print(response2.body)
        response3 = self.testapp.get("/test/GaeSession")
        self.assertEqual(["key1", "value3"], simplejson.loads(response3.body))
        #print(response3.body)


if __name__ == "__main__":
    unittest.main()