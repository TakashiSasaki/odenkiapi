import unittest
from google.appengine.ext import webapp
from lib.json.JsonRpcResponse import JsonRpcResponse


class Hello(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write("hello")


from lib.gae import JsonRpcDispatcher


class Hello2(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        jresponse.setResultValue("message", "hello2")
        #self.response.out.write("hello2")


class _TestCase(unittest.TestCase):
    def setUp(self):
        import webtest
        #app = webapp2.WSGIApplication([map])
        #from lib.gae import run_wsgi_app
        #app = run_wsgi_app(UrlMap.UrlMap)
        from google.appengine.ext import webapp

        app = webapp.WSGIApplication([("/hello", Hello), ("/hello2", Hello2)], debug=True)
        self.testapp = webtest.TestApp(app)

    def testHello(self):
        response = self.testapp.get("/hello")
        self.assertEqual(response.body, "hello")

    def testHello2(self):
        response = self.testapp.get("/hello2")
        import simplejson

        j = simplejson.loads(response.body)
        self.assertIsNotNone(j["id"])
        self.assertEqual(j["result"]["message"], "hello2")


if __name__ == "__main__":
    unittest.main()
