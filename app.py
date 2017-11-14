from sanic import Sanic

from views.api import bp
from views.protocol import JSONHttpProtocol, Request


app = Sanic(__name__, request_class=Request)
app.blueprint(bp)
app.static('/static', './static')


# @app.middleware('request')
# async def halt_request(request):
#     request.start = request.args.get('start', 0)
#     request.limit = request.args.get('limit', 10)


if __name__ == '__main__':
    app.run(host='localhost', port=8300, workers=1, debug=True)