import os
import json

from flask import Flask
from flask import jsonify
from flask import request
from flask import session

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from csh_ldap import CSHLDAP

from mizu import config

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})

app.config.from_object(config)
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    app.config.from_pyfile(os.path.join(os.getcwd(), 'config.py'))

app.secret_key = app.config['SECRET_KEY']

db = SQLAlchemy(app)
migrate = Migrate(app, db)

mock_db = None
if os.path.exists(os.path.join(os.getcwd(), 'mock.json')):
    with open('mock.json', 'r') as f:
        mock_db = json.load(f)

from mizu.models import Machine
from mizu.models import Item
from mizu.models import Slot
from mizu.models import Temp
from mizu.models import Log

ldap = CSHLDAP(app.config['LDAP_BIND_DN'],
               app.config['LDAP_BIND_PW'])

from mizu.auth import check_token

from mizu.drinks import drinks_bp
from mizu.items import items_bp
from mizu.users import users_bp
from mizu.slots import slots_bp

from mizu.data_adapters import SqlAlchemyAdapter, MockAdapter

app.register_blueprint(drinks_bp)
app.register_blueprint(items_bp)
app.register_blueprint(users_bp)
app.register_blueprint(slots_bp)

@app.route('/')
def hello_world():
    return 'hello world'

@app.errorhandler(404)
def handle_404(e):
    error = {
        "message": "What you're looking for does not exist, like a drink admin when drink is empty",
        "error": str(e),
        "errorCode": 404,
    }

    return jsonify(error), 404

@app.errorhandler(500)
def handle_500(e):
    error = {
        "message": "The drink server encountered an error, it was more than likely your fault",
        "error": str(e),
        "errorCode": 500,
    }

    return jsonify(error), 500

@app.after_request
def allow_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE'
    return response

