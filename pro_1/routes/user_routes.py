from fastapi import FastAPI, HTTPException, APIRouter, Query, Depends
from pro_1.services.user_service import create_user,get_all_users,delete_user,update_user
from fastapi import Body
from typing import Optional

from pro_1.models.users import User, Role
from pro_1.config.db import create_tables, connection,get_session
from pro_1.utils.auth import hash_password,super_admin_required ,verify_password, create_access_token, get_current_user, check_role,check_role_factory
from sqlmodel import Session, select

from fastapi.responses import JSONResponse
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)


# ------------------- USER MANAGEMENT ENDPOINTS -------------------



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
            "user_id":user.id,
            "created_by":user.role_id,            # Added role-based message
            "message": f"Successfully logged in as {role.name}"
        })



# ------------------- SUPER ADMIN CRUD -------------------
@router.get("/users", response_model=list[User])
async def fetch_all_users(session: Session = Depends(get_session)):
    return get_all_users(session)





# Update user details (Super Admin only)
@router.put("/update_user/{user_id}")
async def update_user_route(
    user_id: int,
    email: str = Query(...),
    password: str = Query(...),
    role_name: str = Query(...),
   
):
     # Ensure the user is a Super Admin

    updated_user = update_user(user_id, email, password, role_name)
    if updated_user:
        return {"message": f"User {user_id} updated successfully", "user": updated_user}
    else:
        raise HTTPException(status_code=404, detail="User not found")




# Delete a user (Super Admin only)
@router.delete("/delete_user/{user_id}")
async def delete_user_route(
    user_id: int,

):
    # Ensure the user is a Super Admin

    deleted_user = delete_user(user_id)
    if deleted_user:
        return {"message": f"User {user_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# ------------------- USER CREATION FOR ADMIN AND CLIENT -------------------

@router.post('/create_simple_admin')
async def create_simple_admin(
    credentials: Optional[dict] = Body(None),
    email: Optional[str] = Query(None),
    password: Optional[str] = Query(None),

):
    """Create a Simple Admin (Super Admin only)."""
 # Ensure the user is a Super Admin

    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

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
    credentials: Optional[dict] = Body(None),
    email: Optional[str] = Query(None),
    password: Optional[str] = Query(None),

):
   
    if credentials:
        email = credentials.get("email")
        password = credentials.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    with Session(connection) as session:
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

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
