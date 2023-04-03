import uuid
from rest_framework.decorators import api_view
from rest_framework.response import Response

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

        if (not first_name) or (not last_name) or (not username) or (not user_password) or (not email) or (not dob):
            logging.error('[{}]'.format('Request form-data were not provided.'))
            return Response({'detail': 'Request form-data were not provided.'}, status=400)

        db_connection = engine







    except:
