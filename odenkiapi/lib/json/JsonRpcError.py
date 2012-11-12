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

    def __init__(self, code, message, data=None):
        RuntimeError.__init__(self)
        self.code = self.errorCode
        self.message = message
        self.data = data

    def __str__(self):
        return unicode(self.message) + unicode(self.data)

class ParseError(JsonRpcException):
    errorCode = JsonRpcError.PARSE_ERROR
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

class InvalidRequest(JsonRpcException):
    errorCode = JsonRpcError.INVALID_REQUEST
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

class MethodNotFound(JsonRpcException):
    errorCode = JsonRpcError.METHOD_NOT_FOUND
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

class InvalidParams(JsonRpcException):
    errorCode = JsonRpcError.INVALID_PARAMS
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

class InternalError(JsonRpcException):
    errorCode = JsonRpcError.INTERNAL_ERROR
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

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
            kind = unicode(model)
        else:
            kind = unicode(model)
        JsonRpcException.__init__(self, self.errorCode, "Entity of %s is not found" % kind, {"kind":kind, "condition":condition})

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
            kind = unicode(model)
        else:
            kind = unicode(model)
        JsonRpcException.__init__(self, self.errorCode, "Entity of %s already exists" % kind, {"kind":kind, "condition":condition})
        

class UnexpectedState(JsonRpcException):
    errorCode = -32095
    def __init__(self, message, data=None):
        JsonRpcException.__init__(self, self.errorCode, message, data)

class PasswordMismatch(JsonRpcException):
    errorCode = -32094
    def __init__(self, hashed_password):
        JsonRpcException.__init__(self, self.errorCode, "Passwords and do not match.", {"hashed_password": hashed_password})

class MixedAuthentication(JsonRpcException):
    errorCode = -32093
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode, "Authentication with different odenkiId was detected.", data)

class OAuthError(JsonRpcException):
    errorCode = -32092
    def __init__(self, message):
        JsonRpcException.__init__(self, self.errorCode, message)

#class InvalidatedUser(JsonRpcException):
#    errorCode = -32091
#    def __init__(self, data):
#        JsonRpcException.__init__(self, self.errorCode, "Invalidated user.", data)

class EntityDuplicated(JsonRpcException):
    errorCode = -32090
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode, "Duplicated entity found.", data)

class EntityInvalidated(JsonRpcException):
    errorCode = -32089
    def __init__(self, data):
        JsonRpcException.__init__(self, self.errorCode, "Entity was found but invalidated.", data)