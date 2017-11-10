import marshmallow
import re
from marshmallow.utils import get_value as _get_value
from sanic.response import HTTPResponse

try:
    from ujson import dumps as json_dumps
except:
    from json import dumps as json_dumps

from ext.jsonbase import JSONDecoder


__all__ = [
    'Marshmallow',
    'Schema',
    'sanic_jsonify'
]


_tpl_pattern = re.compile(r'\s*<\s*(\S*)\s*>\s*')
sentinel = object()  # 不明白为什么要这个来设置bool值？


_MARSHMALLOW_VERSION_INFO = tuple(
    [int(part) for part in marshmallow.__version__.split('.') if part.isdigit()]
)

# marshmallow>=3.0 改变了obj和attr参数的位置，哈哈哈
if _MARSHMALLOW_VERSION_INFO[0] >= 3:
    get_value = _get_value
else:
    def get_value(obj, attr, *args, **kwargs):
        return _get_value(attr, obj, *args, **kwargs)


def sanic_jsonify(body, status=200, headers=None, content_type="application/json", **kwargs):
    """
    重写了sanic的sanic.response：json
    :param body: Response data to be serialized.
    :param status: Response code.
    :param headers: Custom Headers.
    :param kwargs: Remaining arguments that are passed to the json encoder.
    :param content_type
    """
    return HTTPResponse(json_dumps(body, cls=JSONDecoder, **kwargs), headers=headers,
                        status=status, content_type=content_type)


class Schema(marshmallow.Schema):

    def jsonify(self, obj, many=sentinel, *args, **kwargs):
        if many is sentinel:
            many = self.many
        data, error = self.dump(obj, many=many)
        if error:
            return sanic_jsonify(error, *args, **kwargs)
        return sanic_jsonify(data, *args, **kwargs)


def _attach_fields(obj):
    """绑定所有marshmallow的fields类, 包括schemabase自己的fields
    """
    for attr in marshmallow.fields.__all__:
        if not hasattr(obj, attr):
            setattr(obj, attr, getattr(marshmallow.fields, attr))
    # todo schemabase自己的fields
    # for attr in fields.__all__:
    #     setattr(obj, attr, getattr(fields, attr))


class Marshmallow:

    def __init__(self, app=None):
        self.Schema = Schema
        _attach_fields(self)
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['schemabase'] = self