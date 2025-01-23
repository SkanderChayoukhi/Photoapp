#!/usr/bin/env python3

from fastapi import Path
from pydantic import BaseModel, Field
from typing import List
from beanie import Document


class Dname:
    STR = "The display name of the photographer"
    MAX_LENGTH = 16
    PATH_PARAM = Path(..., title=STR, max_length=MAX_LENGTH, examples=["rdoisneau"])


class Fname:
    STR = "The first name of the photographer"
    MAX_LENGTH = 32


class Lname:
    STR = "The last name of the photographer"
    MAX_LENGTH = 32


class Interests:
    STR = "The interests of the photographer"


class PhotographerDesc(BaseModel):
    display_name: str = Field(None, title=Dname.STR, max_length=Dname.MAX_LENGTH, examples=["rdoisneau"])
    first_name: str = Field(None, title=Fname.STR, max_length=Fname.MAX_LENGTH, examples=["robert"])
    last_name: str = Field(None, title=Lname.STR, max_length=Lname.MAX_LENGTH, examples=["doisneau"])
    interests: List[str] = Field(None, title=Interests.STR, examples=[["street", "portrait"]])
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "display_name": "rdoisneau",
                    "first_name": "robert",
                    "last_name": "doisneau",
                    "interests": ["street", "portrait"],
                }
            ]
        }
    }


class PhotographerDigest(BaseModel):
    display_name: str
    link: str


class Photographers(BaseModel):
    items: List[PhotographerDigest]
    has_more: bool


# Model for Mongo
class Photographer(Document, PhotographerDesc):
    pass
