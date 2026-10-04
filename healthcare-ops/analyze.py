"""Quality-check and summarize the synthetic care-operations cohort."""
import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent
DATA = ROOT / "data"
AS_OF = date(2026, 9, 30)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def iso_date(value):
    return date.fromisoformat(value)


def rate(numerator, denominator):
    return round(100 * numerator / denominator, 1) if denominator else None


def bar(x, y, width, value, maximum, color):
    filled = 0 if maximum == 0 else round(width * value / maximum, 1)
    return f'<rect x="{x}" y="{y}" width="{width}" height="18" rx="9" fill="#e5edf0"/><rect x="{x}" y="{y}" width="{filled}" height="18" rx="9" fill="{color}"/>'


def text(x, y, value, size=16, color="#233547", weight="normal"):
    return f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>'


def render_chart(summary):
    width, height = 1100, 800
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        '<title>Simulated digital care operations scorecard</title>',
        '<desc>Synthetic cohort enrollment, onboarding, milestone, and channel comparisons.</desc>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/><rect width="{width}" height="10" fill="#137a73"/>',
        text(44, 58, "Digital care operations scorecard", 28, "#15323b", "bold"),
        text(44, 88, "Fictional dataset · Cohort through September 30, 2026", 15, "#5d7078"),
        '<rect x="44" y="112" width="1012" height="50" rx="10" fill="#fff5df"/>',
        text(62, 143, "SYNTHETIC DATA — illustrative workflow metrics, not real member or company results", 15, "#78541a", "bold"),
    ]

    cards = [
        ("Enrolled members", f"{summary['total_members']:,}", "Jan–Aug 2026"),
        ("7-day first contact", f"{summary['activation']['rate_pct']}%", f"{summary['activation']['eligible']:,} mature members"),
        ("Day-30 check-in", f"{summary['day30']['rate_pct']}%", f"{summary['day30']['eligible']:,} mature members"),
        ("Day-60 activity", f"{summary['day60']['rate_pct']}%", f"{summary['day60']['eligible']:,} mature members"),
    ]
    for i, (label, value, note) in enumerate(cards):
        x = 44 + i * 258
        parts.extend([
            f'<rect x="{x}" y="184" width="238" height="112" rx="12" fill="#f4f8f9" stroke="#dce7e9"/>',
            text(x + 16, 213, label, 14, "#526970", "bold"),
            text(x + 16, 254, value, 30, "#137a73", "bold"),
            text(x + 16, 278, note, 12, "#64777d"),
        ])

    parts.append(text(44, 346, "Monthly enrollments", 19, "#15323b", "bold"))
    parts.append(text(590, 346, "Rates by enrollment channel", 19, "#15323b", "bold"))
    monthly = summary["monthly_enrollments"]
    max_members = max(monthly.values()) if monthly else 1
    for i, (month, count) in enumerate(monthly.items()):
        y = 378 + i * 39
        parts.extend([text(44, y + 15, month, 13), bar(150, y, 365, count, max_members, "#1d9a8e"), text(535, y + 15, count, 13, "#233547", "bold")])

    for i, (label, metric_key) in enumerate((
        ("7-day first contact", "activation"),
        ("Day-30 check-in", "day30"),
        ("Day-60 activity", "day60"),
    )):
        y = 378 + i * 112
        parts.append(text(590, y, label, 14, "#344f58", "bold"))
        for row_index, channel in enumerate(("Direct", "Employer")):
            value = summary["by_channel"][channel][metric_key]
            row_y = y + 12 + row_index * 29
            parts.extend([
                text(590, row_y + 15, channel, 12, "#536b73"),
                bar(665, row_y, 205, value["rate_pct"], 100, "#637fcb" if channel == "Direct" else "#1d9a8e"),
                text(885, row_y + 14, f"{value['rate_pct']}% · {value['completed']}/{value['eligible']}", 12, "#233547"),
            ])

    parts.append(text(590, 728, "Channel differences are simulated, not real-world findings.", 12, "#78541a"))
    parts.append(text(44, 770, "Window rules: contact days 0–7 · day-30 check-in days 28–37 · day-60 activity days 60–74", 13, "#536b73"))
    parts.append('</svg>')
    (ROOT / "scorecard.svg").write_text("\n".join(parts), encoding="utf-8")


def main():
    members = read_csv(DATA / "members.csv")
    events = read_csv(DATA / "events.csv")
    member_by_id = {row["member_id"]: row for row in members}
    event_ids = [row["event_id"] for row in events]
    member_ids = [row["member_id"] for row in members]
    errors = {
        "duplicate_member_ids": len(member_ids) - len(set(member_ids)),
        "duplicate_event_ids": len(event_ids) - len(set(event_ids)),
        "orphan_events": sum(row["member_id"] not in member_by_id for row in events),
        "events_before_enrollment": 0,
        "events_after_as_of": 0,
        "missing_required_values": 0,
    }
    for row in members:
        errors["missing_required_values"] += sum(not row[field].strip() for field in ("member_id", "enrollment_date", "channel", "care_team"))
    for row in events:
        errors["missing_required_values"] += sum(not row[field].strip() for field in ("event_id", "member_id", "event_type", "event_date"))
        if row["member_id"] in member_by_id:
            event_day = iso_date(row["event_date"])
            if event_day < iso_date(member_by_id[row["member_id"]]["enrollment_date"]):
                errors["events_before_enrollment"] += 1
            if event_day > AS_OF:
                errors["events_after_as_of"] += 1
    if any(errors.values()):
        raise SystemExit(f"Data quality checks failed: {errors}")

    events_by_member = defaultdict(list)
    for row in events:
        events_by_member[row["member_id"]].append(row)
    monthly = Counter(row["enrollment_date"][:7] for row in members)
    metrics = {}
    windows = {
        "activation": (7, "coach_contact_completed", 0, 7),
        "day30": (37, "day30_checkin_completed", 28, 37),
        "day60": (74, "day60_activity_observed", 60, 74),
    }
    segment_rows = defaultdict(dict)

    for metric, (maturity_days, event_type, low_day, high_day) in windows.items():
        cutoff = AS_OF - timedelta(days=maturity_days)
        eligible = [m for m in members if iso_date(m["enrollment_date"]) <= cutoff]
        numerator_members = []
        offsets = []
        for member in eligible:
            enrollment = iso_date(member["enrollment_date"])
            matching_offsets = [
                (iso_date(event["event_date"]) - enrollment).days
                for event in events_by_member[member["member_id"]]
                if event["event_type"] == event_type
            ]
            success_offsets = [day for day in matching_offsets if low_day <= day <= high_day]
            if success_offsets:
                numerator_members.append(member)
                offsets.append(min(success_offsets))
        metrics[metric] = {
            "eligible": len(eligible),
            "completed": len(numerator_members),
            "rate_pct": rate(len(numerator_members), len(eligible)),
            "median_event_day": round(statistics.median(offsets), 1) if offsets else None,
            "maturity_days": maturity_days,
            "window_days": [low_day, high_day],
        }
        for channel in ("Direct", "Employer"):
            channel_eligible = [m for m in eligible if m["channel"] == channel]
            channel_success = [m for m in numerator_members if m["channel"] == channel]
            segment_rows[channel][metric] = {
                "eligible": len(channel_eligible),
                "completed": len(channel_success),
                "rate_pct": rate(len(channel_success), len(channel_eligible)),
            }

    summary = {
        "as_of_date": AS_OF.isoformat(),
        "synthetic": True,
        "total_members": len(members),
        "total_events": len(events),
        "quality_checks": errors,
        "monthly_enrollments": dict(sorted(monthly.items())),
        **metrics,
        "by_channel": dict(segment_rows),
    }
    (ROOT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    render_chart(summary)

    print(f"Synthetic members: {len(members)}; synthetic events: {len(events)}; as of {AS_OF}")
    print("Data quality checks:", errors)
    print("Monthly enrollments:", dict(sorted(monthly.items())))
    for key, label in (("activation", "7-day first contact"), ("day30", "day-30 check-in"), ("day60", "day-60 activity")):
        value = metrics[key]
        print(f"{label}: {value['completed']}/{value['eligible']} eligible = {value['rate_pct']}%; median observed day={value['median_event_day']}")
    print("Channel scorecard:", json.dumps(segment_rows, sort_keys=True))


if __name__ == "__main__":
    main()
