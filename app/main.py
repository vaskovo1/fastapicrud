from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserSchema
from app.models import UserModel
from app.services import user_service
from app.configs.postgres_database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



UserModel.Base.metadata.create_all(bind=engine)
app = FastAPI()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    with SessionLocal() as db:
        return db
        

@app.post('/token')
async def token_generate(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data)
    return {"access_token": form_data.username, "token_type": "bearer"}
    
    
@app.get("/users/profile_pic")
async def profile_pic(token: str = Depends(oauth_scheme)):
    print(token)
    return {"user": "Slava"}


@app.get("/v1/users/{user_id}", response_model=UserSchema.User)
async def get_user(
        user_id: int,
        db: Session = Depends(get_db),
):
    user = await user_service.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return user


@app.put("/v1/users/{user_id}", response_model=UserSchema.User)
async def update_bike(
        user_id: int,
        user: UserSchema.UserIn,
        db: Session = Depends(get_db),
):
    user_db = await user_service.get_user(db, user_id=user_id)
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return await user_service.update_user(user_db=user_db, db=db, user=user)


@app.post("/v1/users/", response_model=UserSchema.User)
async def create_bike(user: UserSchema.User, db: Session = Depends(get_db),
                      ):
    user_db = await user_service.get_user(db, user_id=user.user_id)
    if user_db:
        raise HTTPException(status_code=400, detail="User already exists")
    return await user_service.create_user(db=db, user=user)
