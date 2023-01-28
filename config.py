import os
from dotenv import load_dotenv


class Config(object):
    def __init__(self, dotenv_path: str = None):
        if dotenv_path is None:
            dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.LOG = os.getenv('DS_LOG', True)
        if self.LOG is not True:
            self.LOG = not self.LOG.lower() in ['false', 'no',  'n', 'not', 'never', 'nothing', 'none']
        self.SECRET_KEY = os.getenv('DS_SECRET_KEY')
        self.COMPANY_NAME = os.getenv('DS_COMPANY_NAME')
        self.COMPANY_SITE = os.getenv('DS_COMPANY_SITE')
        self.PER_PAGE = int(os.getenv('DS_PER_PAGE', 6))
        self.COMPANY_EMAILS = os.getenv('DS_COMPANY_EMAIL')
        self.COMPANY_NUMBERS = os.getenv('DS_COMPANY_NUMBER')
        self.COMPANY_DESCRIPTION = os.getenv('DS_COMPANY_DESCRIPTION')
        self.COMPANY_ADDRESS = os.getenv('DS_COMPANY_ADDRESS')
        self.SOCIAL_NETWORKS = os.getenv('DS_COMPANY_SOCIAL_NETWORKS')
        self.DELIVERY_MONEY = int(os.getenv('DS_DELIVERY_MONEY'))
        self.USER = os.getenv('DS_MYSQL_USER')
        self.DEV_TOKEN = os.getenv('DS_DEV_TOKEN')
        self.PASSWORD = os.getenv('DS_MYSQL_USER_PASSWORD')
        self.HOST = os.getenv('DS_MYSQL_HOST', "localhost")
        self.PORT = int(os.getenv('DS_MYSQL_PORT', 3306))
        self.DATABASE = os.getenv('DS_MYSQL_DATABASE')
        self.LOG_FILE_SIZE = int(os.getenv('DS_LOG_FILE_SIZE', 5024))
        self.MAX_LOGS_BACKUPS = os.getenv('DS_MAX_LOGS_BACKUPS', 10)
        self.MAX_SIZE_PHOTO = int(os.getenv('DS_MAX_SIZE_PHOTO', 5 * (1024 * 1024)))
        self.UPLOAD_FOLDER = 'App/static/avatars'
        self.UPLOAD_EXTENSIONS = ['.jpg', '.png', '.gif']
        self.BLUEPRINT_FOLDERS = ['errors', 'api', 'main']
        if self.SOCIAL_NETWORKS:
            temp_array = self.SOCIAL_NETWORKS.split("-")
            self.SOCIAL_NETWORKS = []
            for str_social_network in temp_array:
                if str_social_network.strip():
                    social_network = str_social_network.split(",")
                    name = social_network[0].strip()
                    link = social_network[1].strip()
                    self.SOCIAL_NETWORKS.append([name, link])
        if self.COMPANY_NUMBERS:
            temp_array = self.COMPANY_NUMBERS.split(",")
            self.COMPANY_NUMBERS = []
            for str_number in temp_array:
                number = str_number.strip()
                if number:
                    self.COMPANY_NUMBERS.append(number)
        if self.COMPANY_EMAILS:
            temp_array = self.COMPANY_EMAILS.split(",")
            self.COMPANY_EMAILS = []
            for str_email in temp_array:
                email = str_email.strip()
                if email:
                    self.COMPANY_EMAILS.append(email)
