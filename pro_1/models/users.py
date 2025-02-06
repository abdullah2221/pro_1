# users.py
from sqlmodel import SQLModel, Field, Relationship
from typing import List

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    role_id: int = Field(default=None, foreign_key="role.id")


    class Config:
        from_attributes = True

class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
