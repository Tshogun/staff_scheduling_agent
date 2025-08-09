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
# ===== Validators =====
    """Loads global scheduling constraints."""
    return _load_json("constraints.json")

def validate_staff(staff: List[Dict[str, Any]]) -> None:
    for s in staff:
        assert "id" in s and "name" in s and "role" in s, f"Missing required fields in staff: {s}"


def validate_shifts(shifts: List[Dict[str, Any]]) -> None:
    for shift in shifts:
        assert "id" in shift and "date" in shift and "required_roles" in shift, f"Incomplete shift data: {shift}"


def validate_constraints(constraints: Dict[str, Any]) -> None:
   required_shift_keys = ["shift_types", "shift_times"]
    required_hard_keys = ["max_hours_per_week", "max_shifts_per_week"]

    if "shift_config" not in constraints:
        raise ValueError("Missing 'shift_config' section in constraints")
    if "hard_constraints" not in constraints:
        raise ValueError("Missing 'hard_constraints' section in constraints")

    for key in required_shift_keys:
        if key not in constraints["shift_config"]:
            raise ValueError(f"Missing required shift config: {key}")
    for key in required_hard_keys:
        if key not in constraints["hard_constraints"]:
            raise ValueError(f"Missing required hard constraint: {key}")


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
