from fastapi import HTTPException, status, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from schema import CreatePost, UpdatePost, PostResponse, PostOut
from db import get_db
import models, utils

router = APIRouter(prefix="/posts", tags=['Posts'])


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: int  = Depends(utils.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts = db.query(models.Posts).filter(models.Posts.title.contains(search)).limit(limit).offset(skip).all()
    # TODO: Votes not fixed.
    # results = db.query(models.Posts, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Posts.id, isouter=True).group_by(models.Posts.id).filter(models.Posts.title.contains(search)).limit(limit).offset(skip).all()
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Posts found.")
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post: CreatePost, db: Session = Depends(get_db), current_user: int  = Depends(utils.get_current_user)):
    post = models.Posts(**post.dict(), owner_id= current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    if post is None:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Post not created")
    return post


@router.get("/{id}", status_code=status.HTTP_302_FOUND, response_model=PostResponse)
def get_post(id: int, db: Session = Depends(get_db), current_user: int  = Depends(utils.get_current_user)):
    post = db.query(models.Posts).filter(models.Posts.id == id).first()
    # TODO: Votes not fixed.
    # post = db.query(models.Posts, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Posts.id, isouter=True).group_by(models.Posts.id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {id} not found")
    return post


@router.put("/{id}",status_code=status.HTTP_202_ACCEPTED, response_model=PostResponse)
def update_post(id: int, post: UpdatePost, db: Session = Depends(get_db), current_user: int  = Depends(utils.get_current_user)):
    posts = db.query(models.Posts).filter(models.Posts.id == id)
    post_db = posts.first()
    if post_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post_db.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    posts.update(post.dict(), synchronize_session= False)
    db.commit()
    return posts.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db), current_user: int  = Depends(utils.get_current_user)):
    posts_query = db.query(models.Posts).filter(models.Posts.id == id)
    post = posts_query.first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    posts_query.delete(synchronize_session=False)
    db.commit()
