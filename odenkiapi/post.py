from __future__ import unicode_literals, print_function

from google.appengine.ext import db
from google.appengine.ext import webapp

from lib.json import dumps
from model.Sender import GetSender
from model.RawData import putRawData
from model.Data import Data
from model.Metadata import putMetadata
from model import RawDataNdb
from model.Hems import Relays, Relay, nativeToEpoch


class PostPage(webapp.RequestHandler):
    __slots__ = ["productName", "serialNumber", "moduleId"]

    def get(self):
        self.sender = GetSender(self.request)
        self.raw_data = putRawData(self.request)
        # self.data_list = putDataList(self.request)
        self.data_list = Data.storeRequest(self.request)
        self.metadata = putMetadata(self.sender, self.raw_data, self.data_list)

        assert isinstance(self.response, webapp.Response)
        self.response.headers['Content-Type'] = "text/plain"
        for key in self.data_list:
            data = db.get(key)
            if data.field == "productName":
                self.productName = data.string
            if data.field == "serialNumber":
                self.serialNumber = data.string
            if data.field == "moduleId":
                self.moduleId = data.string

                #self.response.out.write("field:" + data.field + " string:" + data.string + "\n")

        try:
            relays = Relays(self.productName, self.serialNumber, self.moduleId)
            assert isinstance(relays, Relays)
            l = []
            for k, v in relays.iteritems():
                assert isinstance(v, Relay)
                r = {
                    "relayId": v.relayId,
                    #"scheduledDateTime" : v.scheduledDateTime,
                    "scheduledEpoch": nativeToEpoch(v.scheduledDateTime),
                    "expectedState": v.expectedState
                }
                l.append(r)

            o = {
                "relayStates": l
            }

            self.response.out.write(dumps(o))
        except AttributeError, e:
            l = map(lambda key: db.get(key), self.data_list)
            j = dumps(l)
            self.response.out.write(j)

    def post(self):
        # logging.info("body="+self.request.body)
        self.get()


class _GetLastPostedRawDataHandler(webapp.RequestHandler):
    def get(self):
        raw_data = RawDataNdb.RawData.getLast()
        self.response.out.write(raw_data)


paths = [("/post", PostPage)]

#from google.appengine.ext.webapp import WSGIApplication


if __name__ == "__main__":
    wsgi_application = webapp.WSGIApplication(paths, debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app

    run_wsgi_app(wsgi_application)

