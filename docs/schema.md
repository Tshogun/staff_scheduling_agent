# Data Schema Documentation

This document defines the structure and expected fields for the input JSON files:

- [`staff.json`](#staffjson-schema)
- [`shifts.json`](#shiftsjson-schema)

All fields are **case-sensitive**, and any missing required fields may cause validation or runtime errors.

---

## `staff.json` Schema

Each object in `staff.json` represents a **staff member**.

### Structure

```json
[
  {
    "id": "string",                    // Unique staff ID
    "name": "string",                 // Full name
    "role": "string",                 // Job role (e.g. nurse, doctor)
    "skills": ["string", ...],        // List of relevant skills
    "max_hours_per_week": number,     // Weekly work limit in hours
    "preferred_shifts": ["string"],   // List of preferred shift types (e.g. "morning")
    "unavailable_days": ["YYYY-MM-DD"],        // Days unavailable
    "unavailable_shifts": ["string"],          // Specific shifts unavailable (e.g. "2025-08-12_night")
    "vacation_dates": ["YYYY-MM-DD"],          // Approved vacation days
    "max_consecutive_days": number,   // Max workdays without a break
    "min_rest_hours": number,         // Required rest between shifts
    "night_shift_limit_per_week": number, // Max night shifts allowed per week
    "last_five_shifts": [             // Recent shifts (optional but useful)
      {
        "date": "YYYY-MM-DD",
        "shift_type": "string",
        "duration_hours": number
      }
    ],
    "seniority": number               // Integer ranking of experience or priority
  }
]
```

### Required Fields

| Field                | Type     | Required | Description                               |
|---------------------|----------|----------|-------------------------------------------|
| `id`                | string   | ✅       | Unique staff identifier                   |
| `name`              | string   | ✅       | Staff full name                           |
| `role`              | string   | ✅       | Job role (e.g. nurse, doctor)             |
| `skills`            | array    | ✅       | List of string skills (can be empty)      |
| `max_hours_per_week`| number   | ✅       | Maximum hours this staff can work weekly  |

### Optional Fields (Recommended)

- `preferred_shifts`
- `unavailable_days`
- `unavailable_shifts`
- `vacation_dates`
- `max_consecutive_days`
- `min_rest_hours`
- `night_shift_limit_per_week`
- `last_five_shifts`
- `seniority`

---

## `shifts.json` Schema

Each object in `shifts.json` represents a **shift assignment** and its requirements.

### Structure

```json
[
  {
    "id": "string",                   // Unique shift ID (e.g. "20250814E")
    "date": "YYYY-MM-DD",            // Shift date
    "day_of_week": "string",         // Day of the week (e.g. "Tuesday")
    "shift_type": "string",          // Type of shift ("morning", "evening", "night")
    "start_time": "HH:MM",           // Start time (24-hour)
    "end_time": "HH:MM",             // End time (24-hour)
    "duration_hours": number,        // Total duration in hours
    "required_roles": [              // List of required staff roles for the shift
      {
        "role": "string",            // Role needed (e.g. "doctor")
        "count": number,             // Number of staff needed in that role
        "skills_required": ["string"] // Specific required skills (can be empty)
      }
    ],
    "is_holiday": boolean,           // Whether the shift falls on a holiday
    "priority": "string",            // Priority level (e.g. "normal", "high")
    "department": "string",          // Department where the shift occurs
    "location": "string",            // Physical location (e.g. "Wing A")
    "notes": "string"                // Any additional notes for the shift
  }
]
```

### Required Fields

| Field            | Type     | Required | Description                                   |
|------------------|----------|----------|-----------------------------------------------|
| `id`            | string   | ✅       | Unique shift identifier                        |
| `date`          | string   | ✅       | Date of the shift (format: YYYY-MM-DD)         |
| `shift_type`    | string   | ✅       | Type of shift                                  |
| `start_time`    | string   | ✅       | Shift start time (24h format)                  |
| `end_time`      | string   | ✅       | Shift end time (24h format)                    |
| `duration_hours`| number   | ✅       | Total hours in the shift                       |
| `required_roles`| array    | ✅       | Required roles (with counts and skills)        |

### Optional Fields

- `day_of_week`
- `is_holiday`
- `priority`
- `department`
- `location`
- `notes`

---

## Validation Tips

- All dates must be in `"YYYY-MM-DD"` format.
- Skills and roles should be **lowercase** strings to ensure consistency.
- Shift `id` should be **unique** across the dataset.
- `required_roles[].skills_required` can be an empty array if no specific skills are needed.

---

> 💡 These schemas are enforced during runtime by the `validate_*` functions in `data_loader.py`.

---

## Related

- [Solver Documentation](./solver.md)
- [Project Structure](../README.md)
