
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import random
import string
import shutil
import os
from datetime import datetime

from database import session, engine
import database_model

app = FastAPI()

database_model.Base.metadata.create_all(bind=engine)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    return {"message": "API is running"}

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

    return {
        "unique_id": unique_id,
        "total_images": len(images),
        "images": [
            {"image_url": img.image_url, "created_at": img.created_at}
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
    db: Session = Depends(get_db)
):
    # Check if user exists
    user_exists = db.query(database_model.UserImage).filter(
        database_model.UserImage.unique_id == unique_id
    ).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Save file locally
    filename = f"{unique_id}_{int(datetime.utcnow().timestamp())}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Build URL
    image_url = f"https://http://192.168.1.14:8000/uploads/{filename}"

    # Save in SQL database with timestamp
    new_image = database_model.UserImage(
        unique_id=unique_id,
        image_url=image_url,
        created_at=datetime.utcnow()
    )
    db.add(new_image)
    db.commit()
    db.refresh(new_image)

    return {
        "message": "Image uploaded successfully",
        "image_url": image_url,
        "created_at": new_image.created_at
    }

# -------------------- FAVICON --------------------
@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon"}
