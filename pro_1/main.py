from .config.db import create_tables, connection
from .models.Schemas import User, Role
from .config.seed import seed_roles
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pro_1.routes.user_routes import router as user_router
from pro_1.routes import product_routes

from pro_1.routes import cart_routes
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
app.include_router(product_routes.router, tags=["Products"])

app.include_router(cart_routes.router)
@app.get('/')
async def root():
    return {'message': 'Hello World'}


def start():
    create_tables()
    seed_roles()
    uvicorn.run("pro_1.main:app", host="127.0.0.1", port=8080, reload=True)
