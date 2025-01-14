from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    role_id: int = Field(default=None, foreign_key="role.id")

    class from_attributes:
        orm_mode = True  # Ensure the model is serializable

class Role(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
