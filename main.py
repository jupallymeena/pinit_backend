
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import random
import string
import shutil
import os
from datetime import datetime

from database import session, engine
import database_model
from models import LoginRequest

app = FastAPI()

database_model.Base.metadata.create_all(bind=engine)

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from fastapi.staticfiles import StaticFiles
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def generate_unique_id(length=8):
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choices(characters, k=length))

@app.get("/")
def root():
    return {"message": "API was running"}



@app.post("/register")
def register_user(db: Session = Depends(get_db)):
    unique_id = generate_unique_id(length=8)
    new_user = database_model.UserImage(
        unique_id=unique_id,
        image_url=None
    )
    db.add(new_user)
    db.commit()
    return {"unique_id": unique_id}

# -------------------- GET USERS --------------------
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(database_model.UserImage.unique_id).distinct().all()
    return {"users": [u[0] for u in users]}

# -------------------- GET IMAGES --------------------
@app.get("/get-images/{unique_id}")
def get_images(unique_id: str, db: Session = Depends(get_db)):
    user_exists = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    images = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id,
        database_model.UserImage.image_url.isnot(None)
    ).all()

    # return {
    #     "unique_id": unique_id,
    #     "total_images": len(images),
    #     "images": [
    #         {"image_url": img.image_url, "created_at": img.created_at}
    #         for img in images
    #     ]
    # }
    return {
    "unique_id": unique_id,
    "total_images": len(images),
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
        "images": [{"image_url": img.image_url, "created_at": img.created_at} for img in images]
    }
@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    unique_id: str = Form(...),
    device_id: str = Form(...),
    device_model: str = Form(...),
    db: Session = Depends(get_db)
):

    user_exists = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()

    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    filename = f"{unique_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"https://pinit-backend-1.onrender.com/uploads/{filename}"

    new_image = database_model.UserImage(
        unique_id=unique_id,
        image_url=image_url,
        device_id=device_id,
        device_model=device_model,
        created_at=datetime.utcnow()
    )

    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {
        "image_url": image_url,
        "device_id": device_id,
        "device_model": device_model,
        "created_at": new_image.created_at
    }

@app.delete("/delete-image")
def delete_image(image_url: str = Form(...), db: Session = Depends(get_db)):
    image = db.query(database_model.UserImage).filter(
        database_model.UserImage.image_url == image_url
    ).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # delete file from uploads folder
    filename = image_url.split("/uploads/")[-1]
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(image)
    db.commit()

    return {"message": "Image deleted successfully"}

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

    return {"message": f"User {unique_id} and all images deleted"}

# -------------------- FAVICON --------------------
@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon"}

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