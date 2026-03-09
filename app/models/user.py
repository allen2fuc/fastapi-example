from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlmodel import SQLModel

class User(SQLAlchemyBaseUserTableUUID, SQLModel, table=True):
    pass