import unittest
from google.appengine.ext import webapp

class Hello(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("hello")

from lib.gae import JsonRpcDispatcher
class Hello2(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        self.response.out.write("hello2")

class _TestCase(unittest.TestCase):
    def setUp(self):
        import webapp2, webtest
        #app = webapp2.WSGIApplication([map])
        import google.appengine.ext.webapp
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        from google.appengine.ext import webapp
        app = webapp.WSGIApplication( [("/hello", Hello), ("/hello2", Hello2)], debug=True)
        self.testapp = webtest.TestApp(app)

    def testHello(self):
        response = self.testapp.get("/hello")
        self.assertEqual(response.body, "hello")

    def testHello2(self):
        response = self.testapp.get("/hello2")
        self.assertEqual(response.body, "hello2")

if __name__ == "__main__":
    unittest.main()
