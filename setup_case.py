import requests
import click
from faker import Faker
from faker.providers import isbn, person, internet, python
from app.models.user import UserModel
from app.models.book import BookModel
from pymongo import MongoClient
import json


ENDPOINT = "http://localhost:8000/"
CREATE_BOOK = ENDPOINT + "books/"
CREATE_USER = ENDPOINT + "users/"


def fake_book():
    return BookModel(
        name=fake.domain_word(),
        author=fake.name(),
        isbn13=fake.isbn13(),
        num_pages=fake.pyint(100, 500),
    )


def fake_user():
    return UserModel(
        email=fake.free_email(),
        username=fake.user_name(),
        password=fake.password(),
    )


def post_fake_user():
    """Simple program that greets NAME for a total of COUNT times."""
    user = fake_user()
    p = requests.post(CREATE_USER, data=user.json(exclude={"id"}))
    return p


def post_fake_book():
    book = fake_book()
    p = requests.post(CREATE_BOOK, data=book.json(exclude={"id"}))
    return p


def create_mongo_users(nusers):
    with MongoClient("mongodb://root:root@localhost:27017") as conn:
        users_col = conn.get_database("library").users
        users = [fake_user().dict(by_alias=True) for _ in range(nusers)]
        users_col.insert_many(users)
    return None


def create_mongo_books(nbooks):
    with MongoClient("mongodb://root:root@localhost:27017") as conn:
        books_col = conn.get_database("library").books
        books = [fake_book().dict(by_alias=True) for _ in range(nbooks)]
        books_col.insert_many(books)
    return None


@click.group()
def cli():
    pass


@click.command()
@click.option("--user", default=0, help="Creates users")
@click.option("--book", default=0, help="Creates users")
@click.option(
    "--api",
    default=False,
    is_flag=True,
)
def create_objects(user, book, api):
    if user:
        if not api:
            create_mongo_users(user)
        else:
            for _ in range(user):
                post_fake_user()

    if book:
        if not api:
            create_mongo_books(book)
        else:
            for _ in range(book):
                post_fake_book()

    return None


@click.command()
@click.option("--celery", default=0, help="Creates users")
@click.option("--user_id", default="", help="Creates users")
def celery_test(celery, user_id):
    if not celery:
        return None
    with MongoClient("mongodb://root:root@localhost:27017") as conn:
        books_col = conn.get_database("library").books
        ids = books_col.find({}, {"_id": 1}).limit(celery)
        ids = [str(i["_id"]) for i in ids]
    p = requests.post(f"{ENDPOINT}checkout/{user_id}", data=json.dumps(ids))
    return p.status_code


if __name__ == "__main__":
    """
    Usage
    -----
    python setup_case.py create-objects --user 10
    python setup_case.py create-objects --book 100000

    python setup_case.py celery-test --celery 100000 --user_id 6150a1e3fab00a16518b5b2b
    """
    fake = Faker()
    fake.add_provider(isbn)
    fake.add_provider(person)
    fake.add_provider(internet)
    fake.add_provider(python)
    cli.add_command(create_objects)
    cli.add_command(celery_test)
    cli()
