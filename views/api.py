from sanic import Blueprint
from sanic.response import json

from models.models import Subscriber, Resources, session
from schemas.schemas import SubscribeSchema
from views.utils import marshal_with
from tasks.tasks import init_email

bp = Blueprint('api', url_prefix='/api/v1')


@bp.route('/subscribe/', methods=['POST'])
# @marshal_with(SubscribeSchema)
async def subscribe(request):
    nick_name = request.form.get('nick_name')
    email = request.form.get('email')
    resources = request.form.getlist('resources')
    new_resources = ','.join(resources)
    subscriber = Subscriber()
    subscriber.nick_name = nick_name
    subscriber.email = email
    subscriber.resources = new_resources
    session.add(subscriber)
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
    await init_email(resources)
    return json({'resp': 'ok'})


@bp.route('/resources/', methods=['GET'])
async def resources(request):
    resources_list = []
    for uuid, original, name in session.query(Resources.uuid, Resources.original, Resources.name).all()[:5]:
        resources_list.append({
            'id': uuid,
            'url': original,
            'name': name
        })
    return json(resources_list)
