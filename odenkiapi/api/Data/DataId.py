from __future__ import unicode_literals, print_function
#import  webapp2
from lib.gae import JsonRpcDispatcher
#from lib.json import JsonRpcRequest, JsonRpcResponse, JsonRpcError
from lib.json.JsonRpcRequest import JsonRpcRequest
from lib.json.JsonRpcResponse import JsonRpcResponse
from lib.json.JsonRpcError import JsonRpcError
from model.DataNdb import Data


class DataId(JsonRpcDispatcher):
    def GET(self, jrequest, jresponse):
        assert isinstance(jrequest, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        jresponse.setId()
        try:
            data_id_string = jrequest.getPathInfo(4)
            data_id = int(data_id_string)
        except:
            return
        try:
            data = Data.getByDataId(data_id)
        except:
            jresponse.setError(JsonRpcError.SERVER_ERROR_RESERVED_MIN, "dataId %s not found" % data_id)
            return
            #data = data_key.get()
        assert isinstance(data, Data)
        jresponse.addResult(data)
        jresponse.setExtraValue("key_id", data.key.id())


paths = [("/api/Data/dataId/[0-9]+", DataId)]

