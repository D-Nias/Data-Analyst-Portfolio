"""Generate the NYC 311 project charts from analyzer summaries."""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent


def text(x, y, value, size=20, color="#213047", weight="normal"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>')


def bar(x, y, width, label, value, maximum, display, color="#8059b1"):
    filled = 0 if maximum <= 0 else round(width * value / maximum, 1)
    return "".join((
        text(x, y - 10, label),
        f'<rect x="{x}" y="{y}" width="{width}" height="24" rx="12" fill="#ece8f3"/>',
        f'<rect x="{x}" y="{y}" width="{filled}" height="24" rx="12" fill="{color}"/>',
        text(x + width + 18, y + 20, display, 20, "#213047", "bold"),
    ))


def chart(path, title, subtitle, sections, footnote):
    height = max(650, max(y0 + 54 + 62 * len(items) + 120 for _, items, _, y0, _ in sections))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img">',
        f'<title>{escape(title)}</title><desc>{escape(subtitle + ". " + footnote)}</desc>',
        f'<rect width="1000" height="{height}" fill="#ffffff"/>',
        '<rect width="1000" height="12" fill="#8059b1"/>',
        text(55, 68, title, 34, "#15243a", "bold"),
        text(55, 102, subtitle, 19, "#5c6a79"),
    ]
    for header, items, unit, y0, maximum in sections:
        parts.append(text(55, y0, header, 25, "#15243a", "bold"))
        for index, (label, value, display) in enumerate(items):
            parts.append(bar(55, y0 + 54 + 62 * index, 690, label, value, maximum, display))
        parts.append(text(55, y0 + 54 + 62 * len(items) + 37, unit, 16, "#647285"))
    parts.extend((
        f'<line x1="55" y1="{height - 58}" x2="945" y2="{height - 58}" stroke="#d6dee8"/>',
        text(55, height - 25, footnote, 16, "#5c6a79"),
        "</svg>",
    ))
    path.write_text("\n".join(parts), encoding="utf-8")


summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
categories = {row["complaint_type"].casefold(): row for row in summary["top_complaint_types"]}
volume = sorted(summary["top_complaint_types"], key=lambda row: row["requests"], reverse=True)[:3]
long_cycle_names = ("Illegal Parking", "Damaged Tree", "Unsanitary Condition")
long_cycle = [(name, categories[name.casefold()]) for name in long_cycle_names]
chart(
    ROOT / "chart.svg",
    "NYC 311 service operations",
    f"{summary['request_count']:,} requests created June 1–7, 2026",
    [
        ("Highest-volume request types", [
            (row["complaint_type"], row["requests"], f"{row['requests']:,}") for row in volume
        ], "Number of requests", 155, max(row["requests"] for row in volume)),
        ("Median recorded time to close", [
            (name, row["median_hours"], f"{row['median_hours']:.2f} h") for name, row in long_cycle
        ], "Valid closed requests only; closure does not imply physical repair", 455,
         max(row["median_hours"] for _, row in long_cycle)),
    ],
    "Source: NYC Open Data 311 service requests. A request's close timestamp is an administrative event.",
)

pothole_path = ROOT / "pothole_summary.json"
if pothole_path.exists():
    pothole = json.loads(pothole_path.read_text(encoding="utf-8"))
    retrieved = re.search(r"retrieved_(\d{4})_(\d{2})_(\d{2})", pothole["source_file"])
    retrieval_label = "" if not retrieved else f" · filtered extract retrieved {retrieved[1]}-{retrieved[2]}-{retrieved[3]}"
    closure = pothole["closure_time"]
    card_data = [
        ("Requests", f"{pothole['request_count']:,}"),
        ("Close-date coverage", f"{pothole['close_date_coverage_pct']:.2f}%"),
        ("Average time to close", f"{closure['mean_hours']:.2f} h"),
        ("Valid closed records", f"{closure['valid_closed_requests']:,}"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="660" viewBox="0 0 1000 660" role="img">',
        '<title>Pothole service request closure time</title>',
        '<desc>1,506 pothole requests. Close-date coverage 93.89 percent. Average recorded time to close 31.11 hours, median 17.09 hours, and 90th percentile 75.07 hours.</desc>',
        '<rect width="1000" height="660" fill="#ffffff"/>',
        '<rect width="1000" height="12" fill="#8059b1"/>',
        text(45, 55, "NYC 311 pothole requests", 30, "#15243a", "bold"),
        text(45, 88, f"Created June 1–7, 2026{retrieval_label}", 15, "#5c6a79"),
    ]
    for i, (label, value) in enumerate(card_data):
        x = 45 + i * 235
        parts.extend((
            f'<rect x="{x}" y="122" width="215" height="105" rx="12" fill="#f4f1f8" stroke="#e0d8eb"/>',
            text(x + 14, 155, label, 14, "#5c5470", "bold"),
            text(x + 14, 199, value, 24, "#64428b", "bold"),
        ))
    parts.append(text(45, 280, "Recorded closure-time distribution", 21, "#15243a", "bold"))
    items = [
        ("Median", closure["median_hours"]),
        ("Mean", closure["mean_hours"]),
        ("90th percentile", closure["p90_hours"]),
    ]
    max_hours = max(value for _, value in items)
    for i, (label, value) in enumerate(items):
        parts.append(bar(45, 325 + i * 58, 680, label, value, max_hours, f"{value:.2f} hours", "#8059b1"))
    parts.extend((
        text(45, 525, "The mean is above the median because of a long upper tail.", 16, "#354254"),
        text(45, 555, f"{pothole['missing_close_dates']} requests have no close date; {pothole['negative_durations_excluded']} negative duration excluded.", 15, "#5c6a79"),
        '<line x1="45" y1="600" x2="955" y2="600" stroke="#d6dee8"/>',
        text(45, 630, "Administrative closure is not confirmation of a completed physical repair.", 14, "#5c6a79"),
        "</svg>",
    ))
    (ROOT / "potholes.svg").write_text("\n".join(parts), encoding="utf-8")
