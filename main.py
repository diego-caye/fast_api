from fastapi import FastAPI, Depends
import models
from database import engine
import auth 
import auth.routes as auth
from auth.utils import get_current_user
from routes import products, categories

app = FastAPI()

current_user: dict = Depends(get_current_user)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(categories.router)