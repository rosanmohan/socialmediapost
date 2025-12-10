"""
Database models and session management
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import config

Base = declarative_base()

class NewsItem(Base):
    """Stores fetched news articles"""
    __tablename__ = "news_items"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000), nullable=False)
    source = Column(String(200))
    published_at = Column(DateTime, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Float, default=0.0)
    used_in_post = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relationship
    posts = relationship("Post", back_populates="news_item")

class Post(Base):
    """Stores generated posts"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news_items.id"))
    script = Column(Text, nullable=False)
    caption = Column(String(500))
    hashtags = Column(String(500))
    video_path = Column(String(1000))
    thumbnail_path = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    news_item = relationship("NewsItem", back_populates="posts")
    publish_logs = relationship("PublishLog", back_populates="post")

class PublishLog(Base):
    """Stores publishing status for each platform"""
    __tablename__ = "publish_logs"
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    platform = Column(String(50), nullable=False)  # instagram, youtube, facebook
    status = Column(String(50), nullable=False)  # success, failed, pending
    response = Column(Text)
    posted_at = Column(DateTime, nullable=True)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Relationship
    post = relationship("Post", back_populates="publish_logs")

class SystemLog(Base):
    """Stores system-level logs and errors"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    level = Column(String(20), nullable=False)  # info, warning, error
    message = Column(Text, nullable=False)
    component = Column(String(100))  # news_service, content_generator, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(Text)  # JSON string for additional data (renamed from metadata to avoid SQLAlchemy conflict)

# Database setup
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

