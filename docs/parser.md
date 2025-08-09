# Parser file Documentation

## Overview
This module handles:
- **Loading** `staff.json`, `shifts.json`, and `constraints.json` from the `data/` directory.  
- **Validating** the structure and required fields of each dataset.  
- **Returning** all three data sets as Python objects for use in the scheduling system.

---

## Directory Structure

Expected directory layout:<br>

project_root/<br>
│<br>
├── data/<br>
│ ├── staff.json<br>
│ ├── shifts.json<br>
│ └── constraints.json<br>
│<br>
├── scheduler/<br>
│ └── parser.py # this script<br>

---

## Constants
```
DATA_DIR = Path(__file__).parent.parent / "data"
```
**Purpose:** Points to the `/data` directory at the root of the project.  
**Used to:** Locate the JSON files (`staff.json`, `shifts.json`, `constraints.json`).

---

## Functions

### 1. Private Helper
```
def _load_json(filename: str) -> Any:
```
**Purpose:** Loads a given JSON file from the `data/` directory.  
**Raises:**  
- `FileNotFoundError` → If the file does not exist.  

✅ **Example**:
```
staff_data = _load_json("staff.json")
```

---

### 2. Loaders  
Wrapper functions to load specific datasets:

```
def load_staff() -> List[Dict[str, Any]]:
```
- **Returns:** List of staff records from `staff.json`.

```
def load_shifts() -> List[Dict[str, Any]]:
```
- **Returns:** List of shift records from `shifts.json`.

```
def load_constraints() -> Dict[str, Any]:
```
- **Returns:** Dictionary containing scheduling constraints from `constraints.json`.

---

### 3. Validators  
Check that each dataset contains the required fields.

```
def validate_staff(staff: List[Dict[str, Any]]) -> None:
```
- Checks each staff entry for required keys: `"id"`, `"name"`, `"role"`.  
- **Raises:** `AssertionError` if keys are missing.

```
def validate_shifts(shifts: List[Dict[str, Any]]) -> None:
```
- Checks each shift for keys: `"id"`, `"date"`, `"required_roles"`.  
- **Raises:** `AssertionError` if incomplete.

```
def validate_constraints(constraints: Dict[str, Any]) -> None:
```
- Ensures:
  - `shift_config` exists with `"shift_types"`, `"shift_times"`.
  - `hard_constraints` exists with `"max_hours_per_week"`, `"max_shifts_per_week"`.
- **Raises:** `ValueError` if any are missing.

---

### 4. Wrapper to Load All
```
def load_all_data():
```
- Loads **staff**, **shifts**, and **constraints**.  
- Runs the validators for each.  
- **Returns:** `(staff, shifts, constraints)` tuple.

✅ **Example Usage**:

staff, shifts, constraints = load_all_data()


---

## Error Handling
| Error Type         | Trigger Condition                                   |
|--------------------|-----------------------------------------------------|
| `FileNotFoundError`| JSON file not found in `/data/`.                     |
| `AssertionError`   | Missing required fields in staff or shifts.          |
| `ValueError`       | Missing sections or keys in constraints file.        |

---

## Best Practices
- Keep `staff.json`, `shifts.json`, and `constraints.json` **up to date** with the correct structure.
- Run `load_all_data()` early in your program to ensure all data is valid before scheduling.
- If you add new required fields, **update the validators**.

---