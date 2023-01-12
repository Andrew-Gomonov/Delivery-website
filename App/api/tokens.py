import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request
from App.errors.api import APITokenError
from App import app


def dev_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if token is None:
            raise APITokenError('no developer token')
        if token != "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NzM2MzczNTMsImlhdCI6MTY3MzU1MDk1M" \
                    "ywic3ViIjotMTk2OX0.hB1eBrNKhg-fwsVvqzG4VtZ6jt7ks4uNOQW86aZWIxM":
            raise APITokenError('invalid token')
        return f(*args, **kwargs)
    return decorated


def generate_auth_token(sub, exp=86400):
    """Generates the Auth Token"""
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=exp),
            'iat': datetime.utcnow(),
            'sub': sub
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as error:
        return error
