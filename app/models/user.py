from bson import ObjectId

from .pyobjectid import AllOptional, MongoModel


class UserModel(MongoModel):
    """
    Base model used by users.
    """

    email: str
    username: str
    password: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "email@email.email",
                "username": "Umur",
                "password": "password",
            }
        }


class UpdateUserModel(UserModel, metaclass=AllOptional):
    """
    All optional fields for the UserModel
    """

    pass
