from sanic.request import Request as _Request
from sanic.response import HTTPResponse

from json import dumps


iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))


class Request(_Request):
    """ copy from werkzeug"""

    def lists(self):
        for key, values in iteritems(dict, self):
            yield key, list(values)

    def to_dict(self, flat=True):
        if flat:
            return dict(iteritems(self))
        return dict(self.lists())


def resp_ok(data, status=200, headers=None, content_type="application/json", **kwargs):

    """
    :param data: 返回的数据
    :param status: Response code
    :param headers: Custom Headers
    :param content_type:
    :param kwargs: Remaining arguments that are passed to the json encoder
    :return:
    """
    body = {'data': data, 'msg': 'ok'}
    return HTTPResponse(dumps(body, **kwargs), headers=headers,
                        status=status, content_type=content_type)


def resp_error(data, status=200, headers=None, content_type="application/json", **kwargs):

    """
    :param data:
    :param status:
    :param headers:
    :param content_type:
    :param kwargs:
    :return:
    """
    body = {'data': data, 'msg': 'error'}
    return HTTPResponse(dumps(body, **kwargs), headers=headers,
                        status=status, content_type=content_type)


def resp_not_found(data, status=200, headers=None, content_type="application/json", **kwargs):

    """
    :param data:
    :param status:
    :param headers:
    :param content_type:
    :param kwargs:
    :return:
    """
    body = {'data': data, 'msg': 'notFound'}
    return HTTPResponse(dumps(body, **kwargs), headers=headers,
                        status=status, content_type=content_type)