import shutil

import uvicorn
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from sqlalchemy_utils import URLType

from db import Base, SessionLocal, engine


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    created_at = Column(String)
    is_active = Column(Integer)
    title = Column(String)
    images = relationship("Images", back_populates="item")


class Images(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    url = Column(URLType)
    post_id = Column(Integer, ForeignKey('posts.id'))
    item = relationship("Post", back_populates="images")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/images")
def create_image(body: str, title: str, file: list[UploadFile] = File(...),
                 db: Session = Depends(get_db)):
    images = []
    for f in file:
        with open("media/" + f.filename, "wb") as image:
            shutil.copyfileobj(f.file, image)
            url = str("media/" + f.filename)
            images.append(Images(url=url))

    obj = Post(created_at=body, is_active=1, title=title, images=images)
    db.add(obj)
    db.commit()
    return {"message": "ok"}


@app.get("/posts")
def read_images(db: Session = Depends(get_db)):
    objs = db.query(Post).all()
    print(objs[1].images)
    return objs


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
