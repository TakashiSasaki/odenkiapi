from __future__ import unicode_literals, print_function
from logging import debug

class JsonRpcError(object):
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_RESERVED_MAX = -32000
    SERVER_ERROR_RESERVED_MIN = -32099
    

class JsonRpcException(RuntimeError):
    errorCode = -32000
    __slots__ = ["code", "message", "data"]

    def __init__(self, code, message, data={}, exception_class=None):
        RuntimeError.__init__(self)
        assert isinstance(data, dict)
        self.code = code
        self.message = message
        self.data = data
        self.setExceptionClassName(exception_class)
    
    def setExceptionClassName(self, exception_class):
        if exception_class is None:return
        assert issubclass(exception_class, JsonRpcException)
        assert isinstance(self.data, dict)
        self.data["exceptionClass"] = exception_class.__name__

    def __str__(self):
        return unicode(self.message) + unicode(self.data)

class ParseError(JsonRpcException):
    errorCode = JsonRpcError.PARSE_ERROR
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class InvalidRequest(JsonRpcException):
    errorCode = JsonRpcError.INVALID_REQUEST
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class MethodNotFound(JsonRpcException):
    errorCode = JsonRpcError.METHOD_NOT_FOUND
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class InvalidParams(JsonRpcException):
    errorCode = JsonRpcError.INVALID_PARAMS
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class InternalError(JsonRpcException):
    errorCode = JsonRpcError.INTERNAL_ERROR
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class EntityNotFound(JsonRpcException):
    errorCode = -32097
    def __init__(self, model, condition):
        from google.appengine.ext import db
        from google.appengine.ext import ndb
        if isinstance(model, db.Model):
            kind = model.kind()
        elif isinstance(model, ndb.Model):
            kind = model.kind()
        elif isinstance(model, ndb.MetaModel):
            assert isinstance(model, ndb.MetaModel)
            kind = unicode(model.__name__)
        else:
            kind = unicode(model)
        JsonRpcException.__init__(self, self.errorCode,
                                  "Entity of %s is not found" % kind,
                                  {"kind":kind, "condition":condition},
                                  exception_class=self.__class__)

class EntityExists(JsonRpcException):
    errorCode = -32096
    def __init__(self, model, condition):
        from google.appengine.ext import db
        from google.appengine.ext import ndb
        if isinstance(model, db.Model):
            kind = model.kind()
        elif isinstance(model, ndb.Model):
            kind = model.kind()
        elif isinstance(model, ndb.MetaModel):
            assert isinstance(model, ndb.MetaModel)
            kind = unicode(model.__name__)
        else:
            kind = unicode(model)
        JsonRpcException.__init__(self, self.errorCode,
                                  "Entity of %s already exists" % kind,
                                  {"kind":kind, "condition":condition},
                                  exception_class=self.__class__)
        

class UnexpectedState(JsonRpcException):
    errorCode = -32095
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data, self.__class__)

class PasswordMismatch(JsonRpcException):
    errorCode = -32094
    def __init__(self, hashed_password):
        JsonRpcException.__init__(self, self.errorCode,
                                  "Passwords and do not match.",
                                  {"hashed_password": hashed_password},
                                  self.__class__)

class MixedAuthentication(JsonRpcException):
    errorCode = -32093
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode,
                                  "Authentication with different odenkiId was detected.",
                                  data, self.__class__)

class OAuthError(JsonRpcException):
    errorCode = -32092
    def __init__(self, message):
        JsonRpcException.__init__(self, self.errorCode, message, exception_class=self.__class__)

#class InvalidatedUser(JsonRpcException):
#    errorCode = -32091
#    def __init__(self, data):
#        JsonRpcException.__init__(self, self.errorCode, "Invalidated user.", data)

class EntityDuplicated(JsonRpcException):
    errorCode = -32090
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode, "Duplicated entity found.",
                                  data, self.__class__)

class EntityInvalidated(JsonRpcException):
    errorCode = -32089
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode, "Entity was found but invalidated.",
                                  data, self.__class__)

class InconistentAuthentiation(JsonRpcException):
    errorCode = -32088
    def __init__(self, existing_user_id, data={}):
        JsonRpcException.__init__(self, self.errorCode, exception_class=self.__class__)

class _Dummy(JsonRpcException):
    errorCode = -32089

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
            error_code = json_rpc_exception_class.errorCode
            assert isinstance(error_code, int) and error_code < 0
            if json_rpc_exceptions.has_key(error_code):
                raise UserWarning("duplicated errocodes %s were defined in %s and %s",
                                  (error_code, json_rpc_exceptions[error_code].__class__.__name__, json_rpc_exception_name))
            json_rpc_exceptions[error_code] = json_rpc_exception_class
