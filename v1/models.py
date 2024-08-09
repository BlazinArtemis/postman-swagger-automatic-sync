from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    def as_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "date_created": self.date_created.isoformat()
        }

