from google.appengine._internal.django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import DataId, Field, FieldAndString, Range,Recent

class _Index(webapp.RequestHandler):
    def get(self):
        map = []
        map.append(DataId.map)
        map.append(Field.map)
        map.append(FieldAndString.map)
        map.append(Range.map)
        map.append(Recent.map)
        self.response.out.write(simplejson.dumps(map))
        return

if __name__ == "__main__":
    app = webapp.WSGIApplication ([("/api/Data", _Index)])
    run_wsgi_app(app)


# if __name__ == "__main__":
#     import DataId
#     import DeleteUnused
#     import DuplicationCheck
#     import Field
#     import FieldAndString
#     import KeyId
#     import Range
#     import Recent
#     import UrlMap
#     #from lib.gae import run_wsgi_app
#     #run_wsgi_app(UrlMap.UrlMap)
#     print (UrlMap.UrlMap)
