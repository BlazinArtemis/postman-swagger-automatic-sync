from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import json
import datetime
from typing import List

from database import SessionLocal, engine
import models
import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/bookmarks", response_model=schemas.Bookmark)
def create_bookmark(bookmark: schemas.BookmarkCreate, db: Session = Depends(get_db)):
    db_bookmark = models.Bookmark(
        url=bookmark.url,
        title=bookmark.title,
        description=bookmark.description,
        date_created=datetime.datetime.utcnow()
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@app.get("/bookmarks", response_model=List[schemas.Bookmark])
def read_bookmarks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    bookmarks = db.query(models.Bookmark).offset(skip).limit(limit).all()
    return bookmarks

@app.put("/bookmarks/{bookmark_id}", response_model=schemas.Bookmark)
def update_bookmark(bookmark_id: int, bookmark: schemas.BookmarkCreate, db: Session = Depends(get_db)):
    db_bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if db_bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db_bookmark.url = bookmark.url
    db_bookmark.title = bookmark.title
    db_bookmark.description = bookmark.description
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@app.get("/bookmarks/download")
def download_bookmarks(db: Session = Depends(get_db)):
    bookmarks = db.query(models.Bookmark).all()
    bookmarks_dict = [b.as_dict() for b in bookmarks]
    with open("bookmarks.json", "w") as file:
        json.dump(bookmarks_dict, file)
    return FileResponse("bookmarks.json", media_type='application/json', filename="bookmarks.json")

@app.post("/tags", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = models.Tag(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.get("/tags", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tags = db.query(models.Tag).offset(skip).limit(limit).all()
    return tags

@app.post("/bookmarks/{bookmark_id}/tags/{tag_id}")
def add_tag_to_bookmark(bookmark_id: int, tag_id: int, db: Session = Depends(get_db)):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if bookmark is None or tag is None:
        raise HTTPException(status_code=404, detail="Bookmark or Tag not found")
    bookmark.tags.append(tag)
    db.commit()
    return {"message": "Tag added to bookmark"}

@app.get("/bookmarks/tags/{tag_id}", response_model=List[schemas.Bookmark])
def get_bookmarks_by_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag.bookmarks

@app.delete("/bookmarks/{bookmark_id}/tags/{tag_id}")
def remove_tag_from_bookmark(bookmark_id: int, tag_id: int, db: Session = Depends(get_db)):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if bookmark is None or tag is None:
        raise HTTPException(status_code=404, detail="Bookmark or Tag not found")
    bookmark.tags.remove(tag)
    db.commit()
    return {"message": "Tag removed from bookmark"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

