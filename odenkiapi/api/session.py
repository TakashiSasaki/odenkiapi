from __future__ import unicode_literals, print_function
from google.appengine.api.users import create_login_url, create_logout_url
from lib.gae import *
from gaesessions import get_current_session, Session, set_current_session
from lib.OdenkiSession import OdenkiSession

class UserInfo(JsonRpcDispatcher):
    
    def GET(self, json_rpc_request, json_rpc_response):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(json_rpc_response, JsonRpcResponse)
        json_rpc_response.setResultValue("gaesession", str(get_current_session()))
        json_rpc_response.setResultValue("OdenkiSession", OdenkiSession())

#        odenki_session = lib.OdenkiSession()
#        self.jsonRpc.setResultValule("sid", odenki_session.getSid())
#       odenki_user = odenki_session.getOdenkiUser()
#        if odenki_user:
#            self.jsonRpc.updateResult(odenki_user.getDictionary())
#        google_user = odenki_session.getGoogleUser()
#        if google_user:
#            self.jsonRpc.updateResult(google_user.getDictionary())
#        self.jsonRpc.write()
#        return

    def terminate(self, json_rpc_request, jresponse):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        json_rpc_response = JsonRpcResponse(json_rpc_request.getId())
        json_rpc_response.setResultValue("before", str(OdenkiSession().gaesession()))
        OdenkiSession().gaesession().terminate()
        json_rpc_response.setResultValue("after", str(OdenkiSession().gaesession()))

    @classmethod
    def _getLoginUrl(self):
        login_url = create_login_url("/api/session")
        return login_url
    
    @classmethod
    def _getLogoutUrl(self):
        logout_url = create_logout_url("/api/session")
        return logout_url

if __name__ == "__main__":
    url_map = []
    url_map.append(("/api/session", UserInfo))
    application = WSGIApplication(url_map)
    run_wsgi_app(application)