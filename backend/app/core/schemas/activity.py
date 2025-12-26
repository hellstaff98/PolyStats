from typing import Optional

from pydantic import BaseModel, ConfigDict


class ActivityBase(BaseModel):
    name: str          # Например: "Лабораторные", "РГР"
    max_progress: int  # Сколько всего нужно сдать (например, 8)

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    current_progress: Optional[int] = None
    max_progress: Optional[int] = None
    name: Optional[str] = None

class ActivityRead(ActivityBase):
    id: int
    current_progress: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)