from typing import List

from pydantic import BaseModel, ConfigDict

from core.schemas.activity import ActivityRead


class SubjectBase(BaseModel):
    name: str

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int
    activities: List[ActivityRead] = []

    model_config = ConfigDict(from_attributes=True)