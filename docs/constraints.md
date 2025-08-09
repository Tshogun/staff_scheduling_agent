# Constraints Configuration Schema

This document defines the structure and meaning of the fields used in `constraints.json`. This file provides configuration for both **hard constraints** (mandatory scheduling rules) and **soft constraints** (preferences and penalties for optimization).

---

## Table of Contents

- [Overview](#overview)
- [File Structure](#file-structure)
- [Section: `hard_constraints`](#section-hard_constraints)
- [Section: `shift_config`](#section-shift_config)
- [Section: `soft_constraints`](#section-soft_constraints)
- [Validation Rules](#validation-rules)
- [Example](#example)

---

## Overview

The `constraints.json` file is used to:

- Enforce strict scheduling limits (`hard_constraints`)
- Define shift types and durations (`shift_config`)
- Provide optimization preferences (`soft_constraints`)

---

## File Structure

```json
{
  "hard_constraints": { ... },
  "shift_config": { ... },
  "soft_constraints": { ... }
}
```

---

## Section: `hard_constraints`

These are **non-negotiable rules** that must always be respected during scheduling.

| Key                           | Type    | Description                                          |
|-------------------------------|---------|------------------------------------------------------|
| `max_hours_per_week`          | number  | Maximum hours a staff member can work per week      |
| `max_shifts_per_week`         | number  | Maximum number of shifts per week                   |
| `min_days_off_per_week`       | number  | Minimum required days off per week                  |
| `max_consecutive_work_days`   | number  | Max workdays in a row before a break is enforced    |
| `min_rest_hours_between_shifts`| number | Minimum rest time between two shifts (in hours)     |
| `night_shift_limit_per_week`  | number  | Max number of night shifts per staff per week       |

✅ **All fields are required.**

---

## Section: `shift_config`

Defines the types of shifts available and their default timing structure.

### `shift_types`

```json
"shift_types": ["morning", "evening", "night"]
```

- List of defined shift categories.
- Used to match staff preferences and configure `shift_times`.

### `shift_times`

```json
"shift_times": {
  "morning": { "start": "07:00", "end": "15:00" },
  "evening": { "start": "15:00", "end": "23:00" },
  "night":   { "start": "23:00", "end": "07:00" }
}
```

- Defines time windows for each shift type.
- Times should be in `"HH:MM"` 24-hour format.

### `default_shift_duration_hours`

```json
"default_shift_duration_hours": 8
```

- Used if individual shifts do not specify a custom duration.

✅ **All three fields are required.**

---

## Section: `soft_constraints`

These guide the optimization by assigning **weights (penalties/bonuses)** to various soft rules. They are **not strictly enforced**, but the solver tries to minimize the total penalty score.

### `enable`

```json
"enable": true
```

- If `false`, soft constraints will be ignored.

### `weights`

| Key                             | Type   | Description                                                         |
|---------------------------------|--------|---------------------------------------------------------------------|
| `preferred_shift_match`         | number | Bonus for assigning preferred shifts                                |
| `avoided_shift_penalty`         | number | Penalty for assigning avoided shifts                                |
| `overtime_penalty`              | number | Penalty per hour exceeding max allowed weekly hours                 |
| `underscheduling_penalty`       | number | Penalty for not meeting minimum required weekly hours               |
| `understaffed_shift_penalty`    | number | Penalty when a shift is not fully staffed                           |
| `skill_mismatch_penalty`        | number | Penalty when required skills are not met by assigned staff          |
| `overstaffed_shift_penalty`     | number | Penalty when more staff than needed are assigned                    |

✅ **All weights are required if soft constraints are enabled.**

---

## Validation Rules

- `hard_constraints`, `shift_config`, and `soft_constraints` must all be present.
- All keys listed in each section must be provided.
- All numeric values should be non-negative integers.
- Shift times must be in `"HH:MM"` format (24-hour clock).

---

## Example

```json
{
  "hard_constraints": {
    "max_hours_per_week": 40,
    "max_shifts_per_week": 5,
    "min_days_off_per_week": 1,
    "max_consecutive_work_days": 5,
    "min_rest_hours_between_shifts": 12,
    "night_shift_limit_per_week": 2
  },
  "shift_config": {
    "shift_types": ["morning", "evening", "night"],
    "shift_times": {
      "morning": { "start": "07:00", "end": "15:00" },
      "evening": { "start": "15:00", "end": "23:00" },
      "night":   { "start": "23:00", "end": "07:00" }
    },
    "default_shift_duration_hours": 8
  },
  "soft_constraints": {
    "enable": true,
    "weights": {
      "preferred_shift_match": 5,
      "avoided_shift_penalty": 3,
      "overtime_penalty": 10,
      "underscheduling_penalty": 7,
      "understaffed_shift_penalty": 20,
      "skill_mismatch_penalty": 10,
      "overstaffed_shift_penalty": 5
    }
  }
}
```

---

> 📘 **Note**: These constraints work in tandem with shift and staff data. Ensure that your `staff.json` and `shifts.json` align with the shift types and expectations defined here.

---

## Related

- [Staff Schema](./schema.md#staffjson-schema)
- [Shift Schema](./schema.md#shiftsjson-schema)
- [Solver Documentation](./solver.md)
