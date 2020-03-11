import jwt
from flask import Blueprint, url_for, request, session, redirect
from authlib.integrations.flask_client import OAuth
from flask import Flask

APP_KEY = '...'
APP_SECRET = '...'
ALLOWED_IDS = ['user@domain.com']

admin_auth_blueprint = Blueprint('admin_auth', __name__)

app = Flask(__name__)
oauth = OAuth(app)

azure = oauth.register(
    'azure',
    consumer_key=APP_KEY,
    consumer_secret=APP_SECRET,
    request_token_params={'scope': 'openid profile email'},
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize')


def is_authenticated():
    return session.get('admin_authenticated', False)


@admin_auth_blueprint.route('/')
def login():
    if request.args.get('code'):
        response = azure.authorized_response()
        id_token = jwt.decode(response['id_token'], verify=False)
        id = id_token.get('email') or id_token.get('preferred_username')
        if id in ALLOWED_IDS:
            session['admin_authenticated'] = id
            return redirect(url_for('admin.index'))
        return 'No access', 403
    else:
        callback_url = url_for('admin_auth.login', _external=True)
        return azure.authorize(callback=callback_url)


@admin_auth_blueprint.route('/logout')
def logout():
    del session['admin_authenticated']
    return redirect('/')



from flask import Flask, escape, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app.register_blueprint(admin_auth_blueprint)


class AuthMixin(object):

    def is_accessible(self):
        return is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.login'))


class MyModelView(AuthMixin, ModelView):
    pass


@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'
