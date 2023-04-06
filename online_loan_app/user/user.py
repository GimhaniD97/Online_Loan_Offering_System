import email
import json
import sys
import traceback
import uuid

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy.orm import Session

from logs import logging_service
from online_loan_app.database import get_mysql_connection
from online_loan_app.models import User
from online_loan_app.user.user_controller import add_new_user, validate_user, get_all_users, verify_password, \
    get_role_name

# get database connection
engine = get_mysql_connection()


class UserModel:

    def __int__(self, user_id, user_role, first_name, last_name, username, user_password, email, dob, is_admin):
        self.user_id = user_id
        self.user_role = user_role
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_password = user_password
        self.email = email
        self.dob = dob
        self.is_admin = is_admin

    def create_new_user(self):
        log_id = str(uuid.uuid4())[:8]
        logging = logging_service('authentication', log_id)
        try:

            # check whether request parameters are empty or not
            if (not self.user_role) or (not self.first_name) or (not self.last_name) or (not self.username) or \
                    (not self.user_password) or (not self.email) or (not self.dob):
                logging.error('[{}]'.format('Request form-data were not provided.'))
                return Response({'detail': 'Request form-data were not provided.'}, status=400)

            # add new user to db
            user_id = add_new_user(self.user_role, self.first_name, self.last_name, self.username, self.user_password,
                                   self.email, self.dob, self.is_admin)
            if user_id is None:
                return Response({'detail': '{} Internal Server Error.'.format(log_id)}, status=500)

            return Response({'detail': 'User added successfully - user id : ' + str(user_id)}, status=201)

        except Exception as e:
            logging.error('[{}]'.format(str(e)))
            return Response({'Error': '{} {}'.format(log_id, e)}, status=401)

    @api_view(['PUT'])
    def update_user_details(request):
        log_id = str(uuid.uuid4())[:8]
        logging = logging_service('authentication', log_id)

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

        user_id = validate_user(access_token)
        if user_id is None:
            errormsg = json.dumps({'detail': 'User not found.'})
            return HttpResponse(errormsg, status=401)

        try:
            # get username and user_password - form_data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            # email = request.POST.get('email')

            if (not first_name) or (not last_name):
                return Response({'detail': 'Request form-data were not provided.'}, status=400)

            db_connection = engine

            # ## check email exist or not
            # getEmail = check_unique_data_except_pk_user('email', email, engine, user_id)
            # if len(getEmail) > 0:
            #     return Response({'detail': 'This email already exists'}, status=401)

            session = Session(autocommit=True, bind=db_connection, expire_on_commit=False)
            with session.begin():
                session.query(User).filter(User.UserId == user_id).update({User.UserFname: first_name,
                                                                           User.UserLname: last_name})

            return Response({'detail': 'User updated successfully'}, status=200)

        except Exception as e:
            logging.error('[{}]'.format(str(e)))
            return Response({'Error': str(e)}, status=401)

    @api_view(['POST'])
    def user_login(request):
        log_id = str(uuid.uuid4())[:8]
        logging = logging_service('user_login', log_id)

        # get username and user_password - form_data
        username = request.POST.get('username', None)
        user_password = request.POST.get('password', None)

        if (username is None) or (user_password is None):
            logging.error('[{}]'.format('Request form-data were not provided.'))
            return Response({'detail': '{} Request form-data were not provided.'.format(log_id)}, status=400)

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
                        return Response(access_token)
                    else:
                        return Response({'detail': 'Invalid password.'}, status=401)
            else:
                return Response({'detail': 'Invalid user name.'}, status=401)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, exc_type, exc_tb.tb_lineno)
            traceback.print_exc()
            logging.error('[{}]'.format(str(e)))
            return Response({'detail': '{} Internal Server Error.'.format(log_id)}, status=500)
        finally:
            engine.dispose()
