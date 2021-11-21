import fastapi as _fastapi
import fastapi.security as _security
import jwt as jwt
import datetime as _dt
import sqlalchemy.orm as Session
import passlib.hash as _hash

import database as _database, models as _models, schemas as _schemas

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "51ab04efd8e19a3f804b03ec63222b3e273170a4895d01c2e7d3ec6bf85d81a3"


def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_username(username: str, db: Session):
    return db.query(_models.User).filter(_models.User.username == username).first()


async def create_user(user: _schemas.UserCreate, db: Session):
    user_obj = _models.User(
        username=user.username, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(username: str, password: str, db: Session):
    user = await get_user_by_username(db=db, username=username)

    if not user:
        return False

    if not user.verify_password(password):
        return False

    return user


async def create_token(user: _models.User):
    user_obj = _schemas.User.from_orm(user)

    token = jwt.encode(user_obj.dict(), JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2schema),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid username or Password"
        )

    return _schemas.User.from_orm(user)


