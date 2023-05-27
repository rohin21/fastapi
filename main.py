from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from db import engine
# import models
from routes import users, posts, auth, votes

# models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(auth.router)
app.include_router(votes.router)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return "Hello World"

