from marshmallow import fields

from src.schema import BaseObject, BaseSchema

# TODO this file is incomplete
# Once this project has been upgraded, download marshmallow and use it


class Episode(BaseObject):

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(k, v) for k, v in self.__dict__.items()]),
        )


class EpisodeSchema(BaseSchema):
    OBJECT_CLS = Episode
    audio_file_length = fields.Integer(required=True)
    audio_file_url = fields.StringProperty(required=True)
    date_recorded = fields.Date(required=True)
    duration = fields.Float(required=True)
