import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class FileTypeEnum(str, enum.Enum):
    IMAGE = "image"
    AUDIO = "audio"

class ObservationLog(Base):
    """
    Intentionally thin table for raw observational data.
    Downstream ML engines (bioacoustics, image analysis) will consume from here
    and define their own tables for species detection, bounding boxes, etc.
    """
    __tablename__ = "observation_log"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_type = Column(Enum(FileTypeEnum), nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processing_status = Column(String, nullable=False, default="pending")
