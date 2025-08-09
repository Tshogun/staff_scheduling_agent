import json
from staff_schema import Staff
from shift_schema import Shift
from pydantic import ValidationError

def load_staff(filepath: str) -> Staff:
    with open(filepath, "r") as f:
        raw_data = json.load(f)
    return Staff(**raw_data)

def load_shift(filepath: str) -> Shift:
    with open(filepath, "r") as f:
        raw_data = json.load(f)
    return Shift(**raw_data)

def main():
    try:
        staff = load_staff("staff_data.json")
        print("✅ Staff JSON successfully validated and parsed.")
        print(f"Name: {staff.name}")
        print(f"Assigned shifts this week: {staff.metadata.assigned_shifts_this_week}")
        print(f"Leave requests: {[r.date for r in staff.leave_requests]}")

        shift = load_shift("shift_data.json")
        print("\n✅ Shift JSON successfully validated and parsed.")
        print(f"Shift ID: {shift.shift_id}")
        print(f"Date: {shift.date}")
        print(f"Shift Type: {shift.shift_type}")
        print(f"Required Role: {shift.required_role}")
        print(f"Assigned Staff: {shift.assigned_staff}")

    except ValidationError as e:
        print("❌ Validation error:")
        print(e)

if __name__ == "__main__":
    main()
