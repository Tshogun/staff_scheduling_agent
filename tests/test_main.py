from scheduler import solver


def test_generate_schedule_success():
    result = solver.generate_schedule()
    assert result is not None
