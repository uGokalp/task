from typing import Optional

from bson.errors import InvalidId
from bson.objectid import ObjectId
from db.crud import CrudService
from db.mongodb import get_user_service
from fastapi import Depends, Path, Response, exceptions, status
from fastapi.routing import APIRouter
from models.user import UpdateUserModel, UserModel

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: dict(description="User not found!")},
)


async def get_user_object_id(
    user_id: str = Path(..., example="615019d8ab766b8cc37cebf7")
) -> Optional[ObjectId]:
    """
    Cast string object id to ObjectId if possible
    Otherwise return None
    """
    try:
        return ObjectId(user_id)
    except (InvalidId, TypeError):
        return None


@router.get("/{user_id}")
async def find_user(
    user_id: ObjectId = Depends(get_user_object_id),
    user_service: CrudService = Depends(get_user_service),
):
    """
    Find a **user** by its objectid.
    If **user_id** is not a valid objectid or **user_id**
    does not belong to a user raise 404
    """
    user = await user_service.find_model_by_id(user_id)
    if user:
        return user
    else:
        raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post(
    "/", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserModel, user_service: CrudService = Depends(get_user_service)
):
    """
    Creates a new user in the database.
    """
    out = await user_service.create_model(user)
    return out


@router.patch("/{user_id}")
async def update_user(
    user: UpdateUserModel,
    user_id: ObjectId = Depends(get_user_object_id),
    user_service: CrudService = Depends(get_user_service),
):
    """
    Finds and updates **user** in the database
    Raises 404 if user is not found
    """
    user_found = await user_service.find_model_by_id(user_id)
    if user_found:
        update_data = user.dict(exclude_unset=True)
        updated_user = user_found.copy(update=update_data)
        user_in_db = await user_service.update_model(
            user_found.id, updated_user
        )
        return user_in_db
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: ObjectId = Depends(get_user_object_id),
    user_service: CrudService = Depends(get_user_service),
):
    """
    Finds and deletes **user** from the database
    Raises 404 if user is not found
    """
    deleted = await user_service.remove_model(user_id)
    if deleted:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
