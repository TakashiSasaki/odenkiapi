from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data

class Field(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            field = unicode(jrequest.getPathInfo(3))
        except Exception, e:
            jresponse.setErrorInvalidParameter(e)
            return
        data_keys = Data.fetchByField(field)
        for data_key in data_keys:
            data = data_key.get()
            jresponse.addResult(data)

import UrlMap
UrlMap.UrlMap.append(("/api/Data/[^/]+", Field))

if __name__ == "__main__":
    import unittest
    unittest.main()
