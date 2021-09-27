from typing import Optional

import pydantic
from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    """
    Used to attach to all models. I got it from
    https://www.mongodb.com/developer/quickstart/python-quickstart-fastapi/
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class MongoModel(BaseModel):
    """
    Base mongo model that attaches objectid automatically
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")


class AllOptional(pydantic.main.ModelMetaclass):
    """
    Metaclass a pydantic model to turn all its properties to optional.
    Useful for creating update models automatically

    I got it from stackoverflow
    """

    def __new__(self, name, bases, namespaces, **kwargs):
        annotations = namespaces.get("__annotations__", {})
        for base in bases:
            annotations = {**annotations, **base.__annotations__}
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = Optional[annotations[field]]
        namespaces["__annotations__"] = annotations
        return super().__new__(self, name, bases, namespaces, **kwargs)
