from google.appengine.ext import db
from google.appengine.ext.webapp import Request
import types,logging
from Counter import Counter

class Data(db.Model):
    dataId = db.IntegerProperty()
    name = db.StringProperty
    string = db.StringProperty()

def GetData(k,v):
    existing = Data.gql("WHERE name = :1 AND string = :2", k, v).get()
    if existing is not None:
        return existing
    data = Data()
    data.dataId = Counter.GetNextId("dataId")
    data.name = k
    data.string = v
    return data.put()
    
def GetDataList(request):
    assert isinstance(request, Request)
    data_list = []
    for k in request.arguments():
        vlist = request.get_all(k)
        logging.info((k,vlist))
        assert isinstance(vlist, list)
        for v in vlist:
            data = GetData(k,v)
            if data is None: continue
            data_list.append(data)
    return data_list
