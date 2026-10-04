"""Generate a deterministic, fictional care-program operations dataset.

This dataset is synthetic and is not derived from Calibrate or any real patient.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SEED = 20261004
AS_OF = date(2026, 9, 30)
START = date(2026, 1, 1)
LAST_ENROLLMENT = date(2026, 8, 31)
MEMBER_COUNT = 720


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    DATA.mkdir(exist_ok=True)
    rng = random.Random(SEED)
    members = []
    events = []
    next_event = 1
    enrollment_span = (LAST_ENROLLMENT - START).days

    # The different channel probabilities are fictional inputs for demonstrating
    # segmented reporting, not estimates of a real program's performance.
    profiles = {
        "Direct": {"contact": 0.77, "day30": 0.70, "day60": 0.62},
        "Employer": {"contact": 0.84, "day30": 0.77, "day60": 0.70},
    }

    for number in range(1, MEMBER_COUNT + 1):
        member_id = f"SYN{number:04d}"
        enrollment = START + timedelta(days=rng.randint(0, enrollment_span))
        channel = "Employer" if rng.random() < 0.32 else "Direct"
        coach = f"TEAM-{rng.randint(1, 6):02d}"
        members.append({
            "member_id": member_id,
            "enrollment_date": enrollment.isoformat(),
            "channel": channel,
            "care_team": coach,
        })

        def add_event(event_type, offset):
            nonlocal next_event
            event_date = enrollment + timedelta(days=offset)
            if event_date <= AS_OF:
                events.append({
                    "event_id": f"EVT{next_event:06d}",
                    "member_id": member_id,
                    "event_type": event_type,
                    "event_date": event_date.isoformat(),
                })
                next_event += 1

        profile = profiles[channel]
        if rng.random() < profile["contact"]:
            add_event("coach_contact_completed", rng.choice([0, 1, 2, 3, 4, 5, 7, 9, 12]))

        age = (AS_OF - enrollment).days
        if age >= 28 and rng.random() < profile["day30"]:
            add_event("day30_checkin_completed", rng.randint(28, 37))
        if age >= 60 and rng.random() < profile["day60"]:
            add_event("day60_activity_observed", rng.randint(60, 74))

    write_csv(DATA / "members.csv", ["member_id", "enrollment_date", "channel", "care_team"], members)
    write_csv(DATA / "events.csv", ["event_id", "member_id", "event_type", "event_date"], events)
    print(f"Generated {len(members)} fictional members and {len(events)} fictional events (seed {SEED}).")


if __name__ == "__main__":
    main()
