from __future__ import unicode_literals
from urlparse import urlparse

from google.appengine.ext import webapp


class _Path(webapp.RequestHandler):
    def get(self):
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.path)


class _Params(webapp.RequestHandler):
    def get(self):
        assert isinstance(self.request, webapp.Request)
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.params)
        self.response.headers["a"] = "abc"


class _Query(webapp.RequestHandler):
    def get(self):
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.query)


class _Fragment(webapp.RequestHandler):
    def get(self):
        parsed_url = urlparse(self.request.url)
        self.response.out.write(parsed_url.fragment)


class _Body(webapp.RequestHandler):
    def get(self):
        self.response.out.write(self.request.body)


paths = [('/_Path', _Path),
         ('/_Params.*', _Params),
         ('/_Query', _Query),
         ('/_Fragment', _Fragment),
         ('/_Body', _Body)]

import unittest


class _MyTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        try:
            import webtest
        except ImportError:
            import setuptools.command.easy_install as easy_install

            easy_install.main(["WebTest"])
            exit()
        wsgi_application = webapp.WSGIApplication(paths)
        self.test_app = webtest.TestApp(wsgi_application)
        from google.appengine.ext.testbed import Testbed

        self.testbed = Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()
        unittest.TestCase.tearDown(self)


    def test_Path(self):
        response = self.test_app.get("/_Path")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, '/_Path')

    def test_Params(self):
        response = self.test_app.request(b"/_Params;ppp?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.headers["a"], "abc")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "")

    def test_Fragment(self):
        response = self.test_app.request(b"/_Fragment?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "e")

    def test_Query(self):
        response = self.test_app.request(b"/_Query?a=b&c=d#e", method=b"GET")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.headers["Content-Type"], 'text/html; charset=utf-8')
        self.assertEqual(response.body, "a=b&c=d")


class _TestSemicolonInUrl(unittest.TestCase):
    def testUrlParse(self):
        """urlparse.urlparse recognizes the semicolon in the given path for http scheme."""
        self.assertEqual(urlparse("http://localhost/a/b/c;d").params, "d")
        self.assertEqual(urlparse("file://localhost/a/b/c;d").params, "")
        self.assertEqual(urlparse("file:///a/b/c;d").params, "")

    def testWebobRequest(self):
        """It shows a simple usage of WebOb Request class to create a blank request."""
        import webob

        request = webob.Request.blank("/a/b/c")
        self.assertEqual(request.url, "http://localhost/a/b/c")

    def testWebobRequestSemicolon(self):
        """The semicolon in the given path is URL-encoded UNEXPECTEDLY."""
        import webob

        request = webob.Request.blank("/a/b/c;d")
        self.assertEqual(request.url, "http://localhost/a/b/c%3Bd")


if __name__ == "__main__":
    unittest.main()
