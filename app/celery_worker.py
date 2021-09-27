import os

from bson import ObjectId
from celery import Celery
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(".env")

broker = os.getenv("CELERY_BROKER_URL")
backend = os.getenv("CELERY_BROKER_URL")
celery = Celery("fast-api-tasks", broker=broker, backend=backend)


mongo_uri = os.getenv("MONGODB_URL")


@celery.task(name="checkout")
def checkout(book_id: str, user_id: str):
    processed_ids = []
    not_processed_ids = []
    with MongoClient(mongo_uri) as conn:
        db = conn.get_database("library")
        books_collection = db.books
        try:
            book = books_collection.find_one({"_id": ObjectId(book_id)})

            # If books is not found.
            if not book:
                raise ValueError("No book found!")

            # If book is already checked out
            if book["checked_out_by"] is not None:
                raise TypeError("Field is not empty!")

            # Update the book
            updated = books_collection.update_one(
                {"_id": ObjectId(book_id)},
                {"$set": {"checked_out_by": ObjectId(user_id)}},
            )

            if updated.acknowledged and updated.modified_count == 1:
                processed_ids.append(book_id)

        except (ValueError, TypeError, AttributeError):
            not_processed_ids.append(book_id)
    return {
        "processed_ids": processed_ids,
        "not_processed_ids": not_processed_ids,
    }
