from models import Album
from uuid import uuid4
from mongoengine import DoesNotExist

def create_album_in_db(display_name: str, title: str, description: str, cover_photo_id: str = None):
    album_id = str(uuid4())
    album = Album(
        display_name=display_name,
        album_id=album_id,
        title=title,
        description=description,
        cover_photo_id=cover_photo_id,
    )
    album.save()
    return album


def mongo_get_albums_by_name(display_name, offset, limit):
    try:
        qs = Album.objects(display_name=display_name).order_by('-created_at').skip(offset).limit(limit)
        has_more = qs.count(with_limit_and_skip=False) > (offset + limit)
    except Exception as e:
        raise
    return has_more, qs


def mongo_get_album_by_id(display_name: str, album_id: str):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if album:
            album_data = album.to_mongo().to_dict()
            album_data.pop('_id')  # Remove internal MongoDB ID
            return album_data
        return None
    except Exception as e:
        raise


def mongo_update_album(display_name: str, album_id: str, title: str = None, description: str = None, cover_photo_id: str = None):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if not album:
            return None
        
        update_fields = {}
        if title is not None:
            update_fields["title"] = title
        if description is not None:
            update_fields["description"] = description
        if cover_photo_id is not None:
            update_fields["cover_photo_id"] = cover_photo_id
        if not update_fields:
            return None    # Prevent accidental empty updates
        
        album.update(**update_fields)
        album.reload()
        
        album_data = album
        # album._data.pop('id') # Remove internal MongoDB ID
        return album
    except Exception as e:
        raise



def mongo_delete_album(display_name: str, album_id: str):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if not album:
            return False
        album.delete()
        return True
    except Exception as e:
        raise

def mongo_add_photo_to_album(display_name: str, album_id: str, photo_id: str):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if not album:
            return None
        if photo_id in album.photos:
            return album
        album.update(push__photos=photo_id)
        album.reload()
        return album
    except Exception as e:
        raise


def mongo_remove_photo_from_album(display_name: str, album_id: str, photo_id: str):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if not album :
            return None
        if photo_id in album.photos :
            album.update(pull__photos=photo_id)
            album.reload()
            
        return album
    except Exception as e:
        raise
    
def mongo_get_photos_in_album(display_name: str, album_id: str):
    try:
        album = Album.objects(display_name=display_name, album_id=album_id).first()
        if not album:
            return None
        return album.photos
    except Exception as e:
        raise        

def serialize_album(album):
    album_dict = album.to_mongo().to_dict()
    album_dict["_id"] = str(album_dict["_id"])
    return album_dict    