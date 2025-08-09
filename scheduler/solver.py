import logging
from ortools.sat.python import cp_model
from scheduler.parser import load_all_data
from datetime import datetime
import json
from pathlib import Path

# === Configure logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


def generate_schedule():
    log.info("Loading input data...")
    staff_list, shift_list, constraints = load_all_data()
    log.info(f"Loaded {len(staff_list)} staff members")
    log.info(f"Loaded {len(shift_list)} shifts")

    model = cp_model.CpModel()

    staff_ids = [s["id"] for s in staff_list]
    shift_ids = [s["id"] for s in shift_list]

    # === Decision Variables ===
    log.info("Creating decision variables...")
    shift_assignments = {}
    for s_id in staff_ids:
        for sh_id in shift_ids:
            shift_assignments[(s_id, sh_id)] = model.NewBoolVar(f"{s_id}_works_{sh_id}")

    # === Constraints ===
    log.info("Applying constraints...")

    # 1. Shift coverage: role + collective skill coverage
    log.info("Ensuring shifts are fully staffed with required roles and skills...")
    for shift in shift_list:
        shift_id = shift["id"]
        shift_date = shift["date"]

        log.info(f"Evaluating shift: {shift_id} ({shift['shift_type']})")

        for role_req in shift["required_roles"]:
            role = role_req["role"]
            count = role_req["count"]
            skills_required = role_req.get("skills_required", [])

            log.info(f"  Required: {role} x{count}, Skills: {skills_required}")

            # Step 1: Eligible staff by role and availability
            eligible_staff = [
                s for s in staff_list
                if s["role"] == role and
                   shift_date not in s.get("unavailable_days", []) and
                   shift_id not in s.get("unavailable_shifts", [])
            ]
            eligible_ids = [s["id"] for s in eligible_staff]
            log.info(f"    Eligible by role & availability: {eligible_ids}")

            if len(eligible_ids) < count:
                raise ValueError(f"Not enough available staff for role '{role}' on shift {shift_id}")

            # Step 2: Must assign exactly 'count' staff to this role
            model.Add(
                sum(shift_assignments[(s_id, shift_id)] for s_id in eligible_ids) == count
            )

            # Step 3: Ensure collectively all required skills are covered
            for skill in skills_required:
                staff_with_skill = [
                    shift_assignments[(s["id"], shift_id)]
                    for s in eligible_staff if skill in s["skills"]
                ]
                log.info(f"    Staff with skill '{skill}': {[s['id'] for s in eligible_staff if skill in s['skills']]}")
                if not staff_with_skill:
                    raise ValueError(f"No eligible {role} has skill '{skill}' for shift {shift_id}")
                model.Add(sum(staff_with_skill) >= 1)

    # 2. One shift per day per staff
    log.info("Limiting each staff to one shift per day...")
    for s in staff_list:
        s_id = s["id"]
        shifts_by_date = {}
        for shift in shift_list:
            date = shift["date"]
            shifts_by_date.setdefault(date, []).append(shift)

        for date, shifts in shifts_by_date.items():
            model.Add(
                sum(shift_assignments[(s_id, sh["id"])] for sh in shifts) <= 1
            )
            log.debug(f"    {s_id} limited to 1 shift on {date}")

    # 3. Unavailable days
    log.info("Enforcing staff unavailable days...")
    for s in staff_list:
        s_id = s["id"]
        for shift in shift_list:
            if shift["date"] in s.get("unavailable_days", []):
                model.Add(shift_assignments[(s_id, shift["id"])] == 0)
                log.debug(f"    {s_id} unavailable on {shift['date']}")

    # 4. Unavailable specific shifts
    log.info("Enforcing staff unavailable shift IDs...")
    for s in staff_list:
        s_id = s["id"]
        for sh_id in s.get("unavailable_shifts", []):
            if (s_id, sh_id) in shift_assignments:
                model.Add(shift_assignments[(s_id, sh_id)] == 0)
                log.debug(f"    {s_id} unavailable for shift {sh_id}")

    # === Solve ===
    log.info("Solving model...")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    status = solver.Solve(model)

    # === Output ===
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        log.info("Schedule successfully generated.")
        result = []

        for shift in shift_list:
            assigned_staff = []
            for s in staff_list:
                if solver.BooleanValue(shift_assignments[(s["id"], shift["id"])]):
                    assigned_staff.append(s["id"])
                    log.info(f"{s['id']} assigned to shift {shift['id']} ({shift['shift_type']})")

            result.append({
                "shift_id": shift["id"],
                "staff_ids": assigned_staff
            })

        output_path = Path("output/assignments.json")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        log.info(f"Schedule written to {output_path}")
        return result
    else:
        log.warning("No feasible schedule found within time limit.")
        return None


if __name__ == "__main__":
    start = datetime.now()
    log.info("Starting schedule generation...")
    try:
        generate_schedule()
    except Exception as e:
        log.exception(f"Error during schedule generation: {e}")
    finally:
        end = datetime.now()
        log.info(f"Finished in {end - start}")
