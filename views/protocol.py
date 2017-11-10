from sanic.server import HttpProtocol, CIDict
from sanic.request import Request as _Request
from sanic.response import text, json


iteritems = lambda d, *args, **kwargs: iter(d.items(*args, **kwargs))


class Request(_Request):

    def lists(self):
        for key, values in iteritems(dict, self):
            yield key, list(values)

    def to_dict(self, flat=True):
        if flat:
            return dict(iteritems(self))
        return dict(self.lists())


class JSONHttpProtocol(HttpProtocol):
    def on_headers_complete(self):
        remote_addr = self.transport.get_extra_info('peername')
        if remote_addr:
            self.headers.append(('Remote-Addr', '%s:%s' % remote_addr))

        self.request = Request(
            url_bytes=self.url,
            headers=CIDict(self.headers),
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode()
        )

    def write_response(self, response):
        if isinstance(response, str):
            response = text(response)
        elif isinstance(response, (list, dict)):
            response = {'rs': response}
        if isinstance(response, dict):
            response = json(response)
        return super().write_response(response)