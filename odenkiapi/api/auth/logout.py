#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.OdenkiUser import OdenkiUser
#from google.appengine.ext import ndb
from lib.gae import run_wsgi_app
#from logging import debug
#from lib.json import JsonRpcError
from lib.json.JsonRpcError import InvalidParams, EntityNotFound

class LogoutHandler(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound:
            jresponse.addResult("not logged in")
            return
        assert isinstance(odenki_user, OdenkiUser)
        jresponse.addResult("logged out")
        jresponse.addResult(odenki_user)
        OdenkiUser.deleteFromSession()

if __name__ == "__main__":
    #print ("\u30e6\u30fc\u30b6\u30fc\uff11")
    mapping = []
    mapping.append(("/api/auth/logout", LogoutHandler))
    run_wsgi_app(mapping)
