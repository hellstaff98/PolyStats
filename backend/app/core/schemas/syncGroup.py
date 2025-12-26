from pydantic import BaseModel


class SyncGroupRequest(BaseModel):
    group_name: str