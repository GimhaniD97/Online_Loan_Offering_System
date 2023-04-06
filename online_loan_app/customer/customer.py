import json
import uuid

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sqlalchemy.orm import Session

from logs import logging_service
from online_loan_app.customer.customer_controller import add_new_customer, validate_customer
from online_loan_app.database import get_mysql_connection
from online_loan_app.models import Customer

engine = get_mysql_connection()


@api_view(['POST'])
def create_new_customer(request):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('Customer', log_id)
    try:
        # get username and user_password - form_data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        mobile_no = request.POST.get('mobile_no')

        # check whether request parameters are empty or not
        if (not first_name) or (not last_name) or (not user_name) or (not password) or (not dob) or (
                not email) or (not mobile_no):
            logging.error('[{}]'.format('Request form-data were not provided.'))
            return Response({'detail': 'Request form-data were not provided.'}, status=400)

        # add new user to db
        customer_id = add_new_customer(first_name, last_name, user_name, email, dob, mobile_no)
        if customer_id is None:
            return Response({'detail': '{} Internal Server Error.'.format(log_id)}, status=500)

        return Response({'detail': 'Customer added successfully - customer id : ' + str(customer_id)}, status=201)

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        return Response({'Error': '{} {}'.format(log_id, e)}, status=401)


@api_view(['PUT'])
def update_customer_details(request):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('Customer', log_id)

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

    customer_id = validate_customer(access_token)
    if customer_id is None:
        errormsg = json.dumps({'detail': 'Customer not found.'})
        return HttpResponse(errormsg, status=401)

    try:
        # get username and user_password - form_data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        # email = request.POST.get('email')

        if (not first_name) or (not last_name):
            return Response({'detail': 'Request form-data were not provided.'}, status=400)

        db_connection = engine

        session = Session(autocommit=True, bind=db_connection, expire_on_commit=False)
        with session.begin():
            session.query().filter(Customer.CustomerId == customer_id).update({Customer.CustomerFname: first_name,
                                                                               Customer.CustomerLname: last_name})

        return Response({'detail': 'Customer updated successfully'}, status=200)

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        return Response({'Error': str(e)}, status=401)
