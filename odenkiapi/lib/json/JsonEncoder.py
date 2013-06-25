# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from json import JSONEncoder as _JSONEncoder
from datetime import datetime
from logging import debug

from google.appengine.ext import ndb
from google.appengine.ext import db

from gaesessions import Session
from gdata.gauth import OAuthHmacToken
from model.Columns import Columns
import model.DataNdb
import model.Data


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, Session):
            return str(o.sid)
        if isinstance(o, OAuthHmacToken):
            return o.token
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, ndb.Key):
            assert isinstance(o, ndb.Key)
            debug("encoding ndb.Key %s to JSON" % o)
            entity = o.get()
            if entity is None: return None
            return unicode(o.get().to_dict())
        if isinstance(o, db.Key):
            assert isinstance(o, db.Key)
            debug("encoding db.Key %s to JSON" % o)
            return unicode(o)
        if isinstance(o, ndb.Key):
            return self.default(ndb.get(o))
        if isinstance(o, model.Data.Data):
            d = {"dataId": o.dataId, "field": o.field, "string": o.string}
            return d
            # if isinstance(o, model.DataNdb.Data):
        #     l = [o.dataId, o.field, o.string]
        #     return l
        if isinstance(o, ndb.Model):
            debug("encoding NdbModel %s to JSON" % o)
            return o.to_dict()
        if isinstance(o, Columns):
            assert isinstance(o, Columns)
            debug("encoding Columns %s to JSON" % o)
            return o.getDataTableCols()
            # if isinstance(o, dict):
        #     return o
        debug("encoding unknown object %s, %s " % (type(o), o))
        return _JSONEncoder.default(self, o)
