from pathlib import Path

from scheduler import parser, solver


def test_night_shift_soft_constraint():
    data_dir = Path(__file__).parent / "test_data"

    staff, shifts, constraints = parser.load_all_data(
        data_dir=data_dir,
        staff_file="staff_basic.json",  # or staff_night_limited.json if exists
        shifts_file="shifts_night_only.json",
        constraints_file="constraints_soft_night_penalty.json",
    )

    solver.load_all_data = lambda: (staff, shifts, constraints)

    result = solver.generate_schedule()
    assert result is not None

    # Check if staff aren not over-assigned to night shifts beyond soft limits
    night_shift_count = {staff_member["id"]: 0 for staff_member in staff}

    for entry in result:
        shift = next(s for s in shifts if s["id"] == entry["shift_id"])
        if shift["shift_type"] == "night":
            for sid in entry["staff_ids"]:
                night_shift_count[sid] += 1

    for _sid, count in night_shift_count.items():
        assert (
            count
            <= constraints["hard_constraints"].get("night_shift_limit_per_week", 2) + 1
        )  # +1 to allow for soft constraint flexibility


def test_unavailable_staff_never_scheduled():
    data_dir = Path(__file__).parent / "test_data"

    staff, shifts, constraints = parser.load_all_data(
        data_dir=data_dir,
        staff_file="staff_unavailable.json",
        shifts_file="shifts_basic.json",
        constraints_file="constraints_basic.json",
    )

    solver.load_all_data = lambda: (staff, shifts, constraints)
    result = solver.generate_schedule()
    assert result is not None

    # Build shift lookup by ID
    shift_lookup = {s["id"]: s for s in shifts}

    for assignment in result:
        shift_id = assignment["shift_id"]
        shift = shift_lookup[shift_id]
        shift_date = shift["date"]

        for sid in assignment["staff_ids"]:
            staff_member = next(s for s in staff if s["id"] == sid)
            unavailable_days = staff_member.get("unavailable_days", [])
            unavailable_shifts = staff_member.get("unavailable_shifts", [])

            assert shift_date not in unavailable_days, (
                f"Staff {sid} was scheduled on unavailable day {shift_date} for shift {shift_id}"
            )
            assert shift_id not in unavailable_shifts, (
                f"Staff {sid} was scheduled for unavailable shift {shift_id}"
            )


def test_underscheduling_penalty_effect():
    data_dir = Path(__file__).parent / "test_data"

    staff, shifts, constraints = parser.load_all_data(
        data_dir=data_dir,
        staff_file="staff_basic.json",
        shifts_file="shifts_basic.json",
        constraints_file="constraints_basic.json",
    )

    for s in staff:
        s["min_hours_per_week"] = 40  # Force high expected hours

    solver.load_all_data = lambda: (staff, shifts, constraints)
    result = solver.generate_schedule()
    assert result is not None

    # Expect that schedule still returns, even if some underscheduling occurs
    assert isinstance(result, list)
