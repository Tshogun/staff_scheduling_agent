## Solver Class Documentation

## Overview
This module (`generate_schedule`) builds and solves a **medical staff scheduling problem** using **Google OR-Tools CP-SAT Solver**.  

It:
- Loads **staff**, **shifts**, and **constraints** from JSON files using `load_all_data()`.
- Defines **decision variables** for staff–shift assignments.
- Applies **hard constraints** (must-follow rules) and **soft constraints** (preferences with penalties/bonuses).
- Optimizes the schedule to **minimize penalties** while meeting required staffing levels.
- Writes the assignment results to `output/assignments.json`.

---

## Key Dependencies
- `logging` — logs progress and debug information.
- `ortools.sat.python.cp_model` — constraint programming solver (CP-SAT).
- `scheduler.parser.load_all_data` — data loader/validator for staff, shifts, and constraints.
- `datetime` — timestamps for execution.
- `json` & `pathlib.Path` — read/write output files.

---

## Workflow Overview

1. **Load Input Data**
   ```
   staff_list, shift_list, constraints_data = load_all_data()
   ```
   - Reads `staff.json`, `shifts.json`, and `constraints.json` from `/data`.
   - Logs number of staff and shifts.

2. **Extract Parameters**
   - `hard_constraints` → fixed operational rules (e.g., max hours per week).
   - `soft_constraints["weights"]` → penalties/bonuses for soft rule violations.
   - `shift_duration` → default hours per shift (fallback: 8).

3. **Initialize Model**
   ```
   model = cp_model.CpModel()
   solver = cp_model.CpSolver()
   ```

4. **Decision Variables**
   - Boolean variable `(staff_id, shift_id)` → 1 if staff works shift, else 0.

5. **Hard Constraints**
   - **Shift coverage**: Aim to meet `required_count` per role; shortages tracked as penalties.
   - **Required skills**: At least one staff member with each required skill (otherwise soft penalty).
   - **One shift per day per staff**.
   - **Staff unavailability**: Block assignment if unavailable.

6. **Soft Constraints**
   - **Preferred shift match** → bonus if assigned.
   - **Overtime** → penalty if hours exceed max.
   - **Underscheduling** → penalty if hours below min.

7. **Objective Function**
   ```
   model.Minimize(sum(objective_terms))
   ```
   - Combination of penalties and bonuses.

8. **Solve & Output**
   - Solver runs with a 10-second time limit.
   - Logs all assignments found.
   - Outputs `assignments.json` in `/output`.

---

## Example Execution
Run directly:
```
python scheduler.py
```
Example log output:
```
2025-08-09 21:15:00 [INFO] Loading input data...
2025-08-09 21:15:01 [INFO] Loaded 15 staff members
2025-08-09 21:15:01 [INFO] Loaded 42 shifts
2025-08-09 21:15:02 [INFO] Schedule generated successfully.
```

---

## Output Format
`output/assignments.json`:
```
[
  {
    "shift_id": "shift_1",
    "staff_ids": ["staff_4", "staff_7"]
  },
  {
    "shift_id": "shift_2",
    "staff_ids": ["staff_1"]
  }
]
```

---

## Error Handling
| Error Type               | Cause                                                        |
|--------------------------|--------------------------------------------------------------|
| `FileNotFoundError`      | Missing data file (`staff.json`, `shifts.json`, etc.)         |
| `ValueError` / Assertion | Invalid/missing required fields in input data                 |
| `WARNING` log            | No eligible staff for a shift or missing skill requirements   |
| `log.warning`            | No feasible solution found during solve                      |

---

## Best Practices
- Keep constraints realistic to avoid infeasible schedules.
- Adjust penalty weights (`soft_constraints["weights"]`) to prioritize trade-offs.
- Test with small datasets before scaling up.
- Review solver status (`OPTIMAL` vs `FEASIBLE`) to understand result quality.
- Store historical `assignments.json` for audit/tracking purposes.

---

## Extensibility Ideas
- Add **overstaffing penalties**.
- Consider **maximum consecutive days** constraint.
- Support **shift rotation fairness**.
- Export schedules in multiple formats (CSV, Excel).
- Integrate with a **web dashboard** for hospital management.

---
```

***
