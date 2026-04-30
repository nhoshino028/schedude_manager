from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.teams import Team

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    employee_code: str = Field(alias="employeeCode")
    name: str
    team: Team
    created_at: datetime = Field(alias="createdAt")