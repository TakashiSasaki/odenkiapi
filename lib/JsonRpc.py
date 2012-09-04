__all__ = ["JsonRpcError", "JsonRpcRequest", "JsonRpcResponse"]

from encodings.base64_codec import base64_decode
from simplejson import loads, JSONDecodeError
#from lib.CachedContent import CachedContent
#from logging import debug, getLogger, DEBUG
from google.appengine.ext.webapp import Request
#getLogger().setLevel(DEBUG)
import lib

class JsonRpcError(object):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_RESERVED_MAX = -32000
    SERVER_ERROR_RESERVED_MIN = -32099

class JsonRpcRequest(object):
    """JSON-RPC 2.0 over HTTP GET method should have method,id and params in URL parameter part.
    params should be encoded in BASE64.
    This method also accepts bare parameters in URL parameter part and puts them in value of 
    'param' key in JSON-RPC request object.
    See http://www.simple-is-better.org/json-rpc/jsonrpc20-over-http.html
    """
    __slots__ = ["jsonrpc", "method", "id", "params", "extras", "error"]

    def __init__(self, request):
        assert isinstance(request, Request)
        self.error = None
        self.method = None
        self.params = []
        self.id = None
        self.jsonrpc = None
        self.extras = {}

        # methods are listed in http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
        # default JSON-RPC method is identical to HTTP method and it should be overridden
        lib.debug("HTTP method: %s" % request.method)
        self.method = request.method
        if request.method == "OPTIONS":
            self._getFromArguments(request)
            return
        if request.method == "GET":
            self._getFromArguments(request)
            return
        if request.method == "HEAD":
            self._getFromArguments(request)
            return
        if request.method == "POST":
            self._getFromBody(request)
            return
        if request.method == "PUT":
            self._getFromBody(request)
            return
        if request.method == "DELETE":
            self._getFromArguments(request)
            return
        if request.method == "TRACE":
            self._getFromBody(request)
            return
        
    def _getFromArguments(self, request):
        lib.debug("entered in _getFromArguments")
        for argument in request.arguments():
            values = request.get_all(argument)
            if argument == "jsonrpc":
                assert len(values) != 0
                if len(values) > 1:
                    lib.error("multiple jsonrpc version indicator")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.jsonrpc = values[0]
                continue
            if argument == "method":
                lib.debug("argument %s has %s" % (argument, values))
                assert len(values) != 0
                if len(values) > 1:
                    lib.error("multiple methods are given")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.method = values[0]
                continue
            if argument == "id":
                lib.debug("argument %s has %s" % (argument, values))
                assert len(values) != 0
                if len(values) > 1:
                    lib.error("multiple ids are given")
                    self.error = JsonRpcError.INVALID_REQUEST
                    return
                self.id = values[0]
                continue
            if argument == "params":
                for params in values:
                    try:
                        decoded_params = base64_decode(params)
                    except:
                        lib.error("failed to decode BASE64 for params")
                        self.error = JsonRpcError.PARSE_ERROR
                        return
                    try:
                        loaded_params = loads(decoded_params)
                    except:
                        lib.error("failed to decode JSON for params")
                        self.error = JsonRpcError.PARSE_ERROR
                        return
                    try:
                        assert isinstance(loaded_params, list)
                    except:
                        lib.error("params is expected to be an array of objects, that is, a list")
                        self.error = JsonRpcError.PARSE_ERROR
                    self.params.extend(loaded_params)
                continue
            lib.debug("extra data %s:%s" % (argument, values))
            self.extras[argument] = values
        assert not isinstance(self.id, list)
        #self.extras.extends(extras_in_arguments)
                    
    def _getFromBody(self, request):
        """JSON-RPC request in HTTP body precedes that in parameter part of URL and FORM"""
        assert self.error is None
        assert isinstance(request.body, str)
        try:
            json_rpc_request_dict = loads(request.body)
        except:
            lib.error("failed to parse JSON object in the body")
            self.error = JsonRpcError.PARSE_ERROR
            return
        for k, v in json_rpc_request_dict:
            if k == "jsonrpc":
                self.jsonrpc = v
            if k == "method":
                self.method = v
            if k == "id":
                self.id = v
            if k == "params":
                self.params = v
            self.extras[k] = v
        
class JsonRpcResponse(object):
    __slots__ = [ "id", "result", "error" ]
    
    def __init__(self, request_id):
        lib.debug("constructor of JsonRpcResponse object")
        self.id = request_id
        #self.requestHandler = request_handler
        #self.request = request_handler.request
        #self.response = request_handler.response
        #self.error = {}
        self.result = None
        self.error = None
    
    def _getArgumentDict(self):
        raise DeprecationWarning()
        d = {}
        for a in self.request.arguments():
            assert isinstance(a, unicode)
            d[a] = self.request.get_all(a)
            if isinstance(d[a], list) and len(d[a]) == 1:
                d[a] = d[a][0]
        return d

    def redirect(self, url):
        raise DeprecationWarning()
        self.requestHandler.redirect(url)
        assert self.response.status == 302
        self.setHttpStatus(self.response.status)

    def setHttpStatus(self, http_status):
        raise DeprecationWarning()
        assert isinstance(http_status, int)
        assert not hasattr(self, "httpStatus")
        self.httpStatus = http_status
        
    def setError(self, error_code, error_message=None, error_data=None):
        assert isinstance(error_code, int)
        assert not hasattr(self, "error")
        self.error = {
                      "code": error_code,
                      "message": error_message,
                      "data":error_data
                      }
        #http_status = _getHttpStatusFromJsonRpcerror(error_code)
        #self.setHttpStatus(http_status)
        
    def setResultValue(self, key, value):
        if not hasattr(self, "result"):
            self.result = {}
        assert isinstance(self.result, dict)
        assert not self.result.has_key(key)
        self.result[key] = value
        
    def appendResultValue(self, key, value):
        if self.result.has_key(key):
            if not isinstance(self.result.get(key), list):
                self.result[key] = [self.result[key]]
        assert isinstance(self.result.get(key), list)
        self.result["key"].append(value)

        
    #def addLog(self, log_message):
    #    if not hasattr(self, "log"):
    #        self.log = []
    #    self.log.append(log_message)

    def setResult(self, result):
        assert not hasattr(self, "result") or self.result is None
        self.result = result
        
    def updateResult(self, result):
        assert isinstance(self.result, dict)
        self.result.update(result)
        
    #def getParam(self, key):
    #    if hasattr(self, "params"):
    #       if isinstance(self.params, dict):
    #           return self.params.get(key)
    #    return self.jsonRequest.get(key)
    
    #def getParams(self):
    #    assert isinstance(self.params, dict)
    #   return self.params
    
    #def getMethod(self):
    #    if not hasattr(self, "method"): return None
    #   assert isinstance(self.method, str) or isinstance(self.method, unicode)
    #    return self.method
    
    #def getRequest(self):
    #   return self.jsonRequest
    
    #def getId(self):
    #    assert isinstance(self.id, None) or isinstance(self.id, int) or isinstance(self.id, long) or isinstance(self.id, str)
    #    return self.id
    
    #def getVersion(self):
    #    if hasattr(self, "jsonrpc"):
    #        if self.jsonrpc == "2.0":
    #            return 2
    #        else: return 1
    #    return None
        
    def getErrorCode(self):
        try:
            error_code = self.error["code"]
            if isinstance(error_code, int):
                return error_code
        except:
            pass
        return None
    
        
