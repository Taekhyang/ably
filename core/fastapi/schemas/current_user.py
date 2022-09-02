from pydantic import BaseModel, Field
from typing import Optional


class CurrentUser(BaseModel):
    id: Optional[str] = Field(None, description="User ID")

    class Config:
        validate_assignment = True
