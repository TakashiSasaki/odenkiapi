from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.DataNdb import Data
from urlparse import urlparse

class _Range(JsonRpcDispatcher):

    def GET(self, jrequest, jresponse):
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        path_info = self.request.path_info.split("/")
        start = int(path_info[3])
        end = int(path_info[4])

        query = Data.queryRange(start, end)
        #query = query.filter(Data.dataId >= start)
        #query = query.filter(Data.dataId <= end)

        keys = query.fetch(keys_only=True)
        for key in keys:
            entity = key.get()
            assert isinstance(entity, Data)
            jresponse.addResult(entity)


    def PUT(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        query_string = urlparse(self.request.url)[4]
        #debug(query_string)
        if len(query_string) > 0:
            keys = Data.putParams(query_string)
            self.response.out.write("keys = %s" % keys)
            return

import UrlMap
UrlMap.UrlMap.append(("/api/Data/[0-9]+/[0-9]+", _Range))

if __name__ == "__main__":
    import unittest
    unittest.main()
