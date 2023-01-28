from App.core.utils import LOG
import traceback
from flask import render_template
from flask import jsonify
from App.errors.api import APIError
from App.errors import bp


@bp.app_errorhandler(404)
def page_not_found(error):
    LOG.info(error)
    return render_template('errors/page-not-found.html'), 404


@bp.app_errorhandler(APIError)
def api_error(error):
    LOG.error(error.message)
    return jsonify({"code": error.code, "message": error.message})


@bp.app_errorhandler(Exception)
def server_error(error):
    LOG.error(error)
    # log traceback
    traceback.print_exc()
    return render_template('errors/server-error.html'), 500


@bp.app_errorhandler(403)
def forbidden(error):
    LOG.warning(error)
    return render_template('errors/forbidden.html'), 403
