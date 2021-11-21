import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy.orm import relationship
from database import Base
import passlib.hash as _hash
from sqlalchemy.sql.sqltypes import Date

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)

