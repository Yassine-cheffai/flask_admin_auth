from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, session
from flask import url_for, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]k'
oauth = OAuth(app)

oauth.register(
    name='twitter',
    client_id='oYopD4C3hOBykfVpgstgXp3cc',
    client_secret='bZcoU2f7JYKp2L25mqArXdKUNlp7hbeEEnKq6TeLw6y9JgQf30',
    request_token_url='https://api.twitter.com/oauth/request_token',
    request_token_params=None,
    access_token_url='https://api.twitter.com/oauth/access_token',
    access_token_params=None,
    authorize_url='https://api.twitter.com/oauth/authenticate',
    authorize_params=None,
    api_base_url='https://api.twitter.com/1.1/',
    client_kwargs=None,
)


@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.twitter.authorize_access_token()
    resp = oauth.twitter.get('account/verify_credentials.json')
    profile = resp.json()
    # do something with the token and profile
    session['profile'] = profile
    return redirect('/')

# @app.route('/logout')
# def logout():
#     del session['profile']
#     return redirect('/')

@app.route('/')
def hello():
    return 'hello world'




















from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

db.create_all()

def is_authenticated():
    return session.get('profile', False)

class AuthMixin(object):

    def is_accessible(self):
        return is_authenticated()

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class MyModelView(AuthMixin, ModelView):
    pass

admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(MyModelView(User, db.session))

# admin.add_link(MenuLink(name='Logout', endpoint='logout'))
