from pydantic import BaseModel, ConfigDict, Field

class WorkStatusType(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    status_code: str = Field(alias="statusCode")
    status_code: str = Field(alias="statusName")