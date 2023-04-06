class User:

    def __int__(self, user_id, user_role, first_name, last_name, username, user_password, email, dob):
        self.user_id = user_id
        self.user_role = user_role
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_password = user_password
        self.email = email
        self.dob = dob

    def user_add(self):
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

        db_connection.dispose()

        return user_id + 1

    @staticmethod
    def validate_user(access_token):
        return 'success'
