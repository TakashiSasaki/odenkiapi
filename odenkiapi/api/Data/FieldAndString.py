from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher
from lib.json.JsonRpcResponse import JsonRpcResponse
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcError import EntityNotFound
from model.DataNdb import Data


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
        if data_keys is None or len(data_keys) == 0:
            raise EntityNotFound()
        for data_key in data_keys:
            data = data_key.get()
            jresponse.addResult(data)


paths = [("/api/Data/[^/]+/[^/]+", FieldAndString)]

