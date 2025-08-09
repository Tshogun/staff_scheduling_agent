from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date

ShiftType = Literal["morning", "evening", "night"]

class Shift(BaseModel):
    shift_id: str
    date: date
    shift_type: ShiftType
    location: str
    required_role: str
    required_specialty: Optional[str] = None
    max_staff: int = 1
    assigned_staff: List[str] = Field(default_factory=list)
