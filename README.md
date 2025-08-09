# Staff Shift Scheduling Agent

A constraint-based employee shift scheduling system powered by [Google OR-Tools](https://developers.google.com/optimization). This project generates optimized staff shift assignments based on staff data, shift requirements, and a rich set of configurable constraints.

---

## 📁 Project Structure

```
project_root/<br>
│<br>
├── data/                      # Input JSON data<br>
│   ├── staff.json<br>
│   ├── shifts.json<br>
│   └── constraints.json<br>
│<br>
├── scheduler/                       # Core scheduling logic<br>
│   └── parser.py         # Data loader and validator<br>
│   └── solver.py              # Scheduling solver<br>
│<br>
├── output/                    # Generated output (e.g. assignments.json)<br>
│<br>
├── docs/                      # Project documentation<br>
│   ├── schema.md              # JSON schema for input files<br>
│   ├── constraints.md         # Explanation of constraints.json<br>
│   ├── solver.md              # Full breakdown of solver logic<br>
│   └── data_loader.md         # Documentation for data_loader.py<br>
│<br>
└── README.md                  # You're here!<br>
```

---

## 📄 Documentation

All documentation files are located in the [`docs/`](./docs/) folder:

| Document                    | Description                                     |
|----------------------------|-------------------------------------------------|
| [`schema.md`](./docs/schema.md)           | Defines the structure of `staff.json` and `shifts.json` |
| [`constraints.md`](./docs/constraints.md) | Describes fields and logic in `constraints.json`         |
| [`data_loader.md`](./docs/data_loader.md) | Details how data is loaded and validated                 |
| [`solver.md`](./docs/solver.md)           | Full explanation of the scheduling algorithm             |

---

## ▶️ Getting Started

1. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   Make sure a `requirements.txt` file is present (e.g. includes `ortools`, etc.)

   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare input files** in the `data/` folder:

   - `staff.json`
   - `shifts.json`
   - `constraints.json`

4. **Run the scheduler**

   If you're using a module structure like `scheduler/solver.py`, run:

   ```bash
   python -m scheduler.solver
   ```

5. **View output**

   Once complete, the assignments will be saved to:

   ```bash
   cat output/assignments.json
   ```

---

## ✅ Features

- Constraint-based shift assignment using Google OR-Tools CP-SAT
- Supports hard constraints (e.g., hours, roles, availability)
- Flexible soft constraint weighting for optimization
- Staff preferences, rest periods, and fairness options
- Extendable and fully documented

---

## 📌 Notes

- Ensure all input files are valid JSON and conform to the schema.
- The system assumes shifts and roles are pre-defined and consistent.
- You can modify or extend constraints and preferences via `constraints.json`.

---

## 📚 Related

- [Google OR-Tools Documentation](https://developers.google.com/optimization)
- [JSON Schema Validator](https://json-schema.org/)

---

> Maintained with 🛠️ and 📘 by your scheduling logic and documentation team.
