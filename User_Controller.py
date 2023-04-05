import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_mysql_connection
from models import User
from password_controller import create_hash_password
from services import logging_service

engine = get_mysql_connection()


def add_new_user(user_role, first_name, last_name, user_name, user_password, email, dob):
    hashed_password, salt_user = create_hash_password(user_password)
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('user_license_controller', log_id)
    try:
        db_connection = engine
        session = Session(autocommit=True, bind=db_connection)

        # create session and add user
        with session.begin():
            # get last user id from 'Op_user' table
            user_id = session.query(func.max(User.UserId)).scalar()
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
                CreatedBy='',
                CreatedDateTime=datetime.datetime.now(),
                ModifiedBy='',
                ModifiedDateTime=''
            )
            session.add(user)

        return user_id + 1

    except Exception as e:
        logging.error('[{}]'.format(str(e)))
        raise Exception("{} Internal server error - add new user from database {}".format(log_id, e))

    finally:
        engine.dispose()
