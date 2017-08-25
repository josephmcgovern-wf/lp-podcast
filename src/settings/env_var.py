from google.appengine.ext import ndb


class EnvVar(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.TextProperty()

    @classmethod
    def add(cls, name, value):
        found = False
        try:
            cls.get(name)
            found = True
        except:
            pass
        if found:
            raise Exception('Already exists')
        obj = cls(name=name, value=value)
        obj.put()

    @classmethod
    def get(cls, name):
        obj = cls.query(cls.name == name).get()
        if not obj:
            raise Exception('Not found')
        return obj.value
