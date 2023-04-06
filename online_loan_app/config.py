import copy
import os


class configuration():
    def __init__(self, mode):
        self.MYSQL_USER = 'root'
        self.MYSQL_PASSWORD = 'mysql'
        self.DB_HOST_NAME = 'localhost'
        self.DB_NAME = 'dev'

    def set_application_environement_settings(self, mode):
        print('Application mode :', mode)
        self.MODE = mode
        if mode == 'development':
            self.MYSQL_USER = 'root'
            self.MYSQL_PASSWORD = 'mysql'
            self.DB_HOST_NAME = 'localhost'
            self.DB_NAME = 'dev'

    def as_dict(self):
        # we return a deepcopy to avoid unexpected side effects
        return copy.deepcopy(self.__dict__)


mode = 'development'
CONFIGURATION = configuration(mode)
http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']
