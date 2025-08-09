import json
from pathlib import Path
from typing import List, Dict, Any

# Define the base data directory
DATA_DIR = Path(__file__).parent.parent / "data"

# Helper to load JSON file
def _load_json(filename: str) -> Any:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File '{filename}' not found in {DATA_DIR}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===== Loaders =====

def load_staff() -> List[Dict[str, Any]]:
    """Loads all staff definitions."""
    return _load_json("staff.json")


def load_shifts() -> List[Dict[str, Any]]:
    """Loads all shift definitions."""
    return _load_json("shifts.json")


def load_constraints() -> Dict[str, Any]:
    """Loads global scheduling constraints."""
    return _load_json("constraints.json")


# ===== Optional Validators =====

def validate_staff(staff: List[Dict[str, Any]]) -> None:
    for s in staff:
        assert "id" in s and "name" in s and "role" in s, f"Missing required fields in staff: {s}"


def validate_shifts(shifts: List[Dict[str, Any]]) -> None:
    for shift in shifts:
        assert "id" in shift and "date" in shift and "required_roles" in shift, f"Incomplete shift data: {shift}"


def validate_constraints(constraints: Dict[str, Any]) -> None:
    required_fields = [
        "max_hours_per_week",
        "max_shifts_per_week",
        "shift_types",
        "shift_times"
    ]
    for field in required_fields:
        if field not in constraints:
            raise ValueError(f"Missing required constraint: {field}")


# ===== Wrapper to Load All =====

def load_all_data():
    """Convenience wrapper to load everything at once."""
    staff = load_staff()
    shifts = load_shifts()
    constraints = load_constraints()

    validate_staff(staff)
    validate_shifts(shifts)
    validate_constraints(constraints)

    return staff, shifts, constraints
