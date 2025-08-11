from pathlib import Path

from scheduler.parser import (
    load_all_data,
    load_constraints,
    load_shifts,
    load_staff,
    validate_constraints,
    validate_shifts,
    validate_staff,
)

# Define test data path
TEST_DATA_DIR = Path(__file__).parent / "test_data"


def test_load_staff_basic():
    staff = load_staff(data_dir=TEST_DATA_DIR, filename="staff_basic.json")
    assert isinstance(staff, list)
    assert all("id" in s and "name" in s and "role" in s for s in staff)


def test_load_shifts_basic():
    shifts = load_shifts(data_dir=TEST_DATA_DIR, filename="shifts_basic.json")
    assert isinstance(shifts, list)
    assert all("id" in s and "date" in s and "required_roles" in s for s in shifts)


def test_load_constraints_basic():
    constraints = load_constraints(
        data_dir=TEST_DATA_DIR, filename="constraints_basic.json"
    )
    assert isinstance(constraints, dict)
    assert "hard_constraints" in constraints
    assert "shift_config" in constraints


def test_basic_validation():
    staff = load_staff(TEST_DATA_DIR, "staff_basic.json")
    shifts = load_shifts(TEST_DATA_DIR, "shifts_basic.json")
    constraints = load_constraints(TEST_DATA_DIR, "constraints_basic.json")

    validate_staff(staff)
    validate_shifts(shifts)
    validate_constraints(constraints)


def test_load_all_data_with_named_files():
    staff, shifts, constraints = load_all_data(
        data_dir=TEST_DATA_DIR,
        staff_file="staff_basic.json",
        shifts_file="shifts_basic.json",
        constraints_file="constraints_basic.json",
    )

    assert isinstance(staff, list)
    assert isinstance(shifts, list)
    assert isinstance(constraints, dict)
    assert len(staff) > 0
    assert len(shifts) > 0
