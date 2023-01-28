import os
import sys
import mariadb
import importlib
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, cli

from config import Config


# Get config from env
config = Config()


# Connect to Database
try:
    conn = mariadb.connect(
        user=config.USER,
        password=config.PASSWORD,
        host=config.HOST,
        port=config.PORT,
        database=config.DATABASE
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()


def register_blueprints(app):
    """
    Automagically register all blueprints
    """
    for folder in config.BLUEPRINT_FOLDERS:
        app.register_blueprint(importlib.import_module(f'App.{folder}').bp)
    return None


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY
    app.config.from_object(config)
    # register all blueprints indicated by BLUEPRINT_FOLDERS
    register_blueprints(app)
    # Enable logging
    if config.LOG is True:
        logging.getLogger('werkzeug').disabled = True
        cli.show_server_banner = lambda *args: None
        # Disable flask messages
        logging.getLogger('werkzeug').disabled = True
        cli.show_server_banner = lambda *args: None
        # Logs
        if not os.path.exists('logs'):
            os.mkdir('logs')
        # Create rotating file log
        file_handler = RotatingFileHandler(
            'logs/website-delivery-system.log',
            maxBytes=config.LOG_FILE_SIZE,
            backupCount=config.MAX_LOGS_BACKUPS
        )
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Logger enabled")
        app.logger.info("Connection to database opened")
        app.logger.info("Website is up")
    return app
