from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from core.models import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    name = Column(String, nullable=False)
    current_progress = Column(Integer, default=0)
    max_progress = Column(Integer, default=1)

    subject = relationship("Subject", back_populates="activities")