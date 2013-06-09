#!-*- coding:utf-8 -*-
from __future__ import unicode_literals, print_function
from logging import debug

from google.appengine.ext import db
from google.appengine.ext.webapp import Request
from google.appengine.api.memcache import Client

from model.Counter import Counter
from django.utils import simplejson


class Data(db.Model):
    dataId = db.IntegerProperty()
    field = db.StringProperty()
    string = db.StringProperty()

    @classmethod
    def getQueryByDataIdDecending(cls):
        query = db.Query(kind=Data, keys_only=True)
        query.order(-Data.dataId)
        return query

    @classmethod
    def getKeyByFieldAndStringFromMemcache(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        client = Client()
        key = client.get(field + string, namespace="DataKeyByFieldAndString")
        assert key is None or isinstance(key, db.Key)
        return key

    @classmethod
    def getKeyByFieldAndStringFromDatastore(cls, field, string):
        gql_query = Data.gql("WHERE field = :1 AND string = :2", field, string)
        keys = gql_query.fetch(keys_only=True, limit=2)
        if len(keys) == 0:
            return None
        if len(keys) == 2:
            debug("two entities found for field=%s and string=%s" % (field, string))
            # TODO: duplicated entity should be merged
        return keys[0]

    @classmethod
    def getKeyByFieldAndString(cls, field, string):
        key = cls.getKeyByFieldAndStringFromMemcache(field, string)
        if key: return key
        key = cls.getKeyByFieldAndStringFromDatastore(field, string)
        return key

    @classmethod
    def getEntityByKey(cls, key):
        assert isinstance(key, db.Key)
        client = Client()
        entity = client.get(str(key), namespace="DataEntityByKey")
        if entity: return entity
        entities = cls.get([key])
        assert isinstance(entities, list)
        if len(entities) == 0: return None
        entity = entities[0]
        if entity is None: return None
        assert isinstance(entity, Data)
        entity.putEntityToMemcache()
        return entity

    def putEntityToMemcache(self):
        client = Client()
        client.add(self.field + self.string, self, namespace="DataByFeldAndString")
        client.add(str(self.key()), self, namespace="DataEntityByKey")

    def deleteEntityFromMemecache(self):
        client = Client()
        client.delete(str(self.key()), namespace="DataEntityByKey")

    @classmethod
    def putEntity(cls, field, string):
        assert isinstance(field, unicode) or isinstance(field, str)
        assert isinstance(string, unicode) or isinstance(string, str)
        if isinstance(field, str): field = field.decode()
        if isinstance(string, str): string = string.decode()
        key = cls.getKeyByFieldAndString(field, string)
        if key: return key
        key = cls.getKeyByFieldAndStringFromDatastore(field, string)
        if key: return key

        data = Data()
        data.dataId = Counter.GetNextId("dataId")
        data.field = field
        data.string = string
        return data.put()

    @classmethod
    def storeRequest(cls, request):
        assert isinstance(request, Request)
        data_list = []
        for field in request.arguments():
            vlist = request.get_all(field)
            #debug((field, vlist))
            assert isinstance(vlist, list)
            for string in vlist:
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)

        try:
            parsed_json = simplejson.loads(request.body)
        except ValueError:
            parsed_json = None

        if (parsed_json != None):
            for field, string in parsed_json.iteritems():
                #logging.log(logging.INFO, type(v))
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)

        getDataFromRequest(request)

        return data_list


def getDataFromQueryPart(request):
    assert isinstance(request, Request)
    data_list = []
    for field in request.arguments():
        field = field.decode()
        assert isinstance(field, unicode)
        vlist = request.get_all(field)
        #debug((field, vlist))
        assert isinstance(vlist, list)
        for string in vlist:
            assert isinstance(string, unicode)
            #data = cls.putEntity(field, string)
            #if data is None: continue
            data_list.append((field, string))
    return data_list


def getDataFromBody(request):
    assert isinstance(request, Request)
    data_list = []
    try:
        parsed_json = simplejson.loads(request.body)
    except ValueError:
        parsed_json = {}

    for field, string in parsed_json.iteritems():
        #logging.log(logging.INFO, type(v))
        #data = cls.putEntity(field, string)
        #if data is None: continue
        data_list.append((field, string))
    return data_list


def getDataFromRequest(request):
    assert isinstance(request, Request)
    l1 = getDataFromQueryPart(request)
    assert isinstance(l1, list)
    l2 = getDataFromBody(request)
    assert isinstance(l2, list)
    return l1 + l2


import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def testSimplePutGetDelete(self):
        key = Data.putEntity("field1", "stirng1")
        self.assertIsInstance(key, db.Key)
        entity = Data.getEntityByKey(key)
        self.assertEqual(entity.field, "field1")
        entity.delete()
        entity2 = Data.getEntityByKey(key)
        self.assertIsNotNone(entity2)

        entity.deleteEntityFromMemecache()
        entity3 = Data.getEntityByKey(key)
        self.assertIsNone(entity3)


    def tearDown(self):
        self.testbed.deactivate()


if __name__ == "__main__":
    unittest.main()