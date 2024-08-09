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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

