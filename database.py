import os
import sys
import time

from sqlalchemy import create_engine

from settings import CONFIGURATION


def get_mysql_connection(echo=False, username=None, password=None):
    print('connecting to db')
    while True:
        try:
            ssl_args = {'ssl_ca': 'BaltimoreCyberTrustRoot.crt.pem'}
            connection_string = get_mysql_connectionstring(username=None, password=None)
            print(connection_string)
            engine = create_engine(connection_string, echo=echo)
            return engine
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(sys.exc_info())
            print('Retrying in 60 secs')
            time.sleep(60)


def get_mysql_username():
    return CONFIGURATION.MYSQL_USER;


def get_mysql_password():
    return CONFIGURATION.MYSQL_PASSWORD;


def get_mysql_host_name():
    return CONFIGURATION.DB_HOST_NAME;


def get_mysqldbname():
    return CONFIGURATION.DB_NAME;


def get_mysql_connectionstring(username=None, password=None):
    if username is None:
        user = get_mysql_username()

    if password is None:
        password = get_mysql_password()

    hostname = get_mysql_host_name()
    dbname = get_mysqldbname()
    return 'mysql://' + user + ':' + password + '@' + hostname + '/' + dbname + '?ssl=true'
