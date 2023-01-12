from flask import render_template
from App import app
from flask import jsonify
from App.errors.api import APIError


@app.errorhandler(404)
def page_not_found(error):
    app.logger.info(error)
    return render_template('errors/page-not-found.html'), 404


@app.errorhandler(APIError)
def api_error(error):
    app.logger.error(error.message)
    return jsonify({"code": error.code, "message": error.message})


@app.errorhandler(500)
def server_error(error):
    app.logger.error(error)
    return render_template('errors/server-error.html'), 500


@app.errorhandler(403)
def forbidden(error):
    app.logger.warning(error)
    return render_template('errors/forbidden.html'), 403
