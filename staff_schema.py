from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date

ShiftType = Literal["morning", "evening", "night"]
LeaveStatus = Literal["pending", "approved", "denied"]

class LeaveRequest(BaseModel):
    date: date
    reason: str
    status: LeaveStatus = "pending"

class PastShift(BaseModel):
    shift_type: ShiftType
    location: str

class InternalMetadata(BaseModel):
    assigned_shifts_this_week: int = 0
    consecutive_shifts: int = 0
    last_assigned_day: Optional[date] = None
    last_assigned_shift_type: Optional[ShiftType] = None
    consecutive_night_shifts: int = 0

    total_shifts_assigned_this_month: int = 0
    total_night_shifts_this_month: int = 0
    avg_shifts_per_week: float = 0.0

    days_since_last_day_off: int = 0
    had_rest_day_yesterday: bool = False
    recent_shift_streak: List[ShiftType] = Field(default_factory=list)

    declined_shifts_recently: int = 0
    preferred_shift_fill_rate: float = 0.0
    last_leave_type: Optional[str] = None

class Staff(BaseModel):
    staff_id: str
    name: str
    role: str
    specialty: Optional[str] = None
    max_shifts_per_week: int = 5

    available_days: List[str] = Field(default_factory=list)
    cannot_do_shift_types: List[ShiftType] = Field(default_factory=list)
    preferred_shifts: List[ShiftType] = Field(default_factory=list)

    remaining_leaves: int = 0
    last_leave_on: Optional[date] = None
    leave_requests: List[LeaveRequest] = Field(default_factory=list)

    past_shifts: List[PastShift] = Field(default_factory=list)
    metadata: InternalMetadata = Field(default_factory=InternalMetadata)

