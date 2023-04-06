from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class UserRole(Base):
    __tablename__ = 'user_role'

    UserRoleId = Column(Integer, primary_key=True)
    UserRole = Column(String(100))
    CreatedDateTime = Column(DateTime)
    CreatedBy = Column(String(150))


class User(Base):
    __tablename__ = 'user'

    UserId = Column(Integer, primary_key=True)
    UserRoleId = Column(ForeignKey('user_role.UserRoleId'), index=True)
    UserFname = Column(String(100))
    UserLname = Column(String(100))
    UserName = Column(String(50))
    AccessToken = Column(String(1000))
    Password = Column(String(10))
    UserEmail = Column(String(150))
    UserDob = Column(DateTime)
    IsAdmin = Column(Integer, default=0)
    CreatedBy = Column(String(100))
    CreatedDateTime = Column(DateTime)
    ModifiedBy = Column(String(100))
    ModifiedDateTime = Column(DateTime)

    Role = relationship('UserRole')


class Customer(Base):
    __tablename__ = 'customer'

    CustomerId = Column(Integer, primary_key=True)
    CustomerFname = Column(String(100))
    CustomerLname = Column(String(100))
    UserName = Column(String(50))
    AccessToken = Column(String(1000))
    Password = Column(String(10))
    CustomerDob = Column(DateTime)
    CustomerEmail = Column(String(150))
    CustomerMobileNo = Column(String(20))
    CreatedBy = Column(String(100))
    CreatedDateTime = Column(DateTime)
    ModifiedBy = Column(String(100))
    ModifiedDateTime = Column(DateTime)





