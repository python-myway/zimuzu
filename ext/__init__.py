from .utils import FakeApp
from .modelbase import SQLAlchemy


fake_app = FakeApp()


fake_app.make_config({
    'SQLALCHEMY_DATABASE_URI': 'mysql+mysqldb://root:123456@localhost/zimuzu?charset=utf8',
    'SQLALCHEMY_ECHO': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': True,
})


db = SQLAlchemy(fake_app)
