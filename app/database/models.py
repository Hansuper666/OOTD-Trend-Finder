from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, create_engine, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class OutfitImage(Base):
    __tablename__ = "outfit_images"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)  # Original source URL
    file_path = Column(String)  # Local path to the saved image
    source = Column(String)  # e.g., "pinterest"
    features = relationship("ImageFeature", back_populates="image", cascade="all, delete-orphan")
    tags = relationship("ImageTag", back_populates="image", cascade="all, delete-orphan")
    
class ImageFeature(Base):
    __tablename__ = "image_features"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("outfit_images.id", ondelete="CASCADE"))
    embedding = Column(LargeBinary)  # Vector embedding from the AI model
    image = relationship("OutfitImage", back_populates="features")

class ImageTag(Base):
    __tablename__ = "image_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("outfit_images.id", ondelete="CASCADE"))
    tag = Column(String, index=True)  # e.g., "green sneakers", "denim jacket"
    confidence = Column(Float)  # Confidence score for this tag
    image = relationship("OutfitImage", back_populates="tags")

# Database setup
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 