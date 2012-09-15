from __future__ import unicode_literals, print_function
from lib.gae import JsonRpcDispatcher, run_wsgi_app
from lib.json import JsonRpcRequest, JsonRpcResponse
from logging import debug

class Echo(JsonRpcDispatcher):
    """Echo returns given RPC object as it is."""
    
    def GET(self, json_rpc_request, jresponse):
        debug("entered in Echo.GET")
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        return self.echo(json_rpc_request, jresponse)
        
    def TRACE(self, json_rpc_request, jresponse):
        debug("entered in Echo.TRACE")
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)
        return self.echo(json_rpc_request, jresponse)

    def echo(self, json_rpc_request, jresponse):
        assert isinstance(json_rpc_request, JsonRpcRequest)
        assert isinstance(jresponse, JsonRpcResponse)

        debug("entered in Echo.echo with id = %s " % json_rpc_request.getId())
        jresponse.setResult({
                                    "id": json_rpc_request.getId(),
                                    "params" : json_rpc_request.getParams(),
                                    "extra" :json_rpc_request.getExtra(),
                                    "jsonrpc" : json_rpc_request.getJsonRpcVersion()
                                    })
    
if __name__ == "__main__":
    mapping = [("/api/echo", Echo)]
    run_wsgi_app(mapping)
