from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from core.models import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)

    user = relationship("User", back_populates="subjects")
    activities = relationship("Activity", back_populates="subject", cascade="all, delete-orphan")