from flask import Blueprint

bp = Blueprint('api', __name__)

from App.api import routes