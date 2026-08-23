from flask import Blueprint, session, request
from app.models import User, db, environment
from app.forms import LoginForm
from app.forms import SignUpForm
from flask_login import current_user, login_user, logout_user

import os
import secrets as secrets_module

import requests
from flask import abort, redirect
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from tempfile import NamedTemporaryFile
import json
from oauthlib.oauth2.rfc6749.errors import AccessDeniedError

CLIENT_SECRET = os.getenv('CLIENT_SECRET')
CLIENT_ID = os.getenv('CLIENT_ID')
BASE_URL = os.getenv('SERVER_BASE_URL')
REACT_APP_BASE_URL = os.getenv('REACT_APP_BASE_URL')

CLIENT_SECRETS = {
  "web": {
    "client_id": CLIENT_ID,
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": CLIENT_SECRET,
    "redirect_uris": [
      f"{BASE_URL}/api/auth/callback"
    ]
  }
}

# Only relax oauthlib's HTTPS requirement outside of production.
if os.environ.get('FLASK_ENV') != 'production':
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def build_flow():
    """
    Build a fresh Flow per request. A module-level Flow is stateful
    (fetch_token/credentials mutate it), so sharing one instance across
    requests lets concurrent OAuth logins clobber each other's state.
    """
    with NamedTemporaryFile(mode="w") as secrets_file:
        json.dump(CLIENT_SECRETS, secrets_file)
        secrets_file.flush()
        return Flow.from_client_secrets_file(
            client_secrets_file=secrets_file.name,
            scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
            redirect_uri=f"{BASE_URL}/api/auth/callback"
        )


auth_routes = Blueprint('auth', __name__)
def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f'{field} : {error}')
    return errorMessages


@auth_routes.route('/')
def authenticate():
    """
    Authenticates a user.
    """
    if current_user.is_authenticated:
        return current_user.to_dict_self()
    return {'errors': ['Unauthorized']}


@auth_routes.route('/login', methods=['POST'])
def login():
    """
    Logs a user in
    """
    form = LoginForm()
    # Get the csrf_token from the request cookie and put it into the
    # form manually to validate_on_submit can be used
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        # Add the user to the session, we are logged in!
        user = User.query.filter(User.email == form.data['email']).first()
        login_user(user)
        return user.to_dict_self()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@auth_routes.route('/logout')
def logout():
    """
    Logs a user out
    """
    logout_user()
    return {'message': 'User logged out'}


@auth_routes.route('/signup', methods=['POST'])
def sign_up():
    """
    Creates a new user and logs them in
    """
    form = SignUpForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    
    if form.validate_on_submit():
        user = User(
            username=form.data['username'],
            email=form.data['email'],
            password=form.data['password'],
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return user.to_dict_self()
    return {'errors': validation_errors_to_error_messages(form.errors)}, 401


@auth_routes.route('/unauthorized')
def unauthorized():
    """
    Returns unauthorized JSON when flask-login authentication fails
    """
    return {'errors': ['Unauthorized']}, 401

@auth_routes.route('/demo_login')
def demo_login():
    """
    Logs in as the seeded Demo user with no credentials, so the app can be
    tried locally without setting up Google OAuth. Disabled in production -
    only OAuth/password login work there.
    """
    if environment == 'production':
        return {'errors': ['Not found']}, 404

    user = User.query.filter(User.email == 'emo@aa.io').first()
    if user is None:
        user = User(username='Demo', email='emo@aa.io', password='password')
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return user.to_dict_self()


@auth_routes.route("/oauth_login")
def oauth_login():
    flow = build_flow()
    authorization_url, state = flow.authorization_url(prompt="select_account consent")
    referrer = request.headers.get('Referer')
    session["referrer"] = referrer
    session["state"] = state
    return redirect(authorization_url)


@auth_routes.route("/callback")
def callback():
    try:
        if session.get("state") is None or session["state"] != request.args.get("state"):
            abort(500)  # State does not match / missing - possible CSRF

        flow = build_flow()
        flow.fetch_token(authorization_response=request.url)

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=token_request,
            audience=CLIENT_ID
        )

        temp_email = id_info.get('email')
        user = User.query.filter(User.email == temp_email).first()

        if not user:
            email_arr = temp_email.split('@')
            user = User(
                    email=temp_email,
                    # Random, never-revealed password: OAuth accounts must not
                    # be logable into via the regular email/password form.
                    password=secrets_module.token_urlsafe(32),
                    username=email_arr[0],
                )

            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(f"{REACT_APP_BASE_URL}/stocks")
    except AccessDeniedError:
        return redirect(REACT_APP_BASE_URL)
