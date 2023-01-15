class Config(object):
    LOG = True
    TESTING = True
    SECRET_KEY = "putin_huilo"
    DELIVERY_MONEY = 30
    USER = "andrey"
    PASSWORD = "peligas5"
    HOST = "localhost"
    PORT = 3306
    DATABASE = "livrareTiande"
    MAX_SIZE_PHOTO = 5 * (1024 * 1024)  # max 5 mb
    UPLOAD_FOLDER = 'App/static/avatars'
    UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
