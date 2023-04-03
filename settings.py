import copy
import os


class configuration():
    def __init__(self, mode):
        self.MODE = mode
        self.MYSQL_USER = None
        self.MYSQL_PASSWORD = None
        self.DB_HOST_NAME = None
        self.DB_NAME = None

    def set_application_environement_settings(self, mode):
        print('Application mode :', mode)
        self.MODE = mode
        if mode == 'development':
            self.MYSQL_USER = 'dev_user'
            self.MYSQL_PASSWORD = 'abcd@1234'
            self.DB_HOST_NAME = 'localhost'
            self.DB_NAME = ''

    def as_dict(self):
        # we return a deepcopy to avoid unexpected side effects
        return copy.deepcopy(self.__dict__)


mode = os.environ['MODE']
CONFIGURATION = configuration(mode)
http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']
