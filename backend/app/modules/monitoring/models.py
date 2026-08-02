import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base

class DeviceTypeEnum(str, enum.Enum):
    CAMERA_TRAP = "camera_trap"
    AUDIO_SENSOR = "audio_sensor"

class SurveyStatusEnum(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"

class MonitoringSite(Base):
    __tablename__ = "monitoring_sites"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, nullable=False)
    geom = Column(Geometry('POINT', srid=4326), nullable=False)
    habitat_type = Column(String, nullable=True)
    protected_area = Column(String, nullable=True)
    monitoring_device_type = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("monitoring_sites.id"), nullable=False)
    survey_date = Column(Date, nullable=False)
    status = Column(Enum(SurveyStatusEnum), nullable=False, default=SurveyStatusEnum.PLANNED)
    notes = Column(String, nullable=True)

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("monitoring_sites.id"), nullable=False)
    device_type = Column(Enum(DeviceTypeEnum), nullable=False)
    serial = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False, default="active")
    last_active = Column(DateTime(timezone=True), nullable=True)
