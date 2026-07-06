"""
Article / Health Blog — SQLAlchemy Model
Admin creates & manages articles; patients can read them.
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    title       = Column(String(400), nullable=False)
    slug        = Column(String(450), unique=True, nullable=False, index=True)
    excerpt     = Column(String(600), nullable=True)
    content     = Column(Text, nullable=False)
    category    = Column(String(100), nullable=True, index=True)
    author_name = Column(String(200), nullable=False, default="PraDoc Team")
    cover_image_url = Column(String(600), nullable=True)

    is_published = Column(Boolean, default=False, nullable=False, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    created_at   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Article {self.title!r} published={self.is_published}>"
