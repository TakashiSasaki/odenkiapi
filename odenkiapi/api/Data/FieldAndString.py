from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data
from google.appengine.ext import ndb

class FieldAndString(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            field = unicode(jrequest.getPathInfo(3))
            string = unicode(jrequest.getPathInfo(4))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        data_keys = Data.fetchByFieldAndString(field, string)
        if data_keys is None: return
        for data_key in data_keys:
            data = data_key.get()
            jresponse.addResult(data)

import UrlMap
UrlMap.UrlMap.append(("/api/Data/[^/]+/[^/]+", FieldAndString))

if __name__ == "__main__":
    import unittest
    unittest.main()
