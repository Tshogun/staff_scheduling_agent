## Solver Documentation

### Function: `generate_schedule()`

This function is the core of the scheduling system. It loads data, defines constraints and decision variables, sets an optimization objective, solves the model, and outputs the results.

---

### 🔹 Imports & Setup

```python
import logging
from ortools.sat.python import cp_model
from scheduler.parser import load_all_data
from datetime import datetime
import json
from pathlib import Path
```

- `cp_model`: Google OR-Tools constraint programming model.
- `load_all_data`: Custom parser function to load all required JSON inputs.
- `logging`: Used for structured logs and debugging info.
- `datetime`: Used to time the schedule generation.
- `json`, `Path`: For writing results to a file.

---

### 🔹 Logging Configuration

```python
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)
```

- Logs messages with timestamps and log levels (`INFO`, `WARNING`, `ERROR`).
- Used throughout the script for debugging and transparency.

---

### 1. Load Data

```python
staff_list, shift_list, constraints_data = load_all_data()
```

- Loads:
  - **staff_list**: List of all employees with roles, skills, preferences, and availability.
  - **shift_list**: All available shifts with role/skill requirements and dates.
  - **constraints_data**: Contains both hard and soft constraint configurations.

```python
hard_constraints = constraints_data["hard_constraints"]
soft_constraints = constraints_data["soft_constraints"]["weights"]
shift_duration = constraints_data["shift_config"].get("default_shift_duration_hours", 8)
```

- Extracts specific constraint parameters from the config file.
- Uses 8 hours as default shift duration if none specified.

---

### 2. Initialize the Solver

```python
model = cp_model.CpModel()
solver = cp_model.CpSolver()
```

- `model`: Container for all variables and constraints.
- `solver`: Runs the optimization algorithm.

---

### 3. Prepare IDs and Mappings

```python
staff_ids = [s["id"] for s in staff_list]
shift_ids = [s["id"] for s in shift_list]
shift_by_id = {s["id"]: s for s in shift_list}
```

- Extracts IDs for fast lookup.
- `shift_by_id` dictionary helps access full shift data using shift ID.

---

### 4. Create Decision Variables

```python
shift_assignments = {
    (s_id, sh_id): model.NewBoolVar(f"{s_id}_works_{sh_id}")
    for s_id in staff_ids for sh_id in shift_ids
}
```

- Creates a boolean variable for every possible assignment (staff × shift).
- A value of `1` means the staff is assigned to that shift.

---

### 5. Objective Function Terms (Soft Constraints)

```python
objective_terms = []
```

- List of expressions that will be combined to create the objective function.
- Each term represents a penalty (or bonus) based on constraint satisfaction.

---

### 6. Apply Hard Constraints

#### a. Required Roles and Skills Per Shift

```python
for shift in shift_list:
    ...
    for role_req in shift["required_roles"]:
        ...
        eligible_staff = [
            s for s in staff_list
            if s["role"] == role
            and shift_date not in s.get("unavailable_days", [])
            and shift_id not in s.get("unavailable_shifts", [])
        ]
```

- Filters eligible staff by role and availability.
- Assigns only eligible staff to shifts.

#### b. Minimum Required Staff per Role

```python
assigned_sum = model.NewIntVar(0, len(eligible_ids), f"{shift_id}_{role}_assigned")
model.Add(assigned_sum == sum(assigned))
```

- Ensures the required number of people are assigned per role per shift.

#### c. Penalize Understaffing (Soft Constraint)

```python
shortage = model.NewIntVar(0, required_count, f"{shift_id}_{role}_shortage")
model.Add(shortage == required_count - assigned_sum)
objective_terms.append(shortage * soft_constraints["understaffed_shift_penalty"])
```

- Calculates how many required roles are left unfilled.
- Adds penalty if not enough people are assigned.

#### d. Skill Coverage

```python
for skill in required_skills:
    ...
    model.Add(sum(staff_with_skill) >= 1)
```

- Ensures at least one assigned staff member has each required skill.
- If not, adds a penalty:

```python
penalty = model.NewIntVar(0, 1, ...)
model.Add(penalty == 1)
objective_terms.append(penalty * soft_constraints["skill_mismatch_penalty"])
```

---

### 7. One Shift Per Day Per Staff

```python
for s in staff_list:
    ...
    model.Add(sum(shift_assignments[(s_id, sh["id"])] for sh in shifts) <= 1)
```

- Prevents a staff member from working multiple shifts on the same day.

---

### 8. Enforce Staff Availability

```python
for s in staff_list:
    ...
    if sh["date"] in s.get("unavailable_days", []) or sh["id"] in s.get("unavailable_shifts", []):
        model.Add(shift_assignments[(s_id, sh["id"])] == 0)
```

- Staff cannot be assigned to shifts they’ve marked as unavailable.

---

### 9. Add Soft Constraints to Objective

#### a. Preferred Shift Bonus

```python
if sh["shift_type"] in preferred_shifts:
    objective_terms.append(-soft_constraints["preferred_shift_match"] * shift_assignments[(s_id, sh["id"])])
```

- Gives negative (beneficial) score to assignments that match preferences.

#### b. Overtime Penalty

```python
overtime = model.NewIntVar(0, 1000, ...)
model.Add(total_hours - max_hours <= overtime)
model.AddMaxEquality(overtime, [total_hours - max_hours, 0])
```

- Penalizes if staff is scheduled beyond `max_hours_per_week`.

#### c. Underscheduling Penalty

```python
underscheduled = model.NewIntVar(0, 1000, ...)
model.Add(min_hours - total_hours <= underscheduled)
model.AddMaxEquality(underscheduled, [min_hours - total_hours, 0])
```

- Penalizes if staff is scheduled less than `min_hours_per_week`.

---

### 10. Set Objective and Solve

```python
model.Minimize(sum(objective_terms))
solver.parameters.max_time_in_seconds = 10.0
status = solver.Solve(model)
```

- Minimizes the total penalty (objective function).
- Solver runs for up to 10 seconds.

---

### 11. Extract and Save Results

```python
if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    ...
    json.dump(result, f, indent=2)
```

- Collects all assignments where `BooleanValue(...) == True`.
- Outputs them to `output/assignments.json`.

---

### 12. Error Handling and Execution Timing

```python
try:
    generate_schedule()
except Exception as e:
    log.exception(...)
finally:
    log.info(...)
```

- Captures any errors during execution.
- Logs total duration of the scheduling process.

---

## Summary of Key Constraints

| Type               | Constraint                                        | Enforced As        |
|--------------------|--------------------------------------------------|---------------------|
| Hard               | One shift per day per staff                      | ✅ `model.Add(...)` |
| Hard               | Only assign if available                         | ✅ `model.Add(...)` |
| Hard               | Required number of staff per shift               | ✅ + penalty if short |
| Soft               | Underscheduling                                   | 🟡 penalty          |
| Soft               | Overtime                                          | 🟡 penalty          |
| Soft               | Skill mismatch                                    | 🟡 penalty          |
| Soft               | Preferred shift bonus                             | 🟢 reward (negative penalty) |

---

