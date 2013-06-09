from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from model.DataNdb import Data

class DataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            data_id = int(jrequest.getPathInfo()[3])
        except: return
        data_key = Data.getByDataId(data_id)
        if data_key is None:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "dataId %s not found" % data_id)
            return
        data = data_key.get()
        assert isinstance(data, Data)
        jresponse.addResult(data)
        jresponse.setExtraValue("key_id", data.key.id())

import UrlMap
UrlMap.UrlMap.append(("/api/Data/dataId/[0-9]+", DataId))

if __name__ == "__main__":
    import unittest
    unittest.main()
