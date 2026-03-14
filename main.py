
# # from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
# # from sqlalchemy.orm import Session
# # import random
# # import string
# # import shutil
# # import os
# # from datetime import datetime

# # from database import session, engine
# # import database_model
# # from models import LoginRequest

# # app = FastAPI()
# from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# import random
# import string
# import shutil
# import os
# from datetime import datetime

# from database import session, engine
# import database_model
# from models import LoginRequest

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# database_model.Base.metadata.create_all(bind=engine)

# # UPLOAD_FOLDER = "uploads"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# from fastapi.staticfiles import StaticFiles
# # app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# def get_db():
#     db = session()
#     try:
#         yield db
#     finally:
#         db.close()

# def generate_unique_id(length=8):
#     characters = string.ascii_uppercase + string.digits
#     return "".join(random.choices(characters, k=length))

# @app.get("/")
# def root():
#     return {"message": "API was running"}



# @app.post("/register")
# def register_user(db: Session = Depends(get_db)):
#     unique_id = generate_unique_id(length=8)
#     new_user = database_model.UserImage(
#         unique_id=unique_id,
#         image_url=None
#     )
#     db.add(new_user)
#     db.commit()
#     return {"unique_id": unique_id}

# # -------------------- GET USERS --------------------
# @app.get("/users")
# def get_users(db: Session = Depends(get_db)):
#     users = db.query(database_model.UserImage.unique_id).distinct().all()
#     return {"users": [u[0] for u in users]}

# # -------------------- GET IMAGES --------------------
# @app.get("/get-images/{unique_id}")
# def get_images(unique_id: str, db: Session = Depends(get_db)):
#     user_exists = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id
#     ).first()

#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     images = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id,
#         database_model.UserImage.image_url.isnot(None)
#     ).all()

#     # return {
#     #     "unique_id": unique_id,
#     #     "total_images": len(images),
#     #     "images": [
#     #         {"image_url": img.image_url, "created_at": img.created_at}
#     #         for img in images
#     #     ]
#     # }
#     return {
#     "unique_id": unique_id,
#     "total_images": len(images),
#     "images": [
#         {
#             "image_url": img.image_url,
#             "created_at": img.created_at,
#             "device_id": img.device_id,
#             "device_model": img.device_model
#         }
#         for img in images
#     ]
# }

# @app.post("/login")
# def login(unique_id: str = Form(...), db: Session = Depends(get_db)):
#     user = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id
#     ).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     images = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id,
#         database_model.UserImage.image_url.isnot(None)
#     ).all()

#     return {
#         "unique_id": unique_id,
#         "images": [{"image_url": img.image_url, "created_at": img.created_at} for img in images]
#     }
# @app.post("/upload-image/")
# async def upload_image(
#     file: UploadFile = File(...),
#     unique_id: str = Form(...),
#     device_id: str = Form(...),
#     device_model: str = Form(...),
#     db: Session = Depends(get_db)
# ):

#     user_exists = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id
#     ).first()

#     if not user_exists:
#         raise HTTPException(status_code=404, detail="User not found")

#     filename = f"{unique_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"

#     file_path = os.path.join(UPLOAD_FOLDER, filename)

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     image_url = f"https://pinit-backend-1.onrender.com/uploads/{filename}"

#     new_image = database_model.UserImage(
#         unique_id=unique_id,
#         image_url=image_url,
#         device_id=device_id,
#         device_model=device_model,
#         created_at=datetime.utcnow()
#     )

#     db.add(new_image)
#     db.commit()
#     db.refresh(new_image)

#     return {
#         "image_url": image_url,
#         "device_id": device_id,
#         "device_model": device_model,
#         "created_at": new_image.created_at
#     }

# @app.delete("/delete-image")
# def delete_image(image_url: str = Form(...), db: Session = Depends(get_db)):
#     image = db.query(database_model.UserImage).filter(
#         database_model.UserImage.image_url == image_url
#     ).first()

#     if not image:
#         raise HTTPException(status_code=404, detail="Image not found")

#     # delete file from uploads folder
#     filename = image_url.split("/uploads/")[-1]
#     file_path = os.path.join(UPLOAD_FOLDER, filename)

#     if os.path.exists(file_path):
#         os.remove(file_path)

#     db.delete(image)
#     db.commit()

#     return {"message": "Image deleted successfully"}

# @app.delete("/delete-user/{unique_id}")
# def delete_user(unique_id: str, db: Session = Depends(get_db)):

#     images = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id
#     ).all()

#     if not images:
#         raise HTTPException(status_code=404, detail="User not found")

#     for img in images:
#         if img.image_url:
#             filename = img.image_url.split("/uploads/")[-1]
#             file_path = os.path.join(UPLOAD_FOLDER, filename)

#             if os.path.exists(file_path):
#                 os.remove(file_path)

#         db.delete(img)

#     db.commit()

#     return {"message": f"User {unique_id} and all images deleted"}

# # -------------------- FAVICON --------------------
# @app.get("/favicon.ico")
# def favicon():
#     return {"message": "No favicon"}

# @app.post("/web-login")
# def web_login(data: LoginRequest, db: Session = Depends(get_db)):

#     unique_id = data.unique_id

#     user = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id
#     ).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     images = db.query(database_model.UserImage).filter(
#         database_model.UserImage.unique_id == unique_id,
#         database_model.UserImage.image_url.isnot(None)
#     ).all()

#     return {
#         "unique_id": unique_id,
#         "images": [
#             {
#                 "image_url": img.image_url,
#                 "created_at": img.created_at,
#                 "device_id": img.device_id,
#                 "device_model": img.device_model
#             }
#             for img in images
#         ]
#     }
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import random
import string
import shutil
import os
from datetime import datetime

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from database import session, engine
import database_model
from models import LoginRequest

app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- DATABASE --------------------
database_model.Base.metadata.create_all(bind=engine)

# -------------------- UPLOAD FOLDER --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")


# -------------------- DB SESSION --------------------
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


# -------------------- UNIQUE ID --------------------
def generate_unique_id(length=8):
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choices(characters, k=length))


# -------------------- EXTRACT GPS --------------------
def get_gps_info(exif):
    gps_lat = None
    gps_lon = None

    gps_info = exif.get("GPSInfo")

    if gps_info:
        gps_data = {}

        for key in gps_info.keys():
            name = GPSTAGS.get(key)
            gps_data[name] = gps_info[key]

        try:
            lat = gps_data["GPSLatitude"]
            lat_ref = gps_data["GPSLatitudeRef"]

            lon = gps_data["GPSLongitude"]
            lon_ref = gps_data["GPSLongitudeRef"]

            gps_lat = float(lat[0] + lat[1] / 60 + lat[2] / 3600)
            gps_lon = float(lon[0] + lon[1] / 60 + lon[2] / 3600)

            if lat_ref != "N":
                gps_lat = -gps_lat

            if lon_ref != "E":
                gps_lon = -gps_lon

        except:
            pass

    return gps_lat, gps_lon


# -------------------- EXTRACT EXIF --------------------
def extract_exif(file_path):

    metadata = {}

    try:
        image = Image.open(file_path)
        exif_data = image._getexif()

        if exif_data:

            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = value

    except Exception as e:
        print("EXIF error:", e)

    return metadata


# -------------------- ROOT --------------------
@app.get("/")
def root():
    return {"message": "API running"}


# -------------------- REGISTER --------------------
@app.post("/register")
def register_user(db: Session = Depends(get_db)):

    unique_id = generate_unique_id()

    new_user = database_model.UserImage(
        unique_id=unique_id,
        image_url=None
    )

    db.add(new_user)
    db.commit()

    return {"unique_id": unique_id}


# -------------------- USERS --------------------
@app.get("/users")
def get_users(db: Session = Depends(get_db)):

    users = db.query(database_model.UserImage.unique_id).distinct().all()

    return {"users": [u[0] for u in users]}


# -------------------- LOGIN --------------------
@app.post("/login")
def login(unique_id: str = Form(...), db: Session = Depends(get_db)):

    user = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    images = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id,
        database_model.UserImage.image_url.isnot(None)
    ).all()

    return {
        "unique_id": unique_id,
        "images": [
            {
                "image_url": img.image_url,
                "created_at": img.created_at
            }
            for img in images
        ]
    }


# -------------------- WEB LOGIN --------------------
@app.post("/web-login")
def web_login(data: LoginRequest, db: Session = Depends(get_db)):

    unique_id = data.unique_id

    user = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    images = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id,
        database_model.UserImage.image_url.isnot(None)
    ).all()

    return {
        "unique_id": unique_id,
        "images": [
            {
                "image_url": img.image_url,
                "created_at": img.created_at,
                "device_id": img.device_id,
                "device_model": img.device_model
            }
            for img in images
        ]
    }


# -------------------- GET IMAGES --------------------
@app.get("/get-images/{unique_id}")
def get_images(unique_id: str, db: Session = Depends(get_db)):

    user = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    images = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id,
        database_model.UserImage.image_url.isnot(None)
    ).all()

    return {
        "unique_id": unique_id,
        "total_images": len(images),
        "images": [
            {
                "image_url": img.image_url,
                "device_id": img.device_id,
                "device_model": img.device_model,
                "created_at": img.created_at
            }
            for img in images
        ]
    }


# -------------------- UPLOAD IMAGE --------------------
@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    unique_id: str = Form(...),
    device_id: str = Form(...),
    device_model: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    filename = f"{unique_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # EXIF extraction
    exif = extract_exif(file_path)

    make = exif.get("Make")
    model = exif.get("Model")
    software = exif.get("Software")
    orientation = exif.get("Orientation")

    iso = exif.get("ISOSpeedRatings")
    exposure_time = exif.get("ExposureTime")
    f_number = exif.get("FNumber")
    focal_length = exif.get("FocalLength")

    datetime_original = exif.get("DateTimeOriginal")

    gps_lat, gps_lon = get_gps_info(exif)

    image_url = f"https://pinit-backend-1.onrender.com/uploads/{filename}"

    new_image = database_model.UserImage(
        unique_id=unique_id,
        image_url=image_url,
        device_id=device_id,
        device_model=device_model,

        make=make,
        model=model,
        software=software,
        orientation=orientation,

        iso=iso,
        exposure_time=exposure_time,
        f_number=f_number,
        focal_length=focal_length,

        datetime_original=datetime_original,

        gps_latitude=gps_lat,
        gps_longitude=gps_lon,

        created_at=datetime.utcnow()
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {
        "image_url": image_url,
        "device_id": device_id,
        "device_model": device_model,
        "make": make,
        "model": model,
        "iso": iso,
        "gps_latitude": gps_lat,
        "gps_longitude": gps_lon
    }


# -------------------- DELETE IMAGE --------------------
@app.delete("/delete-image")
def delete_image(image_url: str = Form(...), db: Session = Depends(get_db)):

    image = db.query(database_model.UserImage).filter(
        database_model.UserImage.image_url == image_url
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    filename = image_url.split("/uploads/")[-1]
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(image)
    db.commit()

    return {"message": "Image deleted successfully"}


# -------------------- DELETE USER --------------------
@app.delete("/delete-user/{unique_id}")
def delete_user(unique_id: str, db: Session = Depends(get_db)):

    images = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).all()

    if not images:
        raise HTTPException(status_code=404, detail="User not found")

    for img in images:

        if img.image_url:
            filename = img.image_url.split("/uploads/")[-1]
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            if os.path.exists(file_path):
                os.remove(file_path)

        db.delete(img)

    db.commit()

    return {"message": f"User {unique_id} deleted"}