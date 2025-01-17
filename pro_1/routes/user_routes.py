from fastapi import FastAPI, HTTPException, APIRouter, Query, Depends
from pro_1.services.user_service import create_user
from fastapi import Body
from typing import Optional

from pro_1.models.users import User, Role
from pro_1.config.db import create_tables, connection
from pro_1.utils.auth import hash_password, verify_password, create_access_token, get_current_user, check_role,check_role_factory
from sqlmodel import Session, select
from fastapi.responses import JSONResponse
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)


# ------------------- USER MANAGEMENT ENDPOINTS -------------------

@router.post('/register')
async def register_user(
    credentials: Optional[dict] = Body(None),  # This will accept JSON body
    # This will accept query parameters
    email: Optional[str] = Query(None),
    # This will accept query parameters
    password: Optional[str] = Query(None),
    # This will accept query parameters
    role_name: Optional[str] = Query("client")
):
    # If credentials are provided in the body, use them
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")
        # Default to "client" if not in body
        role_name = credentials.get("role_name", "client")

    # Validate the presence of required fields
    if not email or not password:
        raise HTTPException(
            status_code=400, detail="Email and password are required")

    # Check if the user already exists in the database
    with Session(connection) as session:
        logging.debug(f"Checking if user with email {email} exists")
        existing_user = session.exec(
            select(User).where(User.email == email)).first()
        if existing_user:
            logging.error(f"User with email {email} already exists")
            raise HTTPException(
                status_code=400, detail="Email is already taken")

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
        raise HTTPException(
            status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        # Find the user by email
        user = session.exec(select(User).where(User.email == email)).first()

        # Check if the user exists
        if not user:
            raise HTTPException(
                status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401, detail="Invalid email or password")

        # Fetch the user's role
        role = session.exec(select(Role).where(
            Role.id == user.role_id)).first()

        if not role:
            raise HTTPException(status_code=400, detail="User role not found")

        # Create an access token with the user's role
        access_token = create_access_token(
            data={"sub": email, "role": role.name})

        # Return the token and role information
        return JSONResponse(content={
            "access_token": access_token,
            "token_type": "bearer",
            "role": role.name,
            # Added role-based message
            "message": f"Successfully logged in as {role.name}"
        })



# ------------------- USER CREATION FOR ADMIN AND CLIENT -------------------

@router.post('/create_simple_admin')
async def create_simple_admin(
    credentials: Optional[dict] = Body(None),  # This will accept JSON body
    email: Optional[str] = Query(None),
    password: Optional[str] = Query(None)
):
    """Create a Simple Admin (Super Admin only)."""
    # If credentials are provided in the body, use them
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")

    # Validate the presence of required fields
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Find the 'simple_admin' role
        role = session.exec(select(Role).where(Role.name == "simple_admin")).first()
        if not role:
            raise HTTPException(status_code=400, detail="Role 'simple_admin' not found")

        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            role_id=role.id
        )
        session.add(new_user)
        session.commit()
        return {"message": f"Simple Admin '{email}' created successfully"}


@router.post('/create_client')
async def create_client(
    credentials: Optional[dict] = Body(None),  # This will accept JSON body
    email: Optional[str] = Query(None),
    password: Optional[str] = Query(None)
):
    """Create a Client (Super Admin and Simple Admin only)."""
    # If credentials are provided in the body, use them
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")

    # Validate the presence of required fields
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Find the 'client' role
        role = session.exec(select(Role).where(Role.name == "client")).first()
        if not role:
            raise HTTPException(status_code=400, detail="Role 'client' not found")

        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            role_id=role.id
        )
        session.add(new_user)
        session.commit()
        return {"message": f"Client '{email}' created successfully"}


@router.get('/data')
async def data():
    return {
        "data": "This is a protected route, only accessible with a valid access token"
    }



# @router.post("/roles", dependencies=[Depends(check_role_factory("super_admin"))])
# async def create_role(role_name: str = Body(...)):
#     """Create a new role (Super Admin only)."""
#     with Session(connection) as session:
#         existing_role = session.exec(
#             select(Role).where(Role.name == role_name)).first()
#         if existing_role:
#             raise HTTPException(status_code=400, detail="Role already exists")

#         new_role = Role(name=role_name)
#         session.add(new_role)
#         session.commit()
#         return {"message": f"Role '{role_name}' created successfully"}
    

# ------------------- NEW PRODUCT MANAGEMENT ENDPOINTS -------------------

# @router.post("/products", dependencies=[Depends(check_role("simple_admin"))])
# async def add_product(product_data: dict = Body(...)):
#     """Add a product (Simple Admin)."""
#     # Product data would typically include fields like 'name', 'category', etc.
#     # Save the product to the database (you need a Product model for this)
#     return {"message": "Product added successfully", "product": product_data}


# @router.get("/products", dependencies=[Depends(check_role("client"))])
# async def get_products():
#     """Get a list of products (Client)."""
#     # Retrieve products from the database (you need a Product model for this)
#     return {"products": "List of products here"}



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
