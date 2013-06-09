from __future__ import unicode_literals
from logging import debug
from warnings import warn
from google.appengine.ext import ndb
from google.appengine.ext.webapp import Request
#import types,logging
from model.Counter import Counter
#from django.utils import simplejson
from json import loads
from model.NdbModel import NdbModel
from google.appengine.api.memcache import Client
from lib.json.JsonRpcError import EntityDuplicated, EntityNotFound, EntityExists


class Data(NdbModel):
    dataId = ndb.IntegerProperty()
    field = ndb.StringProperty()
    string = ndb.StringProperty()

    fieldnames = ["dataId", "field", "string"]

    def to_list(self):
        return [self.dataId, self.field, self.string]

    @classmethod
    def prepare(cls, field, string):
        try:
            data = cls.getByFieldAndString(field, string)
            return data
        except EntityNotFound:
            data = cls.create(field, string)
            return data

    @classmethod
    def create(cls, field, string, allow_duplication=False):
        try:
            existing = cls.getByFieldAndString(field, string)
            if allow_duplication:
                raise EntityNotFound
            raise EntityExists("Data", {"field": field, "string": string})
        except EntityNotFound:
            data = Data()
            data.dataId = Counter.GetNextId("dataId")
            data.field = field
            data.string = string
            data.put()
            return data

    @classmethod
    def queryByField(cls, field):
        query = ndb.Query(kind="Data")
        query = query.order(cls.dataId)
        query = query.filter(cls.field == field)
        return query

    @classmethod
    def fetchByField(cls, field):
        return cls.queryByField(field).fetch(limit=100, keys_only=True)

    @classmethod
    def queryByFieldAndString(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        query = ndb.Query(kind="Data")
        query = query.order(cls.dataId)
        query = query.filter(cls.field == field)
        query = query.filter(cls.string == string)
        return query

    @classmethod
    def _getMemcacheKeyByFieldAndString(cls, field, string):
        return "kml87wfasfp98uw45nvljkbbjlkq4" + field + "nvnjqlagzahk" + string

    @classmethod
    def fetchByFieldAndString(cls, field, string):
        assert isinstance(field, unicode)
        assert isinstance(string, unicode)
        client = Client()
        data_keys = client.get(cls._getMemcacheKeyByFieldAndString(field, string))
        if data_keys: return data_keys
        data_keys = cls.queryByFieldAndString(field, string).fetch(keys_only=True)
        if len(data_keys) >= 2: warn("duplicated data entities with field=%s and string=%s" % (field, string))
        client.set(cls._getMemcacheKeyByFieldAndString(field, string), data_keys)
        return data_keys

    @classmethod
    def getByFieldAndString(cls, field, string):
        query = cls.queryByFieldAndString(field, string)
        keys = query.fetch(keys_only=True, limit=2)
        if len(keys) == 2:
            raise EntityDuplicated()
        if len(keys) == 0:
            raise EntityNotFound("Data", {"field": field, "string": string})
        return keys[0].get()

    # @classmethod
    # def querySingle(cls, data_id):
    #     #warn("querySingle is deprecatd. Use getByDataId instead.", DeprecationWarning, 2)
    #     raise PendingDeprecationWarning("querySingle is deprecatd. Use getByDataId instead.")
    #     query = ndb.Query(kind="Data")
    #     query = query.filter(Data.dataId == data_id)
    #     return query

    def deleteEntity(self):
        client = Client()
        client.delete(self._getMemcacheKeyByFieldAndString(self.field, self.string))
        client.delete(self._getMemcacheKeyByDataId(self.dataId))
        self.key.delete()

    @classmethod
    def _getMemcacheKeyByDataId(cls, data_id):
        return "jkijwxpmuqzkldruoinjx" + unicode(data_id)

    # @classmethod
    # def queryByDataId(cls, data_id):
    #     assert isinstance(data_id, int)
    #     query = ndb.Query(kind="Data")
    #     query = query.filter(cls.dataId == data_id)
    #     return query

    @classmethod
    def getByDataId(cls, data_id):
        assert isinstance(data_id, int)
        client = Client()
        data = client.get(cls._getMemcacheKeyByDataId(data_id))
        if data: return data
        query = ndb.Query(kind="Data")
        query = query.filter(cls.dataId == data_id)
        #query = query.order(cls.dataId)
        data_keys = query.fetch(keys_only=True, limit=2)
        if data_keys is None: return
        if len(data_keys) == 0:
            raise EntityNotFound("Data", {"dataId": data_id})
        if len(data_keys) > 1:
            warn("%s Data entities with dataId %s were found" % (len(data_keys), data_id), RuntimeWarning)
        data = data_keys[0].get()
        assert isinstance(data, Data)
        client.set(cls._getMemcacheKeyByDataId(data_id), data)
        return data

    @classmethod
    def queryRecent(cls):
        query = ndb.Query(kind="Data")
        query = query.order(-Data.dataId)
        return query

    @classmethod
    def queryRange(cls, start_data_id, end_data_id):
        assert isinstance(start_data_id, int)
        assert isinstance(end_data_id, int)
        query = ndb.Query(kind="Data")
        if start_data_id <= end_data_id:
            query = query.filter(cls.dataId >= start_data_id)
            query = query.filter(cls.dataId <= end_data_id)
            return query
        else:
            query = query.order(-cls.dataId)
            query = query.filter(cls.dataId <= start_data_id)
            query = query.filter(cls.dataId >= end_data_id)
            return query

    def queryDuplication(self):
        query = ndb.Query(kind="Data")
        query = query.filter(Data.field == self.field)
        query = query.filter(Data.string == self.string)
        query = query.order(Data.dataId)
        return query

    @classmethod
    def putEntity(cls, field, string):
        raise PendingDeprecationWarning("NdbData.Data.putEntity is being deprecated.")
        debug("type of field is %s" % type(field))
        field = unicode(field)
        assert isinstance(field, unicode)
        string = unicode(string)
        assert isinstance(string, unicode)
        q = cls.getByFieldAndString(field, string)
        k = q.get(keys_only=True)
        if k: return k

        data = cls()
        assert isinstance(data, ndb.Model)
        data.dataId = Counter.GetNextId("dataId")
        data.field = field
        data.string = string
        data.put()
        q = cls.getByFieldAndString(field, string)
        k = q.get(keys_only=True)
        return k

    @classmethod
    def putParams(cls, query_string):
        from urlparse import parse_qs

        d = parse_qs(query_string)
        assert isinstance(d, dict)
        l = []
        for key_in_dict in d.keys():
            for value_in_dict in d.get(key_in_dict):
                if isinstance(value_in_dict, list):
                    for item in value_in_dict:
                        assert isinstance(item, unicode)
                        entity_key = cls.putEntity(key_in_dict, item)
                        if entity_key not in l:
                            l.append(entity_key)
                else:
                    entity_key = cls.putEntity(key_in_dict, value_in_dict)
                    l.append(entity_key)
        return l

    @classmethod
    def putRequest(cls, request):
        assert isinstance(request, Request)
        data_list = []
        for field in request.arguments():
            vlist = request.get_all(field)
            #logging.info((k,vlist))
            assert isinstance(vlist, list)
            for string in vlist:
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)
        try:
            parsed_json = loads(request.body)
        except ValueError:
            parsed_json = None

        if (parsed_json != None):
            for field, string in parsed_json.iteritems():
                #logging.log(logging.INFO, type(v))
                data = cls.putEntity(field, string)
                if data is None: continue
                data_list.append(data)
        return data_list


def getCanonicalData(key):
    assert isinstance(key, ndb.Key)
    MEMCACHE_KEY = "akafkljacuiudrt2po8vxdzskj" + str(key)
    client = Client()
    canonical_data_key = client.get(MEMCACHE_KEY)
    if canonical_data_key: return canonical_data_key
    data = key.get()
    if data is None: return None
    assert isinstance(data, Data)
    query = data.queryDuplication()
    canonical_data_key = query.get(keys_only=True)
    assert isinstance(canonical_data_key, ndb.Key)
    assert data.dataId >= canonical_data_key.get().dataId
    assert data.field == canonical_data_key.get().field
    assert data.string == canonical_data_key.get().string
    client.set(MEMCACHE_KEY, canonical_data_key)
    return canonical_data_key


def getCanonicalDataList(key_list):
    result = []
    for key in key_list:
        #assert isinstance(key, ndb.Key)
        canonical_data_key = getCanonicalData(key)
        result.append(canonical_data_key)
    return result


def isEquivalentDataKeyList(l1, l2):
    if len(l1) != len(l2): return False
    for i in range(len(l1)):
        k1 = l1[i]
        if not k1:
            return False
        else:
            e1 = k1.get()
        k2 = l2[i]
        if not k2:
            return False
        else:
            e2 = k2.get()
        if e1.field != e2.field: return False
        if e1.string != e2.string: return False
    return True


import unittest


class _TestCase(unittest.TestCase):
    def setUp(self):
        from google.appengine.ext import testbed

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        keys = Data.query().fetch()
        for k in keys: k.delete()

    def testSimplePutGetDelete(self):
        data = Data.prepare("field1", "string1")
        self.assertIsInstance(data, Data)
        #entity = Data.getEntityByKey(key)
        self.assertEqual(data.field, "field1")
        data_id = data.dataId
        key = data.key
        self.assertIsInstance(key, ndb.Key)
        entity2 = key.get()
        self.assertEqual(entity2.field, "field1")
        self.assertEqual(entity2.string, "string1")
        keys = ndb.Query(kind="Data").fetch()
        self.assertEqual(entity2.field, "field1")
        self.assertEqual(entity2.string, "string1")
        entity3 = Data.getByFieldAndString("field1", "string1")
        self.assertEqual(entity3.dataId, data_id)
        entity4 = Data.getByDataId(data_id)
        self.assertEqual(entity4.field, "field1")
        self.assertEqual(entity4.string, "string1")

        keys5 = Data.fetchByFieldAndString("field1", "string2")
        self.assertEqual(len(keys5), 0)

        keys6 = Data.fetchByFieldAndString("field2", "string1")
        self.assertEqual(len(keys6), 0)

        entity5 = Data.prepare("field1", "string1")
        self.assertEqual(entity5.dataId, entity2.dataId)
        self.assertRaises(EntityExists, lambda: Data.create("field1", "string1"))

        entity2.deleteEntity()
        self.assertRaises(EntityNotFound, lambda: Data.getByFieldAndString("field1", "string1"))
        self.assertRaises(EntityNotFound, lambda: Data.getByDataId(data_id))

    def testDuplication(self):
        d1 = Data.create("f3", "s3", allow_duplication=True)
        self.assertRaises(EntityExists, lambda: Data.create("f3", "s3"))
        d2 = Data.create("f3", "s3", allow_duplication=True)
        self.assertTrue(d1.dataId != d2.dataId)
        self.assertRaises(EntityDuplicated, lambda: Data.getByFieldAndString("f3", "s3"))

    def testQueryByField(self):
        Data.create("f4", "s4")
        Data.create("f4", "s44")
        Data.create("f4", "s444")
        Data.create("f5", "s5")
        keys = Data.fetchByField("f4")
        self.assertEqual(len(keys), 3)
        for key in keys:
            self.assertIsInstance(key, ndb.Key)
            self.assertIsInstance(key.get(), Data)

        query = Data.queryByField("f4")
        self.assertIsInstance(query, ndb.Query)
        keys2 = query.fetch()
        for key2 in keys2:
            self.assertIsInstance(key, ndb.Key)
            self.assertIsInstance(key.get(), Data)

        query = Data.query(Data.field == "f4")
        self.assertIsInstance(query, ndb.Query)
        data_list = query.fetch()
        self.assertEqual(len(data_list), 3)
        for data in data_list:
            self.assertIsInstance(data, Data)
            self.assertEqual(data.field, "f4")

    def tearDown(self):
        data_list = Data.query().fetch()
        self.assertIsInstance(data_list, list)
        for d in data_list:
            if d is not None:
                self.assertIsInstance(d, Data)
                d.key.delete()

        client = Client()
        client.cas_reset()
        self.testbed.deactivate()


class _TestCaseNdb(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
