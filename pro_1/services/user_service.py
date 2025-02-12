from pro_1.models.Schemas import User, Role
from pro_1.config.db import connection
from pro_1.utils.auth import hash_password
from sqlmodel import Session, select
import logging
from fastapi import HTTPException, status




def create_user(email: str, password: str, role_name: str = "client"):
    logging.debug(f"Hashing password for {email}")
    hashed_password = hash_password(password)

    with Session(connection) as session:
        logging.debug(f"Checking if role {role_name} exists")
        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if not role:
            logging.error(f"Role '{role_name}' does not exist")
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' does not exist"
            )

        logging.debug(f"Creating user for {email} with role {role_name}")
        new_user = User(email=email, hashed_password=hashed_password, role_id=role.id)
        session.add(new_user)
        session.commit()

        logging.debug(f"User {email} created successfully")
    return new_user


def get_all_users(session:Session):
    return session.exec(select(User)).all()


def update_user(user_id: int, email: str, password: str, role_name: str):
    with Session(connection) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")

        user.email = email
        user.hashed_password = hash_password(password)
        user.role_id = role.id
        session.commit()
        return user
  

def delete_user(user_id: int):
    with Session(connection) as session:
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()    