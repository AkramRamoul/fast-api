from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
import models

from database import engine, SessionLocal
from sqlalchemy.orm import session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

# Pydantic Models
class PostBase(BaseModel):
    title: str
    content: str
    user_id: bool = True

class UserBase(BaseModel):
    username: str  # Use `str` instead of `String`

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[session, Depends(get_db)]

# Endpoint to create a user
@app.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    return db_user  # Return the created user
