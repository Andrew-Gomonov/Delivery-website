from functools import wraps

import jwt
from flask import request, session, redirect, url_for, current_app
from user_agents import parse

from App.core.models import User
from App.errors.api import APINotFoundError


def only_admins(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['sub']
        try:
            user = User(user_id)
            if user.is_admin != 1:
                return redirect(url_for('main.index'))
        except APINotFoundError:
            redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def choice_template(desktop_template: str, mobile_template: str):
    """
    choose a template for the user to give him a mobile template or desktop template
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ua_str = request.headers.get('User-Agent')
            user_agent = parse(ua_str)
            if user_agent.is_mobile is True:
                kwargs['template'] = mobile_template
            else:
                kwargs['template'] = desktop_template
            return f(*args, **kwargs)

        return wrapper

    return decorator


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if token is None:
            return redirect(url_for('main.login_page'))
        try:
            User(jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['sub'])
        except jwt.exceptions.InvalidTokenError:
            return redirect(url_for('main.login_page'))
        except APINotFoundError:
            return redirect(url_for('main.login_page'))
        return f(*args, **kwargs)
    return decorated
