import json
import logging
from datetime import datetime
from pathlib import Path

from ortools.sat.python import cp_model

from scheduler.parser import load_all_data

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)


def generate_schedule():
    log.info("Loading input data...")
    staff_list, shift_list, constraints_data = load_all_data()
    log.info(f"Loaded {len(staff_list)} staff members")
    log.info(f"Loaded {len(shift_list)} shifts")

    hard_constraints = constraints_data["hard_constraints"]
    soft_constraints = constraints_data["soft_constraints"]["weights"]
    shift_duration = constraints_data["shift_config"].get(
        "default_shift_duration_hours", 8
    )

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    staff_ids = [s["id"] for s in staff_list]
    shift_ids = [s["id"] for s in shift_list]

    # Decision Variables
    log.info("Creating decision variables...")
    shift_assignments = {
        (s_id, sh_id): model.NewBoolVar(f"{s_id}_works_{sh_id}")
        for s_id in staff_ids
        for sh_id in shift_ids
    }

    # Objective terms for soft constraints
    objective_terms = []

    # HARD CONSTRAINTS
    log.info("Applying hard constraints...")
    for shift in shift_list:
        shift_id = shift["id"]
        shift_date = shift["date"]
        for role_req in shift["required_roles"]:
            role = role_req["role"]
            required_count = role_req["count"]
            required_skills = role_req.get("skills_required", [])

            eligible_staff = [
                s
                for s in staff_list
                if s["role"] == role
                and shift_date not in s.get("unavailable_days", [])
                and shift_id not in s.get("unavailable_shifts", [])
            ]
            eligible_ids = [s["id"] for s in eligible_staff]
            log.info(
                f"Shift {shift_id} requires {required_count} x {role}. Eligible: {eligible_ids}"
            )

            if not eligible_ids:
                log.warning(f"No eligible staff for role '{role}' on shift {shift_id}.")
                continue

            assigned = [shift_assignments[(s_id, shift_id)] for s_id in eligible_ids]
            assigned_sum = model.NewIntVar(
                0, len(eligible_ids), f"{shift_id}_{role}_assigned"
            )
            model.Add(assigned_sum == sum(assigned))

            shortage = model.NewIntVar(0, required_count, f"{shift_id}_{role}_shortage")
            model.Add(shortage == required_count - assigned_sum)
            objective_terms.append(
                shortage * soft_constraints["understaffed_shift_penalty"]
            )

            # Skill coverage
            for skill in required_skills:
                staff_with_skill = [
                    shift_assignments[(s["id"], shift_id)]
                    for s in eligible_staff
                    if skill in s.get("skills", [])
                ]
                if staff_with_skill:
                    model.Add(sum(staff_with_skill) >= 1)
                else:
                    log.warning(
                        f"No eligible {role} has skill '{skill}' for shift {shift_id}"
                    )
                    penalty = model.NewIntVar(
                        0, 1, f"{shift_id}_{role}_{skill}_mismatch"
                    )
                    model.Add(penalty == 1)
                    objective_terms.append(
                        penalty * soft_constraints["skill_mismatch_penalty"]
                    )

    # One shift per day per staff
    log.info("Applying one-shift-per-day constraint...")
    for s in staff_list:
        s_id = s["id"]
        shifts_by_date = {}
        for sh in shift_list:
            shifts_by_date.setdefault(sh["date"], []).append(sh)
        for _date, shifts in shifts_by_date.items():
            model.Add(sum(shift_assignments[(s_id, sh["id"])] for sh in shifts) <= 1)

    # Enforce unavailability
    log.info("Enforcing staff availability constraints...")
    for s in staff_list:
        s_id = s["id"]
        for sh in shift_list:
            if sh["date"] in s.get("unavailable_days", []) or sh["id"] in s.get(
                "unavailable_shifts", []
            ):
                model.Add(shift_assignments[(s_id, sh["id"])] == 0)

    # SOFT CONSTRAINTS
    log.info("Adding soft constraints to objective function...")
    for s in staff_list:
        s_id = s["id"]
        preferred_shifts = set(s.get("preferred_shifts", []))
        max_hours = s.get("max_hours_per_week", hard_constraints["max_hours_per_week"])
        min_hours = s.get("min_hours_per_week", 0)

        total_hours = sum(
            shift_duration * shift_assignments[(s_id, sh_id)] for sh_id in shift_ids
        )

        # Preferred shift bonus
        for sh in shift_list:
            if sh["shift_type"] in preferred_shifts:
                objective_terms.append(
                    -soft_constraints["preferred_shift_match"]
                    * shift_assignments[(s_id, sh["id"])]
                )

        # Overtime penalty
        overtime = model.NewIntVar(0, 1000, f"{s_id}_overtime")
        model.Add(total_hours - max_hours <= overtime)
        model.AddMaxEquality(overtime, [total_hours - max_hours, 0])
        objective_terms.append(overtime * soft_constraints["overtime_penalty"])

        # Underscheduling penalty
        underscheduled = model.NewIntVar(0, 1000, f"{s_id}_underscheduled")
        model.Add(min_hours - total_hours <= underscheduled)
        model.AddMaxEquality(underscheduled, [min_hours - total_hours, 0])
        objective_terms.append(
            underscheduled * soft_constraints["underscheduling_penalty"]
        )
        
        # Night shift soft limit
        max_night_shifts = hard_constraints.get("night_shift_limit_per_week", 2)
        night_shifts = [
            shift_assignments[(s_id, sh["id"])]
            for sh in shift_list
            if sh["shift_type"] == "night"
        ]
        total_night_shifts = sum(night_shifts)

        excess_night = model.NewIntVar(0, len(night_shifts), f"{s_id}_excess_night")
        model.Add(total_night_shifts - max_night_shifts <= excess_night)
        model.AddMaxEquality(excess_night, [total_night_shifts - max_night_shifts, 0])
        objective_terms.append(
            excess_night * soft_constraints["max_night_shifts_penalty"]
        )

    # Set Objective
    model.Minimize(sum(objective_terms))

    # Solve
    log.info("Solving...")
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        log.info("Schedule generated successfully.")
        result = []
        for shift in shift_list:
            assigned_staff = []
            for s in staff_list:
                if solver.BooleanValue(shift_assignments[(s["id"], shift["id"])]):
                    assigned_staff.append(s["id"])
                    log.info(
                        f"Assigned {s['id']} to shift {shift['id']} ({shift['shift_type']})"
                    )
            result.append({"shift_id": shift["id"], "staff_ids": assigned_staff})

        output_path = Path("output/assignments.json")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        log.info(f"Schedule saved to {output_path}")
        return result
    else:
        log.warning("No feasible solution found.")
        return None


if __name__ == "__main__":
    start = datetime.now()
    log.info("Starting schedule generation...")
    try:
        generate_schedule()
    except Exception as e:
        log.exception(f"Error during schedule generation: {e}")
    finally:
        log.info(f"Finished in {datetime.now() - start}")
