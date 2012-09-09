from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse
from model.RawDataNdb import RawData
#from google.appengine.ext import ndb

class _Range(JsonRpcDispatcher):
#    @ndb.toplevel
#    def get(self):
#        path_info = self.request.path_info.split("/")
#        start = int(path_info[3])
#        end = int(path_info[4])
#        q = RawData.queryPeriod(start, end)
#        
#        for raw_data_key in q.fetch(keys_only=True):
#            self.response.out.write(str(raw_data_key.get()))
            
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])
        query = RawData.queryRange(start, end)
        keys = query.fetch(keys_only=True, limit=100)
        for key in keys:
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)
        
class _Recent(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        try:
            limit = int(jrequest["params"]["limit"])
        except:
            limit = 1000
        jresponse.setId()
        query = RawData.queryRecent()
        keys = query.fetch(keys_only=True, limit=limit)
        for key in keys:
            raw_data = key.get()
            assert isinstance(raw_data, RawData)
            jresponse.addResult(raw_data)

if __name__ == "__main__":
    mapping = []
    mapping.append(('/record/RawData/[0-9]+/[0-9]+', _Range))
    mapping.append(('/record/RawData', _Recent))
    from lib import WSGIApplication
    application = WSGIApplication(mapping)
    from lib import run_wsgi_app
    run_wsgi_app(application)
