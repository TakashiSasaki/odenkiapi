import logging
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import WSGIApplication, RequestHandler
from google.appengine.api import users
from gdata.gauth import OAuthHmacToken
from gdata.docs.client import DocsClient
from gdata.spreadsheets.client import SpreadsheetsClient
from gdata.docs.data import ResourceFeed, Resource
from credentials import GOOGLE_OAUTH_CONSUMER_KEY, GOOGLE_OAUTH_CONSUMER_SECRET
from gdata.gauth import AeSave, AeLoad, AuthorizeRequestToken, AeDelete
from gdata.client import Unauthorized

GOOGLE_OAUTH_SCOPES = ['https://docs.google.com/feeds/',
                       'https://www.google.com/calendar/feeds/',
                       'https://spreadsheets.google.com/feeds/']

def saveRequestToken(request_token):
    #odenki_user = getCurrentUser()
    google_user = users.get_current_user()
    AeSave(request_token, str(google_user.user_id()) + "RequestToken")

def loadRequestToken():
    google_user = users.get_current_user()
    return AeLoad(str(google_user.user_id()) + "RequestToken")

def deleteRequestToken():
    google_user = users.get_current_user()
    return AeDelete(str(google_user.user_id()) + "RequestToken")

def saveAccessToken(access_token):
    google_user = users.get_current_user()
    logging.debug("Saving access token " + access_token.token)
    AeSave(access_token, str(google_user.user_id()) + "AccessToken")

def loadAccessToken():
    google_user = users.get_current_user()
    keystring = str(google_user.user_id()) + "AccessToken"
    logging.debug("Loading access token by keystring " + keystring)
    access_token = AeLoad(keystring)
    if access_token is None:
        logging.debug("Loading access token failed")
    else: 
        logging.debug("Loading access token succeeded")
    return access_token

def deleteAccessToken():
    google_user = users.get_current_user()
    return AeDelete(str(google_user.user_id()) + "AccessToken")

def getDocsClient():
    client = DocsClient(source='odenkiapi')
    access_token = loadAccessToken()
    if access_token is not None: 
        client.auth_token = access_token
    return client

def getSpreadsheetsClient():
    client = SpreadsheetsClient(source='odenkiapi')
    access_token = loadAccessToken()
    if access_token is not None: 
        assert isinstance(access_token, OAuthHmacToken)
        client.auth_token = access_token
    return client

def getResources():
    client = getDocsClient()
    assert isinstance(client, DocsClient)
    resource_feed =  client.get_resources(show_root = True)
    return resource_feed

class _RequestHandler(RequestHandler):
    def get(self):
        google_user = users.get_current_user()
        if google_user is None:
            self.redirect(users.create_login_url("/OdenkiUser"))
            return
        
        if self.request.get("revoke"):
            deleteAccessToken()
            deleteRequestToken()
            self.redirect("/OdenkiUser")
            return
        
        if loadRequestToken() is None:
            gdata_client = getDocsClient() 
            request_token = gdata_client.GetOAuthToken(
                GOOGLE_OAUTH_SCOPES,
                'http://%s/GoogleDocs' % self.request.host,
                GOOGLE_OAUTH_CONSUMER_KEY,
                consumer_secret=GOOGLE_OAUTH_CONSUMER_SECRET)
            assert isinstance(request_token, OAuthHmacToken)
            saveRequestToken(request_token)
            logging.debug("authorizing request token " + str(request_token.generate_authorization_url(google_apps_domain=None)))
            self.redirect(request_token.generate_authorization_url().__str__())
            return
        
        if loadAccessToken() is None:
            request_token = loadRequestToken()
            logging.debug("Getting access token by request token :" + str(request_token.token))
            assert isinstance(request_token, OAuthHmacToken)
            authorized_request_token = AuthorizeRequestToken(request_token, self.request.url)
            assert isinstance(authorized_request_token, OAuthHmacToken)
            gdata_client = getDocsClient()
            try:
                access_token = gdata_client.GetAccessToken(authorized_request_token)
                assert isinstance(access_token, OAuthHmacToken)
                saveAccessToken(access_token)
            except Exception, e:
                logging.debug("Can't get access token. " + e.message)
                deleteAccessToken()
                deleteRequestToken()
                self.redirect("/OdenkiUser")
                return

        assert loadAccessToken() is not None
        try:
            resource_feed = getResources()
            assert isinstance(resource_feed, ResourceFeed)
        except Unauthorized, e:
            deleteRequestToken()
            deleteAccessToken()
            self.redirect("/GoogleDocs")
            return
            
        self.redirect("/OdenkiUser")
        return
            
        
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    application = WSGIApplication([('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler),
                                   ('/GoogleDocs', _RequestHandler)], debug=True)
    run_wsgi_app(application)
