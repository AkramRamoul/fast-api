from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
import models
from typing import Optional
from database import engine, SessionLocal
from sqlalchemy.orm import session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content: str
    user_id: int

class UserBase(BaseModel):
    username: str  # Use `str` instead of `String`

class PostBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None
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

@app.get("/user/{user_id}",status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: db_dependency):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.post("/posts/{post_Id}",status_code=status.HTTP_200_OK)
async def getPost(post_Id:int,db:db_dependency):
  db_post=db.query(models.Post).filter(models.Post.id == post_Id).first()
  if db_post is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
  return db_post



@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()
    return db_post 
  
@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    db.delete(db_post)
    db.commit()

@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post: PostBaseUpdate, db: db_dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.title is not None:
        db_post.title = post.title
    if post.content is not None:
        db_post.content = post.content
    if post.user_id is not None:
        db_post.user_id = post.user_id
    
    try:
        db.commit()  
        db.refresh(db_post)  
        return db_post  
    except Exception as e:
        db.rollback()  
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update post: {str(e)}")