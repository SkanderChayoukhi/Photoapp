from mongoengine import Document, StringField, ListField, DateTimeField
from datetime import datetime
from pydantic import BaseModel
from typing import Optional



class Album(Document):
    display_name = StringField(required=True, max_length=120)
    album_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    description = StringField()
    cover_photo_id = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    photos = ListField(StringField())  # List of photo IDs

    meta = {'collection': 'albums'}  # Ensuring consistency in MongoDB collection name


class AlbumCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cover_photo_id: Optional[str] = None

class AlbumUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_photo_id: Optional[str] = None


class PhotoAdd(BaseModel):
    photo_id:str
