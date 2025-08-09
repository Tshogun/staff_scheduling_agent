# Parser  Documentation

## Overview

This module handles the loading and validation of all JSON-based input data used in the scheduling system:

- `staff.json`
- `shifts.json`
- `constraints.json`

It ensures that the files are present, correctly structured, and contain all required fields before passing them to the solver.

---

## Table of Contents

- [Overview](#overview)
- [Module Responsibilities](#module-responsibilities)
- [Directory Setup](#directory-setup)
- [Functions](#functions)
  - [_load_json](#_load_json)
  - [load_staff](#load_staff)
  - [load_shifts](#load_shifts)
  - [load_constraints](#load_constraints)
  - [validate_staff](#validate_staff)
  - [validate_shifts](#validate_shifts)
  - [validate_constraints](#validate_constraints)
  - [load_all_data](#load_all_data)
- [Error Handling](#error-handling)
- [Usage Example](#usage-example)
- [File Structure Expectations](#file-structure-expectations)

---

## Module Responsibilities

✔ Load JSON input files  
✔ Validate file structure and schema  
✔ Raise meaningful errors on invalid or missing data  
✔ Provide a unified function to load all inputs together

---

## Directory Setup

```python
DATA_DIR = Path(__file__).parent.parent / "data"
```

- Points to the `data/` directory at the project root.
- Assumes the following structure:

```
project_root/<br>
├── data/<br>
│   ├── staff.json<br>
│   ├── shifts.json<br>
│   └── constraints.json<br>
└── scheduler/<br>
    └── parser.py<br>
```

---

## Functions

---

### 🧱 `_load_json(filename: str) → Any`

```python
def _load_json(filename: str) -> Any:
```

- **Purpose**: Generic helper to load any JSON file from the `data/` directory.
- **Raises**: `FileNotFoundError` if file doesn't exist.

```python
path = DATA_DIR / filename
if not path.exists():
    raise FileNotFoundError(...)
```

- Opens and parses JSON safely using UTF-8 encoding.

---

### 👥 `load_staff() → List[Dict[str, Any]]`

```python
def load_staff() -> List[Dict[str, Any]]:
```

- Loads the `staff.json` file.
- Each entry should contain:
  - `"id"`: Unique staff ID
  - `"name"`: Staff member's name
  - `"role"`: Assigned job role
  - (Optional: availability, preferences, etc.)

---

### 🕒 `load_shifts() → List[Dict[str, Any]]`

```python
def load_shifts() -> List[Dict[str, Any]]:
```

- Loads the `shifts.json` file.
- Each shift must contain:
  - `"id"`: Unique shift ID
  - `"date"`: Shift date
  - `"required_roles"`: List of required roles (with counts and skills)

---

### ⚙️ `load_constraints() → Dict[str, Any]`

```python
def load_constraints() -> Dict[str, Any]:
```

- Loads the `constraints.json` file.
- Contains both **shift configuration** and **constraints**, such as:
  - `shift_config`: Types, times, duration
  - `hard_constraints`: Rules like max hours per week
  - `soft_constraints`: Weights for optimization

---

### ✅ `validate_staff(staff: List[Dict[str, Any]])`

```python
def validate_staff(staff: List[Dict[str, Any]]) -> None:
```

- Verifies that each staff entry includes the required fields:
  - `"id"`, `"name"`, and `"role"`

```python
assert "id" in s and "name" in s and "role" in s
```

- Raises `AssertionError` if any are missing.

---

### ✅ `validate_shifts(shifts: List[Dict[str, Any]])`

```python
def validate_shifts(shifts: List[Dict[str, Any]]) -> None:
```

- Ensures each shift has:
  - `"id"`, `"date"`, and `"required_roles"`

```python
assert "id" in shift and "date" in shift and "required_roles" in shift
```

- Raises `AssertionError` if data is incomplete.

---

### ✅ `validate_constraints(constraints: Dict[str, Any])`

```python
def validate_constraints(constraints: Dict[str, Any]) -> None:
```

- Checks that `constraints.json` has all required sections and keys.

**Required Sections:**
- `shift_config`  
- `hard_constraints`

**Required Keys in `shift_config`:**
- `"shift_types"`  
- `"shift_times"`

**Required Keys in `hard_constraints`:**
- `"max_hours_per_week"`  
- `"max_shifts_per_week"`

Raises `ValueError` if any required section or key is missing.

---

### 🧩 `load_all_data() → Tuple[...]`

```python
def load_all_data():
```

- Convenience wrapper to:
  - Load all input files
  - Run all validation checks
- Returns:
  - `staff`, `shifts`, `constraints` as Python objects (lists/dicts)

```python
return staff, shifts, constraints
```

---

## Error Handling

| Error Type        | Trigger                                     |
|------------------|---------------------------------------------|
| `FileNotFoundError` | If any JSON file is missing in `/data/`     |
| `AssertionError`  | If required fields are missing from data    |
| `ValueError`      | If config structure is invalid or incomplete |

All validation errors are designed to fail fast to prevent corrupted input from entering the solver.

---

## Usage Example

```python
from src.data_loader import load_all_data

staff, shifts, constraints = load_all_data()
```

- You now have ready-to-use input data for the solver.

---

## File Structure Expectations

### staff.json (example)
```json
[
  {
    "id": "SHN00001",
    "name": "Alice Smith",
    "role": "nurse",
    "skills": ["icu", "pediatrics"],
    "max_hours_per_week": 40,
    "preferred_shifts": ["morning"],
    "unavailable_days": ["2025-08-10", "2025-08-13"],
    "unavailable_shifts": ["2025-08-12_night"],
    "vacation_dates": ["2025-08-15", "2025-08-16"],
    "max_consecutive_days": 5,
    "min_rest_hours": 12,
    "night_shift_limit_per_week": 2,
    "last_five_shifts": [
      {
        "date": "2025-08-11",
        "shift_type": "morning",
        "duration_hours": 8
      },
      {
        "date": "2025-08-09",
        "shift_type": "evening",
        "duration_hours": 8
      }
    ],
    "seniority": 3
  }
]
```

### shifts.json (example)
```json
[
  {
    "id": "20250814E",
    "date": "2025-08-14",
    "day_of_week": "Tuesday",
    "shift_type": "Evening",
    "start_time": "15:00",
    "end_time": "23:00",
    "duration_hours": 8,
    "required_roles": [
      {
        "role": "nurse",
        "count": 6,
        "skills_required": []
      },
      {
        "role": "doctor",
        "count": 2,
        "skills_required": ["surgery", "icu"]
      }
    ],
    "is_holiday": false,
    "priority": "normal",
    "department": "ICU",
    "location": "Wing A",
    "notes": "ICU must be fully staffed"
  }
]
```

### constraints.json (example)
```json
{
  "shift_config": {
    "shift_types": ["morning", "evening", "night"],
    "shift_times": {
      "morning": "08:00-16:00",
      "evening": "16:00-00:00",
      "night": "00:00-08:00"
    },
    "default_shift_duration_hours": 8
  },
  "hard_constraints": {
    "max_hours_per_week": 40,
    "max_shifts_per_week": 5
  },
  "soft_constraints": {
    "weights": {
      "understaffed_shift_penalty": 10,
      "skill_mismatch_penalty": 5,
      "preferred_shift_match": 2,
      "overtime_penalty": 4,
      "underscheduling_penalty": 3
    }
  }
}
```

---

> 📁 This module is critical to ensure the **solver receives clean, well-structured input**. It should be maintained alongside any changes to the data format or validation rules.

