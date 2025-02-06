from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
from sqlmodel import Session,select
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from pro_1.models.users import User

from pro_1.config.db import get_session
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    
    return pwd_context.verify(plain_password, hashed_password)
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt  



# Decode a JWT token
def decode_access_token(token: str) -> Dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Validate if the token is expired
        if decoded_token.get("exp") < datetime.now().timestamp():
            return None
        return decoded_token
    except jwt.PyJWTError:
        return None
# Get current user from the token

async def get_current_user(session: Session = Depends(get_session), current_user: User = Depends()):
    # Assuming `current_user` is injected based on user login or session info
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in")
    return current_user


async def check_role(required_role: str, current_user: User):
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    if current_user.role != required_role:
        raise HTTPException(
            status_code=403, detail=f"User does not have the required role: {required_role}"
        )
    return current_user


def check_role_factory(required_role: str):
    async def check_role_dependency(current_user: User = Depends(get_current_user)):
        await check_role(required_role, current_user)
    return check_role_dependency







# async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     user_email = payload.get("sub")
#     if not user_email:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token: User email missing",
#         )
    
#     user = await get_user_by_email(user_email)  # Ensure this function is async if needed
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
    
#     return user

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         # Decode token and validate
#         payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
#         user_email: str = payload.get("sub")
#         if user_email is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
        
#         # Fetch user from the database or any other logic here
#         user = get_user_by_email(user_email)
#         if user is None:
#             raise HTTPException(status_code=401, detail="User not found")
#         return user
    
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



def get_user_by_email(email: str):
    with Session(get_session()) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        return user
# async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     user_id = payload.get("sub")  # Assume "sub" contains the user ID
#     if not user_id:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token: User ID missing",
#         )
    
#     # Fetch the user from the database
#     user = session.exec(select(User).where(User.id == user_id)).first()
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
    
#     return user 

# Return the fully hydrated User object
# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     payload = decode_access_token(token)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return payload

# async def check_role(required_role: str, token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
#     user = await get_current_user(token,session)
#     if user["role"] != required_role:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=f"Access denied for {required_role} role"
#         )

# # Dependency factory function
# # Modify check_role to use an async dependency factory
# def check_role_factory(required_role: str):
#     async def check_role_dependency(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
#         return await check_role(required_role, token, session)  # Call the async check_role function
#     return check_role_dependency


# Ensure that only Super Admins can access certain endpoints
def super_admin_required(current_user:User):
    if current_user.role.name != "super_admin":
        raise HTTPException(status_code=403, detail="Access denied. Super Admins only.")
