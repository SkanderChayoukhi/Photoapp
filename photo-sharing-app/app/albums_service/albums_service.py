#!/usr/bin/env python3

import uvicorn
import requests
from requests.exceptions import RequestException
import io
import zipfile
from fastapi.responses import StreamingResponse


import logging
from fastapi import FastAPI, HTTPException
from mongoengine import connect
from pydantic_settings import BaseSettings
from albums_mongo_wrapper import *
from models import (
    AlbumCreate,
    AlbumUpdate,
    PhotoAdd
)

# Configuration Settings
class Settings(BaseSettings):
    mongo_host: str = "mongo-service"
    mongo_port: str = "27017"
    mongo_user: str = ""
    mongo_password: str = ""
    database_name: str = "albums_db"
    auth_database_name: str = "albums"

    photographer_host: str = "photographer-service"
    photographer_port: str = "80"
    photo_host: str = "photo-service"
    photo_port: str = "8001"

settings = Settings()

# Initialize FastAPI app
app = FastAPI(title="Albums Service")

# Logging setup
gunicorn_logger = logging.getLogger("gunicorn.error")
logger = logging.getLogger(__name__)
logger.handlers = gunicorn_logger.handlers

# Construct service URLs
photographer_service = f"http://{settings.photographer_host}:{settings.photographer_port}/"
photo_service = f"http://{settings.photo_host}:{settings.photo_port}/"

@app.on_event("startup")
def startup_event():
    conn = f"mongodb://"
    if settings.mongo_user:
        conn += f"{settings.mongo_user}:{settings.mongo_password}@"
    conn += f"{settings.mongo_host}:{settings.mongo_port}/{settings.database_name}?authSource={settings.auth_database_name}"
    connect(settings.database_name, host=conn)

@app.post("/photographers/{display_name}/albums", status_code=201)
def create_album(display_name: str, album: AlbumCreate):
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")
    
    try:
        album = create_album_in_db(display_name, album.title, album.description, album.cover_photo_id)
        return serialize_album(album)
    except Exception as e:
        logger.error(f"Error creating album: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



    

@app.get("/photographers/{display_name}/albums", status_code=200)
def get_albums(display_name: str, offset: int = 0, limit: int = 10):
    logger.info("Getting albums...")            
    list_of_albums = list()
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=500000000)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        # elif response.status_code == 503:
        #     raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Fetch albums from database
    try:
        has_more, albums = mongo_get_albums_by_name(display_name, offset, limit)
        if not albums:
            raise HTTPException(status_code=204, detail="No Albums Found")
        
        for album in albums:
            album_data = album.to_mongo().to_dict()
            album_data.pop('_id')  # Remove internal MongoDB ID
            list_of_albums.append(album_data)
    
    except Exception as e:
        logger.error(f"Error retrieving albums: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"items": list_of_albums, "has_more": has_more}





@app.get("/photographers/{display_name}/albums/{album_id}", status_code=200)
def get_album(display_name: str, album_id: str):
    logger.info(f"Retrieving album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=500)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        # elif response.status_code == 503:
        #     raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Fetch album from database
    try:
        album_data = mongo_get_album_by_id(display_name, album_id)
        if not album_data:
            raise HTTPException(status_code=404, detail="Album Not Found")
        return album_data
    
    except Exception as e:
        logger.error(f"Error retrieving album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.put("/photographers/{display_name}/albums/{album_id}", status_code=200)
def update_album(display_name: str, album_id: str, album: AlbumUpdate):
    logger.info(f"Updating album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=500)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        # elif response.status_code == 503:
        #     raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Update album in database
    try:
        if not any([album.title, album.description, album.cover_photo_id]):
         raise HTTPException(status_code=400, detail="At least one field must be updated")
        updated_album = mongo_update_album(display_name, album_id, album.title, album.description, album.cover_photo_id)
        if not updated_album:
            raise HTTPException(status_code=404, detail="Album Not Found")
        return serialize_album(updated_album)
    
    except Exception as e:
        logger.error(f"Error updating album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")






@app.delete("/photographers/{display_name}/albums/{album_id}", status_code=200)
def delete_album(display_name: str, album_id: str):
    logger.info(f"Deleting album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=500)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        # elif response.status_code == 503:
        #     raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Delete album from database
    try:
        deleted = mongo_delete_album(display_name, album_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Album Not Found")
        return {"message": "Album successfully deleted"}
    
    except Exception as e:
        logger.error(f"Error deleting album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.post("/photographers/{display_name}/albums/{album_id}/photos", status_code=201)
def add_photo_to_album(display_name: str, album_id: str, photo:PhotoAdd):
    logger.info(f"Adding photo {photo.photo_id} to album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=5000000)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Check if photo exists
    try:
        response = requests.get(f"{photo_service}photo/{display_name}/{photo.photo_id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photo Not Found")
        # elif response.status_code == 503:
        #     raise HTTPException(status_code=503, detail="Photo Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photo Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photo Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photo Service Unreachable")
    
    # Add photo to album in database
    try:
        updated_album = mongo_add_photo_to_album(display_name, album_id, photo.photo_id)
        if not updated_album:
            raise HTTPException(status_code=404, detail="Album Not Found")
        return serialize_album(updated_album)
    
    except Exception as e:
        logger.error(f"Error adding photo {photo.photo_id} to album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.delete("/photographers/{display_name}/albums/{album_id}/photos/{photo_id}", status_code=200)
def remove_photo_from_album(display_name: str, album_id: str, photo_id: str):
    logger.info(f"Removing photo {photo_id} from album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}", timeout=50000000)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Check if photo exists
    try:
        response = requests.get(f"{photo_service}photo/{display_name}/{photo_id}", timeout=500)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photo Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photo Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photo Service")
    # except requests.exceptions.Timeout:
    #     raise HTTPException(status_code=504, detail="Photo Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photo Service Unreachable")
    
    # Remove photo from album in database
    try:
        updated_album = mongo_remove_photo_from_album(display_name, album_id, photo_id)
        if not updated_album:
            raise HTTPException(status_code=404, detail="Album Not Found or Photo Not Present")
        return serialize_album(updated_album)
    
    except Exception as e:
        logger.error(f"Error removing photo {photo_id} from album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")





@app.get("/photographers/{display_name}/albums/{album_id}/photos", status_code=200)
def get_photos_in_album(display_name: str, album_id: str):
    logger.info(f"Retrieving photos from album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}",timeout=500)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    # except requests.exceptions.Timeout:
    #     raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")
    
    # Retrieve photos from album in database
    try:
        album_photos = mongo_get_photos_in_album(display_name, album_id)
        if not album_photos:
            raise HTTPException(status_code=404, detail="Album Not Found or No Photos in Album")
        
        # Retrieve metadata from photo-service
        photos_metadata = []
        for photo_id in album_photos:
            try:
                response = requests.get(f"{photo_service}photo/{display_name}/{photo_id}/attributes", timeout=500)
                if response.status_code == 200:
                    photos_metadata.append(response.json())
            except requests.exceptions.RequestException:
                logger.warning(f"Could not retrieve metadata for photo {photo_id}")
                continue
        
        return {"photos": photos_metadata}
    
    except Exception as e:
        logger.error(f"Error retrieving photos for album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


@app.get("/photographers/{display_name}/albums/{album_id}/photos-archive", status_code=200)
def get_photos_in_album(display_name: str, album_id: str):
    logger.info(f"Retrieving photos from album {album_id} for photographer {display_name}...")
    
    # Check if photographer exists
    try:
        response = requests.get(f"{photographer_service}photographer/{display_name}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Photographer Not Found")
        elif response.status_code == 503:
            raise HTTPException(status_code=503, detail="Photographer Service Unavailable")
        # elif response.status_code != 200:
        #     raise HTTPException(status_code=response.status_code, detail="Error contacting Photographer Service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Photographer Service Timeout")
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Photographer Service Unreachable")

    # Retrieve photo IDs from album
    try:
        album_photos = mongo_get_photos_in_album(display_name, album_id)
        if not album_photos:
            raise HTTPException(status_code=404, detail="Album Not Found or No Photos in Album")
        
        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for photo_id in album_photos:
                try:
                    # Fetch actual photo content from Photo Service
                    response = requests.get(f"{photo_service}photo/{display_name}/{photo_id}", timeout=500)
                    if response.status_code == 200:
                        # Write the photo to the ZIP file
                        zip_file.writestr(f"{photo_id}.jpg", response.content)
                except requests.exceptions.RequestException:
                    logger.warning(f"Could not retrieve photo {photo_id}")
                    continue
        
        # Prepare ZIP for download
        zip_buffer.seek(0)
        return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename=album_{album_id}.zip"})
    
    except Exception as e:
        logger.error(f"Error retrieving photos for album {album_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80, log_level="info")
