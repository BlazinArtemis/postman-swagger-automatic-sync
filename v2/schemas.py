from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

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

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

