import json
from pathlib import Path
from typing import Any

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File '{path.name}' not found in {path.parent}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ===== Loaders =====


def load_staff(
    data_dir: Path = DEFAULT_DATA_DIR, filename: str = "staff.json"
) -> list[dict[str, Any]]:
    return _load_json(data_dir / filename)


def load_shifts(
    data_dir: Path = DEFAULT_DATA_DIR, filename: str = "shifts.json"
) -> list[dict[str, Any]]:
    return _load_json(data_dir / filename)


def load_constraints(
    data_dir: Path = DEFAULT_DATA_DIR, filename: str = "constraints.json"
) -> dict[str, Any]:
    return _load_json(data_dir / filename)


# ===== Validators =====


def validate_staff(staff: list[dict[str, Any]]) -> None:
    for s in staff:
        assert "id" in s and "name" in s and "role" in s, (
            f"Missing required fields in staff: {s}"
        )


def validate_shifts(shifts: list[dict[str, Any]]) -> None:
    for shift in shifts:
        assert "id" in shift and "date" in shift and "required_roles" in shift, (
            f"Incomplete shift data: {shift}"
        )


def validate_constraints(constraints: dict[str, Any]) -> None:
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


def load_all_data(
    data_dir: Path = DEFAULT_DATA_DIR,
    staff_file: str = "staff.json",
    shifts_file: str = "shifts.json",
    constraints_file: str = "constraints.json",
):
    """Loads all data files, validates them, and returns them."""
    staff = load_staff(data_dir, staff_file)
    shifts = load_shifts(data_dir, shifts_file)
    constraints = load_constraints(data_dir, constraints_file)

    validate_staff(staff)
    validate_shifts(shifts)
    validate_constraints(constraints)

    return staff, shifts, constraints
