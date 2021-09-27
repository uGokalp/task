from typing import Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId
from db.crud import CrudService
from db.mongodb import get_book_service
from fastapi import Depends, Path, Response, exceptions, status
from fastapi.routing import APIRouter
from models.book import BookModel, UpdateBookModel

router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: dict(description="Book not found!")},
)


async def get_book_object_id(
    book_id: str = Path(..., example="615019d8ab766b8cc37cebf7")
) -> Optional[ObjectId]:
    """
    Cast string object id to ObjectId if possible
    Otherwise return None
    """
    try:
        return ObjectId(book_id)
    except (InvalidId, TypeError):
        return None


@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def find_book(
    book_id: ObjectId = Depends(get_book_object_id),
    book_service: CrudService = Depends(get_book_service),
):
    """
    Find a **book** by its objectid.
    If **book_id** is not a valid objectid or **book_id**
    does not belong to a book raise 404
    """
    book = await book_service.find_model_by_id(book_id)
    if book:
        return book
    raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookModel, book_service: CrudService = Depends(get_book_service)
):
    """
    Creates a new **book** in the database.
    """
    # Plain create the model
    result = await book_service.create_model(book)
    if result:
        return result
    raise exceptions.HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


@router.patch("/{book_id}", status_code=status.HTTP_200_OK)
async def update_book(
    book: UpdateBookModel,
    book_id: ObjectId = Depends(get_book_object_id),
    book_service: CrudService = Depends(get_book_service),
):
    """
    Finds and updates **book** in the database
    Raises 404 if **book** is not found
    """
    # Try to find the book
    book_found = await book_service.find_model_by_id(book_id)
    # Swap the old props with new
    if book_found:
        update_data = book.dict(exclude_unset=True)
        updated_book = book_found.copy(update=update_data)
        book_in_db = await book_service.update_model(
            book_found.id, updated_book
        )
        return book_in_db
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(
    book_id: ObjectId = Depends(get_book_object_id),
    book_service: CrudService = Depends(get_book_service),
):
    # Try to remove
    deleted = await book_service.remove_model(book_id)
    # Check if removed
    if deleted:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
