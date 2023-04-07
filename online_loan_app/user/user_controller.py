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

from online_loan_app.logs import Logger
from online_loan_app.database import get_mysql_connection
from online_loan_app.models import User
from online_loan_app.user.user import UserModel

engine = get_mysql_connection()

logger = Logger()


@api_view(['POST'])
def create_new_user(request):
    logger.info('add user endpoint initialize')
    try:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        dob = request.POST.get('dob')
        email = request.POST.get('email')

        # check whether request parameters are empty or not
        if (not first_name) or (not last_name) or (not user_name) or (not password) or (not dob) or (
                not email):
            logger.error('[{}]'.format('Request form-data were not provided.'))
            return HttpResponse({'detail': 'Request form-data were not provided.'}, status=400)

        user = UserModel()

        user.user_id = 1,
        user.user_role = "0",
        user.first_name = first_name,
        user.last_name = last_name,
        user.username = user_name,
        user.user_password = password,
        user.email = email,
        user.dob = dob,
        user.is_admin = "0"

        status, user_id = user.create_new_user()

        if not status:
            return HttpResponse({'detail': 'Internal server error_' + str(user_id)}, status=400)

        return user_id

    except Exception as e:
        logger.error('[{}]'.format(str(e)))
        raise Exception("Internal server error - add new user from database {}".format(e))


@api_view(['PUT'])
def update_user_details(request):
    logger.info('authentication')

    # authentication header details - auth token
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        errormsg = json.dumps({'detail': 'Authentication credentials were not provided.'})
        return HttpResponse(errormsg, status=403)

    try:
        access_token = authorization_header.split(' ')[1]
    except IndexError:
        errormsg = json.dumps({'detail': 'Authentication token prefix was not provided.'})
        return HttpResponse(errormsg, status=403)

    user_id = UserModel.validate_user(access_token)

    if user_id is None:
        errormsg = json.dumps({'detail': 'User not found.'})
        return HttpResponse(errormsg, status=401)

    try:
        # get username and user_password - form_data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # email = request.POST.get('email')
        if (not first_name) or (not last_name):
            return HttpResponse({'detail': 'Request form-data were not provided.'}, status=400)

        db_connection = engine
        # ## check email exist or not
        # getEmail = check_unique_data_except_pk_user('email', email, engine, user_id)
        # if len(getEmail) > 0:
        #     return Response({'detail': 'This email already exists'}, status=401)

        session = Session(autocommit=True, bind=db_connection, expire_on_commit=False)

        with session.begin():
            session.query(User).filter(User.UserId == user_id).update({User.UserFname: first_name,
                                                                       User.UserLname: last_name})

            return HttpResponse({'detail': 'User updated successfully'}, status=200)

    except Exception as e:
        logger.error('[{}]'.format(str(e)))
        return HttpResponse({'Error': str(e)}, status=401)


@api_view(['POST'])
def user_login(request):
    logger.info('user_login')

    # get username and user_password - form_data
    username = request.POST.get('username', None)
    user_password = request.POST.get('password', None)

    if (username is None) or (user_password is None):
        logger.error('[{}]'.format('Request form-data were not provided.'))
        return HttpResponse({'detail': 'Request form-data were not provided.'}, status=400)

    # get all 'op_user' table data from db using input parameters [ username ]
    db_connect = engine
    ResultSet = get_all_users('user', username, db_connect)

    try:
        # check if the user exists in the 'op_user' table
        if len(ResultSet) > 0:
            for result in ResultSet:
                access_token = str(result[5])
                password_hash = result[6]
                is_admin = result[9]
                salt = result[1]

                role_name = get_role_name(is_admin, engine)

                # verify and validate the user password using input password , hashed password and salt
                if verify_password(password_hash, user_password, salt):
                    access_token = {
                            'access_token': access_token,
                            'user_role': role_name,
                        }
                    return HttpResponse(access_token)
                else:
                    return HttpResponse({'detail': 'Invalid password.'}, status=401)
        else:
            return HttpResponse({'detail': 'Invalid user name.'}, status=401)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        traceback.print_exc()
        logger.error('[{}]'.format(str(e)))
        return HttpResponse({'detail': 'Internal Server Error.'}, status=500)
    finally:
        engine.dispose()


def get_all_users(arg_type, input_para, engine):
    logger.info('user_login_controller')
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
        logger.error('[{}]'.format(e))
        raise Exception('Internal Server Error - Retrieve all users from database {}'.format(e))

    finally:
        connection.close()
        engine.dispose()


def verify_password(hashed_password, provided_password, user_salt):
    logger.info('password_controller')
    try:
        salt = hashlib.sha256(user_salt.encode('utf-8')).hexdigest().encode('ascii')
        pwd_hash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt, 100000)
        pwd_hash = binascii.hexlify(pwd_hash)
        return hashed_password == (salt + pwd_hash).decode('ascii')

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        traceback.print_exc()
        logger.error('[{}]'.format(str(e)))
        raise Exception('Internal Server Error - verify password_' + str(e))


def get_role_name(role_id, engine):
    logger.info('user_license_controller')
    try:
        session = Session(autocommit=True, bind=engine, expire_on_commit=False)
        with session.begin():
            role_name = session.query(User.UserRoleId).filter(UserRole.UserRoleId == role_id).first()
    except Exception as e:
        logger.error('[{}]'.format(str(e)))
        raise Exception("Internal server error - get role name from database {}".format(e))
    finally:
        engine.dispose()
    return role_name[0]
