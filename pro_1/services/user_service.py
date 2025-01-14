from pro_1.models.users import User, Role
from pro_1.config.db import connection
from pro_1.utils.auth import hash_password
from sqlmodel import Session, select
import logging
from fastapi import HTTPException, status

# def create_user(email: str, password: str, role_name: str = "client"):
#     # Step 1: Hash the password
#     hashed_password = hash_password(password)

#     with Session(connection) as session:
#         # Step 2: Check if the role exists
#         role = session.exec(select(Role).where(Role.name == role_name)).first()
#         if not role:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Role '{role_name}' does not exist."
#             )
        
#         # Step 3: Check if the user already exists
#         existing_user = session.exec(select(User).where(User.email == email)).first()
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"User with email '{email}' already exists."
#             )
        
#         # Step 4: Create and save the new user
#         new_user = User(email=email, hashed_password=hashed_password, role_id=role.id)
#         session.add(new_user)
#         session.commit()
#         session.refresh(new_user)

#     return new_user



def create_user(email: str, password: str, role_name: str = "client"):
    logging.debug(f"Hashing password for {email}")
    hashed_password = hash_password(password)

    with Session(connection) as session:
        logging.debug(f"Checking if role {role_name} exists")
        role = session.exec(select(Role).where(Role.name == role_name)).first()
        if not role:
            logging.error(f"Role '{role_name}' does not exist")
            raise ValueError(f"Role '{role_name}' does not exist")

        logging.debug(f"Creating user for {email} with role {role_name}")
        user = User(email=email, hashed_password=hashed_password, role_id=role.id)
        session.add(user)
        session.commit()

        logging.debug(f"User {email} created successfully")
    return user
