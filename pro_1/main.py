from .config.db import create_tables, connection
from .models.users import User, Role
from .config.seed import seed_roles
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pro_1.routes.user_routes import router as user_router


app = FastAPI()
load_dotenv()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router,  tags=["Users"])


@app.get('/')
async def root():
    return {'message': 'Hello World'}


def start():
    create_tables()
    seed_roles()
    uvicorn.run("pro_1.main:app", host="127.0.0.1", port=8080, reload=True)
