from pydantic import BaseModel, ConfigDict, Field

class Team(BaseModel):

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    team_code: str = Field(alias="teamCode")
    name: str