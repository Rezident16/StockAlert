from flask import Blueprint, jsonify, session, request
from flask_login import login_required,current_user
from app.models import User
from app.forms import SignUpForm
from app.models import *
from app.forms import *

user_routes = Blueprint('users', __name__)


@user_routes.route('/')
@login_required
def users():
    """
    Query for all users and returns them in a list of user dictionaries
    """
    users = User.query.all()
    return {'users': [user.to_dict_self() for user in users]}




@user_routes.route('/current')
@login_required
def current(id):
    """
    Query for a user by id and returns that user in a dictionary
    """
    user = User.query.get(current_user.id)
    return user.to_dict_self()

@user_routes.route('/<int:userId>')
def user(userId):
    """
    Query for a user by id and returns that user in a dictionary
    """
    try:
        user = User.query.get(userId)
    except AttributeError:
        return None
    return user.to_dict_self()
