from pathlib import Path

from scheduler import parser, solver


def test_basic_schedule_generation():
    data_dir = Path(__file__).parent / "test_data"

    # Use specific test files
    staff, shifts, constraints = parser.load_all_data(
        data_dir=data_dir,
        staff_file="staff_basic.json",
        shifts_file="shifts_basic.json",
        constraints_file="constraints_basic.json",
    )

    # Monkeypatch the loader function inside solver to return this data directly
    def mock_loader():
        return staff, shifts, constraints

    solver.load_all_data = mock_loader

    result = solver.generate_schedule()

    assert result is not None
    assert isinstance(result, list)
    assert all("shift_id" in r and "staff_ids" in r for r in result)
