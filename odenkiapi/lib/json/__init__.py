from __future__ import unicode_literals, print_function
from json import dumps as _dumps

from JsonEncoder import JSONEncoder
from JsonRpcRequest import JsonRpcRequest
from JsonRpcResponse import JsonRpcResponse
from JsonRpcError import JsonRpcError


def dumps(d):
    return _dumps(d, indent=4, cls=JSONEncoder)
