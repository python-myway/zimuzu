import json as b_json
from sanic import Blueprint
from sanic.response import json

from models.models import Subscriber, Resources, session
from schemas.schemas import SubscribeSchema, ResourceSchema
from views.utils import marshal_with
from tasks.tasks import init_email

bp = Blueprint('api', url_prefix='/api/v1')


@bp.route('/subscribe/', methods=['POST'])
# @marshal_with(SubscribeSchema)
async def subscribe(request):
    schema = SubscribeSchema()
    data, error = schema.load(request.form)  # todo 传入空的字符串不能required不能识别
    # if error:
    #     return json({'resp': 'error',
    #
    #                   'msg': error})
    if not data['nick_name']:
        return json({'resp': 'error', 'msg': '该字段必填'}, headers={'Access-Control-Allow-Origin': '*'})
    try:
        data['nick_name']
    except KeyError as e:
        return json({'resp': 'error', 'msg': e.args}, headers={'Access-Control-Allow-Origin': '*'})
    resources = request.form.getlist('resources[]', [])
    if not resources:
        return json({'resp': 'error', 'msg': '该字段必填'}, headers={'Access-Control-Allow-Origin': '*'})
    subscriber = Subscriber()
    subscriber.nick_name = data['nick_name']
    subscriber.email = data['email']
    subscriber.resources = ','.join(resources)
    session.add(subscriber)
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
        return json({'resp': 'error',
                     'msg': str(e.args)}, headers={'Access-Control-Allow-Origin': '*'})
    await init_email(resources)
    return json({'resp': 'ok'}, headers={'Access-Control-Allow-Origin': '*'})


# @bp.route('/resources/', methods=['GET'])
# # @marshal_with(ResourceSchema)
# async def resources(request):
#     schema = ResourceSchema()
#     query = session.query(Resources.uuid, Resources.original, Resources.name).all()
#     return schema.jsonify(query, many=True, headers={'Access-Control-Allow-Origin': '*/*'})


@bp.route('/resources/', methods=['GET'])
# @marshal_with(ResourceSchema)
async def resources(request):
    query_list = []
    query = session.query(Resources).limit(50)
    for q in query:
        query_list.append({
            'uuid': q.uuid,
            'recordId': q.id,
            'name': q.name,
            'owner': q.owner,
            'originalUrl': q.original
        })
    table_dict = {
        'total': 10,
        'rows': query_list
    }
    return json(table_dict, headers={'Access-Control-Allow-Origin': '*'})
