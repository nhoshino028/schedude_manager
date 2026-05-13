from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MonthlyReportUser(BaseModel):
    id: int
    name: str

class MonthlyReport(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    user: MonthlyReportUser
    year_month: str = Field(alias="yearMonth")
    office_days: int = Field(alias="officeDays")
    remote_days: int = Field(alias="remoteDays")
    paid_leave_days: int = Field(alias="paidLeaveDays")
    am_leave_count: int = Field(alias="amLeaveCount")
    pm_leave_count: int = Field(alias="pmLeaveCount")
    absence_days: int = Field(alias="absenceDays")
    updated_at: datetime = Field(alias="updatedAt")