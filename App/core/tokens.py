from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import request, current_app

from App.errors.api import APITokenError


def dev_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if token is None:
            raise APITokenError('no developer token')
        if token != current_app.config['DEV_TOKEN']:
            raise APITokenError('invalid token')
        return f(*args, **kwargs)
    return decorated


def generate_auth_token(sub, exp=3600):
    """Generates the Auth Token"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=exp),
            'iat': datetime.utcnow(),
            'sub': sub
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as error:
        return error
