import binascii
import hashlib
import secrets
import sys
import traceback
import uuid

from services import logging_service


def create_hash_password(user_password):
    log_id = str(uuid.uuid4())[:8]
    logging = logging_service('password_controller', log_id)
    try:
        random_string = secrets.token_hex(8)
        password = user_password

        salt = hashlib.sha256(random_string.encode('utf-8')).hexdigest().encode('ascii')
        pwd_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwd_hash = binascii.hexlify(pwd_hash)
        hashed_password = (salt + pwd_hash).decode('ascii')

        return hashed_password, random_string

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_type, exc_tb.tb_lineno)
        traceback.print_exc()
        logging.error('[{}]'.format(str(e)))
        raise Exception('Internal Server Error - verify password_' + str(e))
