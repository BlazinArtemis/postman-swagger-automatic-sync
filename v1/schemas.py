from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookmarkBase(BaseModel):
    url: str
    title: str
    description: Optional[str] = None

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id: int
    date_created: datetime

    class Config:
        from_attributes = True

