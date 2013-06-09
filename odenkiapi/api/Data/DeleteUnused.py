from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data
from google.appengine.ext import ndb
from model.UnusedDataEliminator import UnusedDataEliminator
from google.appengine.ext.deferred import defer

class _DeleteUnused(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            start = int(jrequest.getPathInfo(4))
            end = int(jrequest.getPathInfo(5))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        #query = MetadataNdb.queryRange(start, end)
        #keys = query.fetch(keys_only=True)
        eliminator = UnusedDataEliminator(start, end)
        defer(eliminator.run)
        jresponse.setExtraValue("start", start)
        jresponse.setExtraValue("end", end)


import UrlMap
UrlMap.UrlMap.append(("/api/Data/UnusedDataEliminator/[0-9]+/[0-9]+", _DeleteUnused))

if __name__ == "__main__":
    import unittest
    unittest.main()
