from google.appengine.ext import ndb


class EnvVar(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.TextProperty()

    @classmethod
    def add(cls, name, value):
        if cls._get_object(name):
            raise Exception('Already exists')
        obj = cls(name=name, value=value)
        obj.put()

    @classmethod
    def get(cls, name):
        obj = cls._get_object(name)
        if not obj:
            raise Exception('Not found')
        return obj.value

    @classmethod
    def update(cls, name, value):
        obj = cls._get_object(name)
        if not obj:
            raise Exception('Not found')
        obj.value = value
        obj.put()

    @classmethod
    def delete(cls, name):
        obj = cls._get_object(name)
        if not obj:
            raise Exception('Not found')
        obj.key.delete()

    @classmethod
    def _get_object(cls, name):
        return cls.query(cls.name == name).get()
