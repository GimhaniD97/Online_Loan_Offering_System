import json
import uuid

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from User_Controller import add_new_user
from database import get_mysql_connection
from services import logging_service

# get database connection
engine = get_mysql_connection()


@api_view(['POST'])
def create_new_user(request):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('authentication', log_id)
    try:
        # get username and user_password - form_data
        user_role = int(request.POST.get('user_role'))
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        user_password = request.POST.get('password')
        email = request.POST.get('email')
        dob = request.POST.get('dob')

        # check whether request parameters are empty or not
        if (not user_role) or (not first_name) or (not last_name) or (not username) or (not user_password) or (
                not email) or (not dob):
            logging.error('[{}]'.format('Request form-data were not provided.'))
            return Response({'detail': 'Request form-data were not provided.'}, status=400)

        # add new user to db
        user_id = add_new_user(user_role, first_name, last_name, username, user_password, email, dob)
        if user_id is None:
            return Response({'detail': '{} Internal Server Error.'.format(log_id)}, status=500)

        return Response({'detail': 'User added successfully - user id : ' + str(user_id)}, status=201)

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        return Response({'Error': '{} {}'.format(log_id, e)}, status=401)


@api_view(['PUT'])
def update_login_user_details(request):
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

        engine = get_mysql_connection()

        # ## check email exist or not
        # getEmail = check_unique_data_except_pk_user('email', email, engine, user_id)
        # if len(getEmail) > 0:
        #     return Response({'detail': 'This email already exists'}, status=401)

        session = Session(autocommit=True, bind=engine, expire_on_commit=False)
        with session.begin():
            session.query(OpUser).filter(OpUser.id == user_id).update({OpUser.first_name: first_name,
                                                                       OpUser.last_name: last_name})

        return Response({'detail': 'User updated successfully'}, status=200)

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        return Response({'Error': str(e)}, status=401)

