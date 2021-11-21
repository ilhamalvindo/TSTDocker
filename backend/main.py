from typing import List

from fastapi import Depends, FastAPI, security
import fastapi
from pydantic import errors
from pydantic.schema import schema
from sqlalchemy.orm import Session


import models, schemas, services
from database import SessionLocal, engine

app = fastapi.FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.post("/api/users")
async def create_user(
    user: schemas.UserCreate, db: Session = Depends(services.get_db)
):
    db_user = await services.get_user_by_email(user.username, db)
    if db_user:
        raise fastapi.HTTPException(status_code=400, detail="Username already in use")

    user = await services.create_user(user, db)

    return await services.create_token(user)


@app.post("/api/token")
async def generate_token(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: Session = fastapi.Depends(services.get_db),
):
    user = await services.authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

    return await services.create_token(user)


@app.get("/api/users/me", response_model=schemas.User)
async def get_user(user: schemas.User = fastapi.Depends(services.get_current_user)):
    return user


@app.get("/api")
async def root():
    return {"message": "Awesome Leads Manager"}