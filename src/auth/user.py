from flask_login import UserMixin
from google.cloud import ndb


class UserModel(ndb.Model):
    email = ndb.StringProperty(required=True)


class User(UserMixin):
    def __init__(self, id_, email):
        self.id = id_
        self.email = email

    @classmethod
    def get(cls, user_id):
        with ndb.Client().context():
            um = UserModel.get_by_id(user_id)
        if not um:
            return None
        return cls(um.key.id(), um.email)

    @classmethod
    def get_or_add(cls, user_id, email):
        u = cls.get(user_id)
        if not u:
            with ndb.Client().context():
                um = UserModel(id=user_id, email=email)
                um.put()
            u = cls(user_id, email)
        return u
