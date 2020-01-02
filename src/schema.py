from marshmallow import Schema, post_load, EXCLUDE


class BaseSchema(Schema):
    """
    Base schema class.

    Base schema class for all schemas to subclass if they produce an object
    from JSON data.
    """

    OBJECT_CLS = None

    # Add this so all fields passed into a schema.load that are not declared in
    # the schema definition are ignored instead of raising a validation error
    class Meta:
        unknown = EXCLUDE

    @post_load
    def make_obj(self, data, **kwargs):
        """
        Create an object from a dictionary.

        This function is automatically called by Schema().load(data).
        """
        return self.OBJECT_CLS(**data)


class BaseObject(object):
    """Base object class."""

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ", ".join(["{}={}".format(k, v) for k, v in self.__dict__.items()]),
        )
