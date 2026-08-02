from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.modules.observations.models import FileTypeEnum

class ObservationLogResponse(BaseModel):
    id: int
    survey_id: int
    uploaded_by: int
    file_type: FileTypeEnum
    uploaded_at: datetime
    processing_status: str

    model_config = ConfigDict(from_attributes=True)
