from collections import defaultdict
from typing import Dict, List

from bson.objectid import ObjectId
from celery_worker import checkout
from db.crud import CrudService
from db.mongodb import get_book_service, get_user_service
from fastapi import Body, Depends, Response, status
from fastapi.routing import APIRouter
from routers.books import get_book_object_id
from routers.users import get_user_object_id

router = APIRouter(
    prefix="",
    tags=["interactions"],
)


@router.post("/checkout/{user_id}", status_code=status.HTTP_201_CREATED)
async def checkout_book(
    book_ids: List[str] = Body(...),
    user_id: ObjectId = Depends(get_user_object_id),
    book_service: CrudService = Depends(get_book_service),
):
    """
    If book is not checkedout then checkout book
    else return error
    """

    # Turn books ids into object ids
    obook_ids = [await get_user_object_id(o) for o in book_ids]
    obook_ids = list(filter(None, obook_ids))

    # First query the database to get the ids of matches
    id_cursor = book_service.collection.find(
        {
            "$and": [
                {"_id": {"$in": obook_ids}},
                {"checked_out_by": {"$eq": None}},
            ]
        },
        {"_id": 1},
    )
    # Get only the ids, use this compare okay ids with not okay ids,
    # to return processed and unprocessed ids
    okay_book_ids = [str(res["_id"]) async for res in id_cursor]
    not_okay_book_ids = list(set(book_ids) ^ set(okay_book_ids))

    # If # of books to checkout is > 100_000 as per the guideline
    # Run the celery task
    if len(book_ids) >= 5:
        tasks = []
        for book_id in okay_book_ids:
            tasks.append(checkout.delay(book_id, str(user_id)))
        results = [t.get() for t in tasks]
        return join_on_key(results, ["processed_ids", "not_processed_ids"])

    # Query the database and update each. Use update many because it is faster
    updates = await book_service.collection.update_many(
        {
            "$and": [
                {"_id": {"$in": obook_ids}},
                {"checked_out_by": {"$eq": None}},
            ]
        },
        {"$set": {"checked_out_by": user_id}},
    )

    # I suspect for most cases this won't be a problem, but
    # as a cautionary check I make sure at least the lengths match
    if updates.modified_count != len(okay_book_ids):
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return {
        "processed_ids": okay_book_ids,
        "not_processed_ids": not_okay_book_ids,
    }


@router.post("/return/{book_id}", status_code=status.HTTP_201_CREATED)
async def return_book(
    book_id: ObjectId = Depends(get_book_object_id),
    user_id: str = Body(...),
    book_service: CrudService = Depends(get_book_service),
    user_service: CrudService = Depends(get_user_service),
):
    """
    Implementation works by removing the attached **user**
    from the book, if there is any.

    If the book is checked out by another user then 404 is returned.
    """
    user = await user_service.find_model_by_id(
        await get_user_object_id(user_id)
    )
    book = await book_service.find_model_by_id(book_id)

    # If the book is not found return 404
    if not book:
        return Response(
            content="Book not found!", status_code=status.HTTP_404_NOT_FOUND
        )

    # If the book is checked out by another user return 404
    if book.checked_out_by != user.id:
        return Response(
            content="Book is checked out by another user!",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    # Can clear
    book.checked_out_by = None
    updated = await book_service.update_model(book.id, book)
    if updated:
        return Response(
            content="Book returned successfully!",
            status_code=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            content="An error occured",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def join_on_key(data: List[dict], keys: List[str]):
    out: Dict[str, list] = {k: [] for k in keys}
    for d in data:
        for k, v in d.items():
            if v:
                out[k].append(v[0])
    return out
