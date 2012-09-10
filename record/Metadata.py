from lib.JsonRpc import JsonRpcDispatcher, JsonRpcResponse, JsonRpcRequest, \
    JsonRpcError
from model.MetadataNdb import Metadata
from model.DataNdb import Data, getCanonicalizedKey, canonicalizeKeyList
from datetime import datetime, timedelta

class _Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        query = Metadata.queryRecent()
        keys = query.fetch(keys_only=True)
        for key in keys:
            metadata = key.get()
            assert isinstance(metadata, Metadata)
            jresponse.addResult(metadata.getFields())
    
class _Range(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        pass
    

class _CleanData(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getValue("start")[0])
            end = int(jrequest.getValue("end")[0])
        except Exception, e:
            jresponse.setError(JsonRpcError.INVALID_PARAMS, unicode(e.__class__) + unicode(e))
            return
        query = Metadata.queryRange(start, end)
        keys = query.fetch(keys_only=True)
        #assert len(keys) == abs(start - end) + 1
        for key in keys:
            metadata = key.get()
            assert isinstance(metadata, Metadata)
            data_list = metadata.dataList
            if not isinstance(data_list, list): continue
            canonicalized_list = canonicalizeKeyList(data_list)
            assert len(canonicalized_list) == len(data_list)
            for i in range(len(canonicalized_list)):
                assert canonicalized_list[i].get().field == data_list[i].get().field
                assert canonicalized_list[i].get().string == data_list[i].get().string
            metadata.dataList = canonicalized_list
            metadata.put_async()
            jresponse.addResult([metadata.metadataId, data_list, canonicalized_list])
            
class _OneDay(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = jrequest.getPathInfo()
        try:
            year = int(path_info[3])
            month = int(path_info[4])
            day = int(path_info[5])
        except:
            year = 2012
            month = 8
            day = 20
        start = datetime(year=year, month=month, day=day)
        end = start + timedelta(days=1)
        query = Metadata.queryDateRange(start, end)
        keys = query.fetch(limit=24*60+100, keys_only=True)
        for key in keys:
            jresponse.addResult(key.get().to_list())

if __name__ == "__main__":
    mapping = []
    mapping.append(("/record/Metadata", _Recent))
    mapping.append(("/record/Metadata/[0-9]+/[0-9]+", _Range))
    mapping.append(("/record/Metadata/[0-9]+/[0-9]+/[0-9]+", _OneDay))
    mapping.append(("/record/Metadata/CleanData", _CleanData))
    from google.appengine.ext.webapp import WSGIApplication
    application = WSGIApplication(mapping, debug=True)
    from google.appengine.ext.webapp.util import run_wsgi_app
    run_wsgi_app(application)
