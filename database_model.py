# from sqlalchemy import Column, String, Integer, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

# Base = declarative_base()

# class UserImage(Base):
#     __tablename__ = "user_images"

#     id = Column(Integer, primary_key=True, index=True)
#     unique_id = Column(String(8), index=True, nullable=False)
#     # image_url = Column(String, nullable=True)

#     # created_at = Column(DateTime, default=datetime.utcnow)  # ✅ auto timestamp
#     # id = Column(Integer, primary_key=True)
#     # unique_id = Column(String)
#     image_url = Column(String)
#     device_id = Column(String)
#     device_model = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)
from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserImage(Base):
    __tablename__ = "user_images"

    id = Column(Integer, primary_key=True, index=True)

    # user
    unique_id = Column(String(8), index=True, nullable=False)

    # image info
    image_url = Column(String)

    # device info
    device_id = Column(String)
    device_model = Column(String)

    # camera metadata
    make = Column(String)              # Apple / Samsung
    model = Column(String)             # iPhone 15 Pro
    software = Column(String)          # iOS / Android version
    orientation = Column(String)

    # camera settings
    iso = Column(String)
    exposure_time = Column(String)
    f_number = Column(String)
    focal_length = Column(String)

    # timestamps
    datetime_original = Column(String)

    # GPS metadata
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)

    # upload timestamp
    created_at = Column(DateTime, default=datetime.utcnow)