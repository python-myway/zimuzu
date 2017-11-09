from marshmallow import Schema, fields


class EmailSchema(Schema):
    name = fields.Str()


class SubscribeSchema(Schema):
    pass
