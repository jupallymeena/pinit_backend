
from pydantic import BaseModel
from sqlalchemy import LargeBinary

class User(BaseModel):
    unique_id:str
