from fastapi import FastAPI, HTTPException, APIRouter,Query
from pro_1.services.user_service import create_user
from fastapi import Body
from typing import Optional

from pro_1.models.users import User, Role
from pro_1.config.db import create_tables, connection
from pro_1.utils.auth import hash_password, verify_password, create_access_token
from sqlmodel import Session, select
from fastapi.responses import JSONResponse
import logging
router = APIRouter()


logging.basicConfig(level=logging.DEBUG)

@router.post('/register')
async def register_user(
    credentials: Optional[dict] = Body(None),  # This will accept JSON body
    email: Optional[str] = Query(None),         # This will accept query parameters
    password: Optional[str] = Query(None),      # This will accept query parameters
    role_name: Optional[str] = Query("client")  # This will accept query parameters
):
    # If credentials are provided in the body, use them
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")
        role_name = credentials.get("role_name", "client")  # Default to "client" if not in body

    # Validate the presence of required fields
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Check if the user already exists in the database
    with Session(connection) as session:
        logging.debug(f"Checking if user with email {email} exists")
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            logging.error(f"User with email {email} already exists")
            raise HTTPException(status_code=400, detail="Email is already taken")

    # User creation logic (including hashing password, etc.)
    # Example of creating user (simplified for this case)
    logging.debug(f"Creating user with email {email} and role {role_name}")
    user = create_user(email=email, password=password, role_name=role_name)

    logging.debug(f"User with email {email} created successfully")
    
    # Return success message
    return {"message": "User registered successfully", "user": user}







@router.post('/login')
async def login(
    credentials: Optional[dict] = Body(None),
    email: Optional[str] = Query(None),
    password: Optional[str] = Query(None)
):
    # If credentials are provided in the body, use them
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")

    # If query parameters are provided, use them
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        # Find the user by email
        user = session.exec(select(User).where(User.email == email)).first()

        # Check if the user exists
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Fetch the user's role
        role = session.exec(select(Role).where(Role.id == user.role_id)).first()

        if not role:
            raise HTTPException(status_code=400, detail="User role not found")

        # Create an access token with the user's role
        access_token = create_access_token(data={"sub": email, "role": role.name})

        # Return the token and role information
        return JSONResponse(content={
            "access_token": access_token, 
            "token_type": "bearer", 
            "role": role.name,
            "message": f"Successfully logged in as {role.name}"  # Added role-based message
        })















@router.get('/data')
async def data():
    return {
        "data": "This is a protected route, only accessible with a valid access token"
    }
    
    
    
# @router.post('/login')
# async def login(
#     email: str = Query(..., description="The user's email address"),
#     password: str = Query(..., description="The user's password")
# ):
#     with Session(connection) as session:
#         # Find the user by email
#         user = session.exec(select(User).where(User.email == email)).first()

#         # Check if the user exists
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         # Verify password
#         if not verify_password(password, user.hashed_password):
#             raise HTTPException(status_code=401, detail="Invalid email or password")
        
#         # Fetch the user's role
#         role = session.exec(select(Role).where(Role.id == user.role_id)).first()

#         if not role:
#             raise HTTPException(status_code=400, detail="User role not found")

#         # Create an access token with the user's role
#         access_token = create_access_token(data={"sub": email, "role": role.name})
        
#         # Return the token and role information
#         return JSONResponse(content={"access_token": access_token, "token_type": "bearer", "role": role.name})
 
# @router.post('/login')
# async def login(email: str = Body(...), password: str = Body(...)):
#     with Session(connection) as session:
#         # Find the user by email
#         user = session.exec(select(User).where(User.email == email)).first()

#         # Check if the user exists
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         # Verify password
#         if not verify_password(password, user.hashed_password):
#             raise HTTPException(status_code=401, detail="Invalid email or password")
        
#         # Fetch the user's role
#         role = session.exec(select(Role).where(Role.id == user.role_id)).first()

#         if not role:
#             raise HTTPException(status_code=400, detail="User role not found")

#         # Create an access token with the user's role
#         access_token = create_access_token(data={"sub": email, "role": role.name})
        
#         # Return the token and role information
#         return JSONResponse(content={"access_token": access_token, "token_type": "bearer", "role": role.name})

# @router.post('/login')
# async def login(credentials: dict = Body(...)):
#     email = credentials.get("email")
#     password = credentials.get("password")
    
#     with Session(connection) as session:
#         # Find user by email
#         user = session.exec(select(User).where(User.email == email)).first()

#         # Check if user exists
#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         # Verify password
#         if not verify_password(password, user.hashed_password):
#             raise HTTPException(status_code=401, detail="Invalid email or password")
        
#         # Fetch the user's role
#         role = session.exec(select(Role).where(Role.id == user.role_id)).first()

#         if not role:
#             raise HTTPException(status_code=400, detail="User role not found")

#         # Create access token with role
#         access_token = create_access_token(data={"sub": email, "role": role.name})
        
#         # Return the token and role information
#         return JSONResponse(content={"access_token": access_token, "token_type": "bearer", "role": role.name})


