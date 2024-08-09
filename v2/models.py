from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

bookmark_tags = Table(
    'bookmark_tags', Base.metadata,
    Column('bookmark_id', Integer, ForeignKey('bookmarks.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    tags = relationship("Tag", secondary=bookmark_tags, back_populates="bookmarks")

    def as_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "date_created": self.date_created.isoformat()
        }

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    bookmarks = relationship("Bookmark", secondary=bookmark_tags, back_populates="tags")

