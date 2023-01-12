import atexit
import os
import sys
import mariadb
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, cli
from config import Config


app = Flask(__name__)
app.config.from_object(Config)

# Disable console messages on the Flask server, if it is not it is not testing
if Config.TESTING is False:
    logging.getLogger('werkzeug').disabled = True
    cli.show_server_banner = lambda *args: None


if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/website-delivery-system.log', maxBytes=1048576, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Connect to Database
try:
    conn = mariadb.connect(
        user=Config.USER,
        password=Config.PASSWORD,
        host=Config.HOST,
        port=Config.PORT,
        database=Config.DATABASE
    )
except mariadb.Error as e:
    app.logger.critical(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()


@atexit.register
def goodbye():
    conn.close()
    app.logger.info("Connection to database closed")


app.logger.info('Connection to database opened')
app.logger.info('Website is launched')

from App import routes, errors, restApi
