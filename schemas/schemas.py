from ext.schemabase import Marshmallow


ma = Marshmallow()


class SubscribeSchema(ma.Schema):
    nick_name = ma.Str(required=True, error_messages={'required': '该字段必填'})
    email = ma.Email(required=True, error_messages={'required': '该字段必填', 'invalid': '字段格式不正确'})
    resources = ma.Str(required=True, error_messages={'required': '该字段必填'})


class ResourceSchema(ma.Schema):
    uuid = ma.Str()
    id = ma.Str()
    url = ma.Str(attribute='original')
    name = ma.Str()
    owner = ma.Str()
