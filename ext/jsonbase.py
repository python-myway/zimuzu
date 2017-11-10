import io
import uuid
from datetime import date, datetime
from time import gmtime
import json as _json


_slash_escape = '\\/' not in _json.dumps('/')


__all__ = ['dump', 'dumps', 'load', 'loads', 'JSONDecoder', 'JSONEncoder']


def _dump_date(d, delim):
    """ 时间为UTC时间 """

    if d is None:
        d = gmtime()
    elif isinstance(d, datetime):
        d = d.utctimetuple()
    elif isinstance(d, (int, float)):
        d = gmtime(d)
    return '%s, %02d%s%s%s%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[d.tm_wday],
        d.tm_mday, delim,
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dec')[d.tm_mon-1],
        delim, str(d.tm_year), d.tm_hour, d.tm_min, d.tm_sec
    )


def http_date(timestamp=None):
    """Formats the time to match the RFC1123 date format.
    Outputs a string in the format ``Wdy, DD Mon YYYY HH:MM:SS GMT``.
    :param timestamp: If provided that date is used, otherwise the current.
    """
    return _dump_date(timestamp, ' ')


def _wrap_reader_for_text(fp, encoding):
    if isinstance(fp.read(0), bytes):
        fp = io.TextIOWrapper(io.BufferedReader(fp), encoding)
    return fp


def _wrap_writer_for_text(fp, encoding):
    try:
        fp.write('')
    except TypeError:
        fp = io.TextIOWrapper(fp, encoding)
    return fp


class JSONEncoder(_json.JSONEncoder):
    """ 重写default方法以支持时间解析，若要支持其他扩展，也是重写default方法
        不支持html解析
    """

    def default(self, o):
        if isinstance(o, date):
            return http_date(o.timetuple())
        if isinstance(o, uuid.UUID):
            return str(o)
        return _json.JSONEncoder.default(self, o)


class JSONDecoder(_json.JSONDecoder):
    """ 未做处理 """


def _dump_arg_defaults(kwargs, current_app=None):
    """Inject default arguments for dump functions."""
    if current_app:
        kwargs.setdefault('cls', current_app.config['JSON_ENCODER'])
        if not current_app.config['JSON_AS_ASCII']:
            kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('sort_keys', current_app.config['JSON_SORT_KEYS'])
    else:
        kwargs.setdefault('sort_keys', True)
        kwargs.setdefault('cls', JSONEncoder)


def _load_arg_defaults(kwargs, current_app=None):
    """Inject default arguments for load functions."""
    if current_app:
        kwargs.setdefault('cls', current_app.config['JSON_ENCODER'])
    else:
        kwargs.setdefault('cls', JSONDecoder)


def dumps(obj, **kwargs):
    """Serialize ``obj`` to a JSON formatted ``str`` by using the application's
    configured encoder (:attr:`~flask.Flask.json_encoder`) if there is an
    application on the stack.

    This function can return ``unicode`` strings or ascii-only bytestrings by
    default which coerce into unicode strings automatically.  That behavior by
    default is controlled by the ``JSON_AS_ASCII`` configuration variable
    and can be overridden by the simplejson ``ensure_ascii`` parameter.
    """
    _dump_arg_defaults(kwargs)
    encoding = kwargs.pop('encoding', None)
    rv = _json.dumps(obj, **kwargs)
    return rv


def dump(obj, fp, **kwargs):
    """Like :func:`dumps` but writes into a file object."""
    _dump_arg_defaults(kwargs)
    encoding = kwargs.pop('encoding', None)
    if encoding is not None:
        fp = _wrap_writer_for_text(fp, encoding)
    _json.dump(obj, fp, **kwargs)


def loads(s, **kwargs):
    """Unserialize a JSON object from a string ``s`` by using the application's
    configured decoder (:attr:`~flask.Flask.json_decoder`) if there is an
    application on the stack.
    """
    _load_arg_defaults(kwargs)
    if isinstance(s, bytes):
        s = s.decode(kwargs.pop('encoding', None) or 'utf-8')
    return _json.loads(s, **kwargs)


def load(fp, **kwargs):
    """Like :func:`loads` but reads from a file object.
    """
    _load_arg_defaults(kwargs)
    fp = _wrap_reader_for_text(fp, kwargs.pop('encoding', None) or 'utf-8')
    return _json.load(fp, **kwargs)


def htmlsafe_dumps(obj, **kwargs):
    rv = dumps(obj, **kwargs) \
        .replace(u'<', u'\\u003c') \
        .replace(u'>', u'\\u003e') \
        .replace(u'&', u'\\u0026') \
        .replace(u"'", u'\\u0027')
    if not _slash_escape:
        rv = rv.replace('\\/', '/')
    return rv


def htmlsafe_dump(obj, fp, **kwargs):
    pass

