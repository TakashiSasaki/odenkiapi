from gaesessions import get_current_session, Session, set_current_session
from logging import getLogger, debug, DEBUG
from GoogleUser import GoogleUser
from OdenkiUser import getOdenkiUser, OdenkiUser
getLogger().setLevel(DEBUG)

class NoOdenkiId(BaseException):
    pass

class OdenkiSession(object):
    __slot__=["session"]
    def __init__(self):
        try:
            self.session = get_current_session()
        except:
            self.session = Session()
            self.session.start()
        if self.session.is_active():
            assert isinstance(self.session.sid, str)
        else:
            self.session.start()
            assert isinstance(self.session.sid, str) 

    def getSid(self):
        assert isinstance(self.session.sid, str) 
        return self.session.sid

    def revoke(self):
        self.deleteGoogleUser()
        self.deleteOdenkiUser()


    def setGoogleUser(self, google_user):
        assert isinstance(google_user, GoogleUser)
        self.session["googleUser"] = google_user
        if self.getOdenkiUser() is None:
            odenki_user = google_user.getOdenkiUser()
            self.setOdenkiUser(odenki_user)
        
    def getGoogleUser(self):
        try:
            google_user = self.session["googleUser"]
            return google_user
        except KeyError:
            return None
    
    def deleteGoogleUser(self):
        try:
            self.session["googleUser"] = None
        except KeyError:
            pass
    
    def getOdenkiUser(self):
        try:
            return self.session["odenkiUser"]
        except KeyError:
            return None
    
    def deleteOdenkiUser(self):
        try:
            self.session["odenkiUser"] = None
        except KeyError:
            pass
        
    def getCanonicalOdenkiId(self):
        odenki_user = self.getOdenkiUser()
        assert isinstance(odenki_user, OdenkiUser)
        return odenki_user.getOdenkiId()
    
    def setOdenkiUser(self, odenki_user):
        assert isinstance(odenki_user, OdenkiUser)
        try:
            assert self.session["odenkiUser"] is None
        except KeyError:
            pass
        self.session["odenkiUser"] = odenki_user
        
