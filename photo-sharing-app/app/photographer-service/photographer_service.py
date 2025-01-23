#!/usr/bin/env python3

import uvicorn

from fastapi import Body, FastAPI, HTTPException, Path
from starlette.responses import Response
from fastapi.logger import logger

from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
import pymongo
from models import (
    Dname,
    Photographer,
    PhotographerDesc,
    Photographers,
    PhotographerDigest,
)
import docs

from beanie import init_beanie
import motor


class Settings(BaseSettings):
    mongo_host: str = "mongo"
    mongo_port: str = "27017"
    mongo_user: str = ""
    mongo_password: str = ""
    database_name: str = "photographers"
    auth_database_name: str = "photographers"


settings = Settings()


# FastAPI logging
# gunicorn_logger = logging.getLogger('gunicorn.error')
# logger.handlers = gunicorn_logger.handlers


################################################################################
@asynccontextmanager
async def startup_event(application: FastAPI):
    conn = f"mongodb://"
    if settings.mongo_user:
        conn += f"{settings.mongo_user}:{settings.mongo_password}@"
    conn += f"{settings.mongo_host}:{settings.mongo_port}"
    conn += f"/{settings.database_name}?authSource={settings.auth_database_name}"
    client = motor.motor_asyncio.AsyncIOMotorClient(conn)
    await init_beanie(
        database=client[settings.database_name], document_models=[Photographer]
    )
    yield


app = FastAPI(
    title="Photographer Service",
    openapi_tags=docs.photographer_metadata,
    lifespan=startup_event,
)


################################################################################
@app.post(
    "/photographers",
    status_code=201,
    summary="Upload a new Photographer",
    description=docs.create_photographers_doc,
    tags=["photographers"],
)
async def create_photographer(
    response: Response,
    photographer_desc: PhotographerDesc = Body(
        example={
            "display_name": "rdoisneau",
            "first_name": "robert",
            "last_name": "doisneau",
            "interests": ["street", "portrait"],
        }
    ),
):
    try:
        check = await Photographer.find_one(
            Photographer.display_name == photographer_desc.display_name
        )
        if check is None:
            new_photographer = Photographer(**dict(photographer_desc))
            await new_photographer.insert()
            response.headers["Location"] = f"/photographer/{photographer_desc.display_name}"
            return new_photographer  # Retourner le photographe créé
        else:
            raise HTTPException(status_code=409, detail="Conflict")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


################################################################################
@app.head(
    "/photographers",
    status_code=200,
    summary="Retrieve the count of Photographers",
    description=docs.head_photographers_doc,
    tags=["photographers"],
)
async def head_photographers(response: Response) -> None:
    try:
        response.headers["X-Total-Count"] = str(await Photographer.count())
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


################################################################################
@app.get(
    "/photographers",
    status_code=200,
    summary="Get a list of Photographers",
    description=docs.get_photographers_doc,
    tags=["photographers"],
)
async def get_photographers(
    response: Response, offset: int = 0, limit: int = 10
) -> Photographers:
    photographer_digests = list()
    last_id = 0
    try:
        response.headers["X-Total-Count"] = str(await Photographer.count())
        async for result in Photographer.find().sort("_id").skip(offset).limit(limit):
            digest = PhotographerDigest(
                display_name=result.display_name,
                link="/photographer/" + result.display_name,
            )
            last_id = result.id
            photographer_digests.append(digest)
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")
    has_more = await Photographer.find(Photographer.id > last_id).to_list()
    return {"items": photographer_digests, "has_more": True if len(has_more) else False}


################################################################################
@app.get(
    "/photographer/{display_name}",
    response_model=PhotographerDesc,
    status_code=200,
    summary="Get a Photographer",
    description=docs.get_photographer_doc,
    tags=["photographer"],
)
async def get_photographer(
    display_name: str = Path(
        title="The display name of the photographer",
        max_length=16,
        examples="rdoisneau",
    )
):
    try:
        photographer = await Photographer.find_one(
            Photographer.display_name == display_name
        )
        if photographer is not None:
            return photographer
        else:
            raise HTTPException(status_code=404, detail="Photographer does not exist")
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


################################################################################
@app.put(
    "/photographer/{display_name}",
    status_code=200,
    summary="Update a Photographer",
    description=docs.put_photographer_doc,
    tags=["photographer"],
)
async def update_photographer(
    display_name: str = Path(
        title="The display name of the photographer",
        max_length=16,
        examples="rdoisneau",
    ),
    photographer: PhotographerDesc = Body(
        example={
            "display_name": "rdoisneau",
            "first_name": "robert",
            "last_name": "doisneau",
            "interests": ["street", "portrait"],
        }
    ),
) -> None:
    try:
        found = await Photographer.find_one(Photographer.display_name == display_name)
        if found is None:
            raise HTTPException(status_code=503, detail="Not Found")
        elif display_name != photographer.display_name:
            raise HTTPException(
                status_code=422,
                detail="path param and body display_name must be identical",
            )
        else:
            await found.set(dict(photographer))
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


################################################################################
@app.delete(
    "/photographer/{display_name}",
    status_code=204,
    summary="Delete a Photographer",
    description="Delete a photographer by their display name.",
    tags=["photographer"],
)
async def delete_photographer(
    display_name: str = Path(
        title="The display name of the photographer",
        max_length=16,
        examples="rdoisneau",
    )
):
    try:
        photographer = await Photographer.find_one(
            Photographer.display_name == display_name
        )
        if photographer is None:
            raise HTTPException(status_code=404, detail="Photographer does not exist")
        await photographer.delete()  # Delete the photographer from the database
    except pymongo.errors.ServerSelectionTimeoutError:
        raise HTTPException(status_code=503, detail="Mongo unavailable")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    # logger.setLevel(logging.DEBUG)
else:
    # logger.setLevel(gunicorn_logger.level)
    pass
