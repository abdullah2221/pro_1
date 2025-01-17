# from sqlmodel import SQLModel, Field

# class User(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     email: str
#     hashed_password: str
#     role_id: int = Field(default=None, foreign_key="role.id")

#     class from_attributes:
#         orm_mode = True  # Ensure the model is serializable

# class Role(SQLModel, table=True):
#     id: int = Field(default=None, primary_key=True)
#     name: str




from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

# Role Model
class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    # Relationship with users
    users: List["User"] = Relationship(back_populates="role")

# User Model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    role_id: int = Field(foreign_key="role.id")

    # Relationship with roles
    role: Optional[Role] = Relationship(back_populates="users")

    class Config:
        from_attributes = True
