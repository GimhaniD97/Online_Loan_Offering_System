import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from online_loan_app.database import get_mysql_connection, call_store_procedure_get
from online_loan_app.logs import Logger
from online_loan_app.models import User
from online_loan_app.user.password_controller import create_hash_password


logger = Logger()


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
        try:
            hashed_password, salt_user = create_hash_password(self.user_password)
            # add new user to db
            engine = get_mysql_connection()
            session = Session(autocommit=True, bind=engine, expire_on_commit=False)

            # create session and add user
            with session.begin():
                # get last user id from 'Op_user' table
                user_id = session.query(func.max(User.UserId)).scalar()
                user = User(
                    UserId=(user_id + 1),
                    UserRoleId=self.user_role,
                    UserFname=self.first_name,
                    UserLname=self.last_name,
                    UserName=self.username,
                    AccessToken=hashed_password,
                    Password=hashed_password,
                    UserEmail=self.email,
                    UserDob=self.dob,
                    CreatedBy='',
                    CreatedDateTime=datetime.datetime.now(),
                    ModifiedBy='',
                    ModifiedDateTime=''
                )
                session.add(user)
                engine.dispose()

            if user_id is None:
                return False, 'Internal Server Error'

            return True, ""

        except Exception as e:
            engine.dispose()
            logger.error('[{}]'.format(str(e)))
            return False, str(e)

    @staticmethod
    def validate_user(access_token):
        logger.info('user_controller')
        try:
            uid = call_store_procedure_get('validate_user', access_token)
            if uid == '':
                return None
            elif uid != '':
                return uid

        except Exception as e:
            logger.error('[{}]'.format(str(e)))
            raise Exception('{} Internal Server Error - Token Verification {}'.format(log_id, e))