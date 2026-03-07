from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserImage(Base):
    __tablename__ = "user_images"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(8), index=True, nullable=False)
    # image_url = Column(String, nullable=True)

    # created_at = Column(DateTime, default=datetime.utcnow)  # ✅ auto timestamp
    # id = Column(Integer, primary_key=True)
    # unique_id = Column(String)
    image_url = Column(String)
    device_id = Column(String)
    device_model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)