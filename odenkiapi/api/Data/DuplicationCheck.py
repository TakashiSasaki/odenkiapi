from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data, getCanonicalData
from google.appengine.ext import ndb

class _DuplicationCheck(JsonRpcDispatcher):
    
    def GET(self, jrequest, jresponse):
        LIMIT = 100
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getValue("start")[0])
            end = int(jrequest.getValue("end")[0])
        except:
            jresponse.setError(JsonRpcError.INVALID_PARAMS, "start and end are mandatory")
            return
        query = Data.queryRange(start, end)
        keys = query.fetch(keys_only=True, limit=LIMIT)
        for key in keys:
            data = key.get()
            assert isinstance(data, Data)
            query_for_duplicated_data = data.queryDuplication()
            assert isinstance(query_for_duplicated_data, ndb.Query)
            keys_for_duplicated_data = query_for_duplicated_data.fetch(keys_only=True)
            if len(keys_for_duplicated_data) <= 1: continue
            jresponse.addResult([data.dataId, data.field, data.string, getCanonicalData(key).get().dataId])
        jresponse.setExtraValue("limit", LIMIT)

import UrlMap
UrlMap.UrlMap.append(("/api/Data/duplicated", _DuplicationCheck))

if __name__ == "__main__":
    import unittest
    unittest.main()

