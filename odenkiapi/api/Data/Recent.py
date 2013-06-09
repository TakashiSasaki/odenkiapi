from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
#from urlparse import urlparse
from model.DataNdb import Data
#from model.UnusedDataEliminator import UnusedDataEliminator
#from google.appengine.ext import ndb
#from logging import debug
#from google.appengine.ext.deferred import defer

class Recent(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            limit = int(jrequest.getValue("limit"))
        except:
            limit = 100
        jresponse.setExtraValue("limit", limit)
        query = Data.queryRecent()
        keys = query.fetch(keys_only=True, limit=limit)
        for k in keys:
            assert isinstance(k, ndb.Key)
            e = k.get()
            assert isinstance(e, Data)
            jresponse.addResult(e)

import UrlMap
UrlMap.UrlMap.append(("/api/Data/Recent", Recent))

if __name__ == "__main__":
    import unittest
    unittest.main()
