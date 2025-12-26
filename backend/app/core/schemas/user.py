from typing import Optional

from fastapi_users import schemas
from pydantic import BaseModel

from core.types.user_id import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    group_name: Optional[str]
    group_id: Optional[str]


class UserCreate(schemas.BaseUserCreate):
    group_name: str


class UserUpdate(schemas.BaseUserUpdate):
    group_name: Optional[str] = None
    group_id: Optional[str] = None


class UserRegisteredNotification(BaseModel):
    user: UserRead
    ts: int