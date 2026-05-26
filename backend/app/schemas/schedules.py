from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, model_validator ,field_validator


class SimpleUser(BaseModel):
    id: int
    name: str

class SimpleStatus(BaseModel):
    id: int
    statusCode: str
    statusName: str

class Schedule(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    user: SimpleUser #{"id": 10, "name": "山田 太郎"}
    target_date: date = Field(alias="targetDate")
    status_type: SimpleStatus #{"id": 1, "statusCode": "OFFICE", "statusName": "出社"}
    start_time: time | None = Field(default=None, alias="from")
    end_time: time | None = Field(default=None, alias="to")
    comment: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


#エラーチェック用のモデル
class ScheduleQuery(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    target_date: date | None = Field(default=None, validation_alias="date")
    user_id: int | None = Field(default=None, alias="userId") 
    start_time: time | None = Field(default=None, validation_alias="from")
    end_time: time |None = Field(default=None, validation_alias="to")

    #未入力時に空文字を送らないようにする
    @field_validator("user_id", "target_date", "start_time", "end_time", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    #エラーチェック
    @model_validator(mode="after")
    def _validate_query(self)-> "ScheduleCreateRequest":
            if self.target_date is not None and (self.start_time is not None or self.end_time is not None):
                raise ValueError(
                "date cannot be used with from/to"
            )
            
   
            if (self.start_time is not None and self.end_time is None) or (self.end_time is not None and self.start_time is None):
                raise ValueError(
                "from and to must both be specified"
            )
            

            if (self.start_time is not None) and (self.end_time is not None):
                if (self.start_time) > (self.end_time):
                    raise ValueError("startTime must be <= endTime")
            return self
            

class ScheduleCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    target_date: date = Field(validation_alias="targetDate")
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
    
class ScheduleUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    target_date: date = Field(alias="targetDate")
    status_type_id: int = Field(alias="statusTypeId")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    comment: str | None = None

    @model_validator(mode="after")
    def _validate_time_order(self) -> "ScheduleUpdateRequest":
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
