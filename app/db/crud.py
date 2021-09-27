from typing import Optional, Type, TypeVar

from bson import ObjectId
from models.pyobjectid import MongoModel
from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel

M = TypeVar("M", bound=MongoModel)


class CrudService(BaseModel):
    """
    Generic crud service

    Takes a collection to operate on and a model to operate with.
    """

    collection: AsyncIOMotorCollection
    model_cls: Type[MongoModel]

    class Config:
        arbitrary_types_allowed = True

    async def create_model(self, model: M) -> Optional[M]:
        """
        Try to create a model in models collection.
        If creation is failed return none instead
        """
        created = await self.collection.insert_one(model.dict(by_alias=True))
        if created.acknowledged and created.inserted_id == model.id:
            return model
        else:
            return None

    async def find_model_by_id(self, oid: ObjectId) -> Optional[MongoModel]:
        """
        Try to match `oid` with ObjectId in models collection,
        if found return the model as M
        else return none.
        """
        model = await self.collection.find_one({"_id": oid})
        if model:
            return self.model_cls(**model)
        return None

    async def update_model(self, oid: ObjectId, model_update: M) -> Optional[M]:
        """
        Try to replace the entire object with the new object
        If the operation is acknowledged by the db return the model
        else return none
        """
        ok = await self.collection.replace_one(
            {"_id": oid}, replacement=model_update.dict(by_alias=True)
        )
        if ok.acknowledged:
            return model_update
        else:
            return None

    async def remove_model(self, oid: ObjectId) -> bool:
        """
        Try to delete the model with given oid
        If the operation is acknowledged and a deletion operation has occured
        return the True
        else return False
        """
        ok = await self.collection.delete_one({"_id": oid})
        if ok.acknowledged and ok.deleted_count == 1:
            return True
        else:
            return False
