from typing import Optional

from bson import ObjectId

from .pyobjectid import AllOptional, MongoModel, PyObjectId


class BookModel(MongoModel):
    """
    Base model used by books.
    """

    name: str
    author: str
    isbn13: str
    num_pages: int
    checked_out_by: Optional[PyObjectId]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "The Hitchhiker's Guide to the Galaxy",
                "author": "Douglas Adams",
                "isbn13": "978-0-345-39180-3",
                "num_pages": 224,
                "checked_out": None,
            }
        }


class UpdateBookModel(BookModel, metaclass=AllOptional):
    """
    All optional fields for the BookModel
    """

    pass
