import datetime
import uuid

from rest_framework.decorators import api_view
from sqlalchemy import func
from sqlalchemy.orm import Session

from logs import logging_service
from online_loan_app.database import get_mysql_connection, call_store_procedure_get
from online_loan_app.models import Customer
from online_loan_app.user.password_controller import create_hash_password

engine = get_mysql_connection()


def add_new_customer(first_name, last_name, user_name, user_password, email, dob, mobile_no):
    hashed_password, salt_user = create_hash_password(user_password)
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('customer_controller', log_id)
    try:
        db_connection = engine
        session = Session(autocommit=True, bind=db_connection)

        # create session and add user
        with session.begin():
            # get last user id from 'Op_user' table
            customer_id = session.query(func.max(Customer.CustomerId)).scalar()
            customer = Customer(
                CustomerId=customer_id,
                CustomerFname=first_name,
                CustomerLname=last_name,
                UserName=user_name,
                AccessToken=hashed_password,
                Password=hashed_password,
                CustomerDob=dob,
                CustomerEmail=email,
                CustomerMobileNo=mobile_no,
                CreatedBy='',
                CreatedDateTime=datetime.datetime.now(),
                ModifiedBy='',
                ModifiedDateTime=''
            )
            session.add(customer)

        return customer_id + 1

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception("{} Internal server error - add new customer from database {}".format(log_id, e))

    finally:
        engine.dispose()


def validate_customer(access_token):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_controller', log_id)
    try:
        cusid = call_store_procedure_get('validate_customer', access_token)
        if cusid == '':
            return None
        elif cusid != '':
            return cusid

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception('{} Internal Server Error - Token Verification {}'.format(log_id, e))
