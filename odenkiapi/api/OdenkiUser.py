#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from lib.gae.JsonRpcDispatcher import JsonRpcDispatcher
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from model.OdenkiUser import OdenkiUser
from lib.json.JsonRpcError import InvalidParams, EntityNotFound


class OdenkiUserApi(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()

        #query = ndb.Query(kind="OdenkiUser")
        #query = query.order(-OdenkiUser.odenkiId)
        #keys = query.fetch(limit=100, keys_only=True)
        #for key in keys:
        #    jresponse.addResult(key.get())

        odenki_user = OdenkiUser.loadFromSession()
        if odenki_user is not None:
            assert isinstance(odenki_user, OdenkiUser)
            jresponse.setResultObject(odenki_user)

    def create(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)

        odenki_name = jrequest.request.get("odenkiName")
        odenki_name = odenki_name.decode()
        if odenki_name is None or len(odenki_name) == 0:
            raise InvalidParams("odenkiName is mandatory.")

        odenki_user = OdenkiUser.createNew()
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.odenkiName = odenki_name
        odenki_user.put()
        jresponse.addResult(odenki_user)
        jresponse.setId()

    def login(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        import gaesessions

        session = gaesessions.get_current_session()
        assert isinstance(session, gaesessions.Session)
        odenki_id = jrequest.request.get("odenkiId")
        odenki_id = int(odenki_id)
        odenki_user = OdenkiUser.getByOdenkiId(odenki_id)
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.saveToSession()
        jresponse.addResult(odenki_user)

    def logout(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            odenki_user = OdenkiUser.loadFromSession()
        except EntityNotFound, e:
            jresponse.addResult("not logged in")
            return
        assert isinstance(odenki_user, OdenkiUser)
        jresponse.addResult("logged out")
        jresponse.addResult(odenki_user)
        OdenkiUser.deleteFromSession()


class SetOdenkiName(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        try:
            new_odenki_name = jrequest.getValue("odenkiName")[0]
            assert isinstance(new_odenki_name, unicode)
        except:
            raise InvalidParams("SetOdenkiName requires odenkiName")
        odenki_user.setOdenkiName(new_odenki_name)
        odenki_user.saveToSession()

        jresponse.setResult(odenki_user)


class CurrentOdenkiId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        jresponse.setId()
        odenki_user = OdenkiUser.loadFromSession()
        jresponse.setResult(odenki_user)

    def POST(self, jrequest, jresponse):
        jresponse.setId()
        odenki_id = int(jrequest.getValue("odenkiId")[0])
        try:
            odenki_user = OdenkiUser.getByOdenkiId(odenki_id)
        except EntityNotFound, e:
            odenki_user = OdenkiUser.createNew()
        assert isinstance(odenki_user, OdenkiUser)
        odenki_user.saveToSession()
        jresponse.setResult(odenki_user)


paths = [("/api/OdenkiUser/SetOdenkiName", SetOdenkiName),
         ("/api/OdenkiUser", OdenkiUserApi),
         ("/api/OdenkiUser/CurrentOdenkiId", CurrentOdenkiId)]

if __name__ == "__main__":
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp.util import run_wsgi_app
    import gaesessions

    wsgi_application = webapp.WSGIApplication(paths, debug=True)
    import credentials

    gaesessions_application = gaesessions.SessionMiddleware(wsgi_application, credentials.SESSION_SALT)

    run_wsgi_app(gaesessions_application)