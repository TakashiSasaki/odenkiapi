from __future__ import unicode_literals, print_function

from google.appengine.ext.deferred import defer

from lib.gae import JsonRpcDispatcher
from lib.json import JsonRpcRequest, JsonRpcResponse
from model.UnusedDataEliminator import UnusedDataEliminator


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


paths = [("/api/Data/UnusedDataEliminator/[0-9]+/[0-9]+", _DeleteUnused)]

