from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data
from google.appengine.ext import ndb

class KeyId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            key_id = int(jrequest.getPathInfo()[4])
        except: return
        data_key = ndb.Key(Data, key_id)
        jresponse.addResult(data_key.get())
        jresponse.setExtraValue("key_id", key_id)

import UrlMap
UrlMap.UrlMap.append(("/api/Data/keyId/[0-9]+", KeyId))

if __name__ == "__main__":
    import unittest
    unittest.main()
