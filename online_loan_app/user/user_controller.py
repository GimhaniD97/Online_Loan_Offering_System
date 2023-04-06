import binascii
import datetime
import hashlib
import json
import sys
import traceback
import uuid

from django.http import HttpResponse
from rest_framework.decorators import api_view
from sqlalchemy import func
from sqlalchemy.orm import Session
import sqlalchemy as db

from logs import logging_service
from online_loan_app.database import get_mysql_connection, call_store_procedure_get
from online_loan_app.models import User, UserRole
from online_loan_app.user.password_controller import create_hash_password
from online_loan_app.user.user import UserModel

engine = get_mysql_connection()


@api_view(['POST'])
def add_new_user(user_role, first_name, last_name, user_name, password, email, dob, is_admin):
    hashed_password, salt_user = create_hash_password(password)
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_login_controller', log_id)
    try:
        user_id = Session.query(func.max(User.UserId)).scalar()
        user = User(
            UserId=(user_id + 1),
            UserRoleId=user_role,
            UserFname=first_name,
            UserLname=last_name,
            UserName=user_name,
            AccessToken=hashed_password,
            Password=hashed_password,
            UserEmail=email,
            UserDob=dob,
            IsAdmin=is_admin,
            CreatedBy='',
            CreatedDateTime=datetime.datetime.now(),
            ModifiedBy='',
            ModifiedDateTime=''
        )
        Session.add(user)

        user_id = user.user_add()

        return user_id + 1

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception("{} Internal server error - add new user from database {}".format(log_id, e))




    finally:
        engine.dispose()


def validate_user(access_token):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_controller', log_id)
    try:
        uid = call_store_procedure_get('validate_user', access_token)
        if uid == '':
            return None
        elif uid != '':
            return uid

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception('{} Internal Server Error - Token Verification {}'.format(log_id, e))


def get_all_users(arg_type, input_para, engine):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_login_controller', log_id)
    connection = engine.connect()
    try:
        metadata = db.MetaData()
        user_data = db.Table('user', metadata, autoload=True, autoload_with=engine)

        # use ORM query according to the arg_type
        if arg_type == 'user':
            query = db.select([user_data]).where(user_data.columns.UserName == input_para)
        elif arg_type == 'token':
            query = db.select([user_data]).where(user_data.columns.AccessToken == input_para)
        elif arg_type == 'email':
            query = db.select([user_data]).where(user_data.columns.UserEmail == input_para)

        ResultProxy = connection.execute(query)
        ResultSet = ResultProxy.fetchall()

        return ResultSet

    except Exception as e:
        logging.error('[{}]'.format(e))
        raise Exception('{} Internal Server Error - Retrieve all users from database {}'.format(log_id, e))

    finally:
        connection.close()
        engine.dispose()


def verify_password(hashed_password, provided_password, user_salt):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('password_controller', log_id)
    try:
        salt = hashlib.sha256(user_salt.encode('utf-8')).hexdigest().encode('ascii')
        pwd_hash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt, 100000)
        pwd_hash = binascii.hexlify(pwd_hash)
        return hashed_password == (salt + pwd_hash).decode('ascii')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        traceback.print_exc()
        logging.error('[{}]'.format(str(e)))
        raise Exception('Internal Server Error - verify password_' + str(e))


def get_role_name(role_id, engine):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_license_controller', log_id)
    try:
        session = Session(autocommit=True, bind=engine, expire_on_commit=False)
        with session.begin():
            role_name = session.query(User.UserRoleId).filter(UserRole.UserRoleId == role_id).first()
    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception("{} Internal server error - get role name from database {}".format(log_id, e))
    finally:
        engine.dispose()
    return role_name[0]



