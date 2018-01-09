from sanic import Sanic
from sqlalchemy import func

from ext.resp import Request, resp_error, resp_ok
from ext.schemabase import Marshmallow
from models import Subscriber, Resources, session
from tasks import init_email

app = Sanic(__name__, request_class=Request)
app.static('/static', './static')


# ======= Start of Schema ========
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
# ======= End of Schema ========


@app.middleware('response')
async def custom_header(request, response):
    """ 本地测试需要 """
    response.headers['Access-Control-Allow-Origin'] = '*'


@app.route('/subscribe/', methods=['POST'])
async def subscribe(request):
    schema = SubscribeSchema()
    data, error = schema.load(request.form)  # todo 传入空的字符串不能required不能识别
    if error:
        return resp_error(error)

    subscriber = Subscriber()
    subscriber.nick_name = data['nick_name']
    subscriber.email = data['email']
    subscriber.resources = data['resources']
    session.add(subscriber)
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
        return resp_error(e.args)
    email_ = await init_email(data['nick_name'], data['email'], data['resources'])
    if not email_:
        return resp_ok('您已经成功订阅')
    else:
        return resp_error(email_)


@app.route('/resources/', methods=['GET'])
async def resources(request):
    """
    todo 指定页数的查询
    """
    schema = ResourceSchema()
    query = session.query(Resources.id, Resources.uuid, Resources.original, Resources.name, Resources.owner).all()
    count = session.query(func.count('*')).select_from(Resources).scalar()
    data, error = schema.dump(query, many=True)
    if error:
        return resp_error(error)
    return resp_ok({'rows': data, 'total': int(count)})


if __name__ == '__main__':
    app.run(host='localhost', port=8300, workers=2, debug=True)
