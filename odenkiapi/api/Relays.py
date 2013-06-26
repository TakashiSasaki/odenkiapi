# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
#import json as simplejson
from google.appengine.ext import webapp
from lib.gae import JsonRpcDispatcher
#from lib.json import JsonRpcRequest, JsonRpcResponse
from model.Hems import Relays
from lib.json.JsonRpcResponse import JsonRpcResponse
from lib.json.JsonRpcRequest import JsonRpcRequest


class _Index(webapp.RequestHandler):
    def get(self):
        html = """
<html>
<head><title>Relays</title></head><body>
<form method="POST">
    <p>productName<input type="text" name="productName"/></p>
    <p>serialNumber<input type="text" name="serialNumber"/></p>
    <p>moduleId<input type="text" name="moduleId" /></p>
    <p>relayId<input type="text" name="relayId" /></p>
    <p>scheduledDateTime<input type="text" name="scheduledDateTime" /></p>
    <p>expectedState<input type="text" name="expectedState" /></p>
</form>
</body></html>"""
        self.response.out.write(html)


class _Relays(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)

        relays = Relays(product_name, serial_number, module_id)
        jresponse.addResult(relays)

    def POST(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        product_name = jrequest.getPathInfo(3)
        serial_number = jrequest.getPathInfo(4)
        module_id = jrequest.getPathInfo(5)
        #self.response.headers.add_header(b"Set-Cookie", b"productName=%s" % product_name.encode())
        #self.response.headers.add_header(b"Set-Cookie", b"serialNumber=%s" % serial_number.encode())
        #self.response.headers.add_header(b"Set-Cookie", b"moduleId=%s" % module_id.encode())

        relays = Relays(product_name, serial_number, module_id)
        assert isinstance(relays, Relays)
        for relay in jrequest.list:
            relays.setExpectedState(relay["relayId"], relay["scheduledDateTime"], relay["expectedState"])
        if jrequest.dict:
            if isinstance(jrequest.dict["relayId"], list) and len(jrequest.dict["relayId"]) == 1:
                relay_id = jrequest.dict["relayId"][0]
            else:
                relay_id = jrequest.dict["relayId"]
            if isinstance(jrequest.dict["scheduledDateTime"], list) and len(jrequest.dict["scheduledDateTime"]) == 1:
                scheduled_date_time = jrequest.dict["scheduledDateTime"][0]
            else:
                scheduled_date_time = jrequest.dict["scheduledDateTime"]
            if isinstance(jrequest.dict["expectedState"], list) and len(jrequest.dict["expectedState"]) == 1:
                expected_state = jrequest.dict["expectedState"][0]
            else:
                expected_state = jrequest.dict["expectedState"]
            relays.setExpectedState(relay_id, scheduled_date_time, expected_state)
            assert isinstance(jrequest.request, webapp.Request)

        relays = Relays(product_name, serial_number, module_id)
        assert isinstance(relays, dict)
        l = []
        for k, v in relays.iteritems():
            l.append(v)
        jresponse.addResult(l)


paths = [("/api/Relays/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+/[0-9a-zA-Z_]+", _Relays),
         ("/api/Relays/", _Index)]

if __name__ == "__main__":
    import os

    if os.environ.get("APPENGINE_RUNTIME"):
        from google.appengine.ext.webapp.util import run_wsgi_app
        from google.appengine.ext.webapp import WSGIApplication

        wsgi_application = WSGIApplication(maps, debug=True)
        run_wsgi_app(wsgi_application)
    else:
        import unittest

        unittest.main()
