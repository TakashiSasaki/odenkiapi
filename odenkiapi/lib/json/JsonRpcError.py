from __future__ import unicode_literals, print_function
from logging import debug
from model.NdbModel import NdbModel
from yaml.parser import ParserError

class JsonRpcError(object):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_RESERVED_MAX = -32000
    SERVER_ERROR_RESERVED_MIN = -32099
    

class JsonRpcException(RuntimeError):
    code = -32000
    __slots__ = ["message", "data"]
    
    def __str__(self):
        return unicode(self.message) + unicode(self.data)

class ParseError(JsonRpcException):
    code = JsonRpcError.PARSE_ERROR
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class InvalidRequest(JsonRpcException):
    code = JsonRpcError.INVALID_REQUEST
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class MethodNotFound(JsonRpcException):
    code = JsonRpcError.METHOD_NOT_FOUND
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class InvalidParams(JsonRpcException):
    code = JsonRpcError.INVALID_PARAMS
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class InternalError(JsonRpcException):
    code = JsonRpcError.INTERNAL_ERROR
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class EntityNotFound(JsonRpcException):
    code = -32097
    def __init__(self, data={}, message=None):
        self.message = message
        self.data = data

class EntityExists(JsonRpcException):
    code = -32096
    def __init__(self, data={}, message=""):
        self.data = data
        self.message = message

class UnexpectedState(JsonRpcException):
    code = -32095
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class PasswordMismatch(JsonRpcException):
    code = -32094
    def __init__(self, hashed_password, message=None):
        self.message = message
        self.data = {"hashed_password": hashed_password}

#class MixedAuthentication(JsonRpcException):
#    code = -32093
#    def __init__(self, data={}, message = None):
#        self.message = message
#        self.data  = data
#        JsonRpcException.__init__(self, self.errorCode,
#                                  "Authentication with different odenkiId was detected.",
#                                  data, self.__class__)

class OAuthError(JsonRpcException):
    code = -32092
    def __init__(self, data={}, message=None):
        assert isinstance(data, dict)
        assert isinstance(message, unicode)
        self.message = message
        self.data = data

#class InvalidatedUser(JsonRpcException):
#    errorCode = -32091
#    def __init__(self, data):
#        JsonRpcException.__init__(self, self.errorCode, "Invalidated user.", data)

class EntityDuplicated(JsonRpcException):
    code = -32090
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class EntityInvalidated(JsonRpcException):
    code = -32089
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class InconsistentAuthentiation(JsonRpcException):
    code = -32088
    def __init__(self, data={}, message=None):
        self.data = data
        self.message = message

class _Dummy(JsonRpcException):
    code = -32087

if __name__ == "__main__":
    import sys
    print (sys.version)
    print (dir())
    print (globals())
    g = dict(globals())
    json_rpc_exceptions = {}
    for json_rpc_exception_name, json_rpc_exception_class in g.iteritems():
        if not isinstance(json_rpc_exception_class, type): continue
        if issubclass(json_rpc_exception_class, JsonRpcException):
            print (json_rpc_exception_name, json_rpc_exception_class)
            error_code = json_rpc_exception_class.code
            assert isinstance(error_code, int) and error_code < 0
            if json_rpc_exceptions.has_key(error_code):
                raise UserWarning("duplicated errocodes %s were defined in %s and %s",
                                  (error_code, json_rpc_exceptions[error_code].__class__.__name__, json_rpc_exception_name))
            json_rpc_exceptions[error_code] = json_rpc_exception_class
