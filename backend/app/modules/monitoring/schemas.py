from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.modules.monitoring.models import DeviceTypeEnum, SurveyStatusEnum

# --- Monitoring Site ---
class MonitoringSiteBase(BaseModel):
    location_name: str
    habitat_type: Optional[str] = None
    protected_area: Optional[str] = None
    monitoring_device_type: Optional[str] = None

class MonitoringSiteCreate(MonitoringSiteBase):
    latitude: float
    longitude: float

class MonitoringSiteResponse(MonitoringSiteBase):
    id: int
    created_by: int
    created_at: datetime
    latitude: float
    longitude: float
    
    model_config = ConfigDict(from_attributes=True)

# --- Survey ---
class SurveyBase(BaseModel):
    site_id: int
    survey_date: date
    notes: Optional[str] = None

class SurveyCreate(SurveyBase):
    pass

class SurveyResponse(SurveyBase):
    id: int
    status: SurveyStatusEnum

    model_config = ConfigDict(from_attributes=True)

# --- Device ---
class DeviceBase(BaseModel):
    site_id: int
    device_type: DeviceTypeEnum
    serial: str
    status: str = "active"

class DeviceCreate(DeviceBase):
    pass

class DeviceResponse(DeviceBase):
    id: int
    last_active: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
