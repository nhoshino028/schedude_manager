from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.teams import Team

class ScheduleCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    target_date: date = Field(alias="targetDate")
    status_type_id: int = Field(alias="statusTypeId")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    comment: str | None = None

    @model_validator(mode="after")
    def _validate_time_order(self) -> "ScheduleCreateRequest":
        if self.start_time is not None and self.end_time is not None:
            if self.start_time > self.end_time:
                raise ValueError("startTime must be <= endTime")
        return self
    

class ScheduleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    user_id: int = Field(alias="userId")
    target_date: date = Field(alias="targetDate")
    status_type_id: int = Field(alias="statusTypeId")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    comment: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
