from google.cloud import ndb


class EnvVar(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.TextProperty()

    @classmethod
    def add(cls, name, value):
        if cls._get_object(name):
            raise Exception('Already exists')
        with cls._ndb_client().context():
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
        with cls._ndb_client().context():
            obj.value = value
            obj.put()

    @classmethod
    def delete(cls, name):
        obj = cls._get_object(name)
        if not obj:
            raise Exception('Not found')
        with cls._ndb_client().context():
            obj.key.delete()

    @classmethod
    def _get_object(cls, name):
        with cls._ndb_client().context():
            return cls.query(cls.name == name).get()

    @staticmethod
    def _ndb_client():
        return ndb.Client()

