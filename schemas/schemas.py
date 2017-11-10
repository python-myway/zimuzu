from ext.schemabase import Marshmallow


ma = Marshmallow()


class SubscribeSchema(ma.Schema):
    nick_name = ma.Str(required=True, error_messages={'required': '该字段必填'})
    email = ma.Email(required=True, error_messages={'required': '该字段必填', 'invalid': '字段格式不正确'})
    # resources = ma.Method('format_resources', deserialize='format_resources', required=True, error_messages={'required': '该字段必填'})

    # def format_resources(self, resources):
    #     return ','.join(resources)


class ResourceSchema(ma.Schema):
    id = ma.Str(attribute='uuid')
    url = ma.Str()
    name = ma.Str()
