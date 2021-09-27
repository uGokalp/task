from core import config
from db.crud import CrudService
from models.book import BookModel
from models.user import UserModel
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

settings = config.Settings()  # Settings read from .env

client = AsyncIOMotorClient(settings.db_uri)
db = client.get_database(settings.db_name)
users_collection: AsyncIOMotorCollection = db.users
books_collection: AsyncIOMotorCollection = db.books


def get_user_service() -> CrudService:
    """
    User specific crud service. To be used as a dependency.
    """
    return CrudService(collection=users_collection, model_cls=UserModel)


def get_book_service() -> CrudService:
    """
    Book specific crud service. To be used as a dependency.
    """
    return CrudService(collection=books_collection, model_cls=BookModel)
