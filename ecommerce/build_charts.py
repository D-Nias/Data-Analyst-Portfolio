"""Render the e-commerce SVGs from metrics calculated from the source CSV."""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
DATA = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
ACCENT = "#11877f"


def text(x, y, value, size=20, color="#213047", weight="normal"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" '
            f'font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>')


def bar(x, y, width, label, value, maximum, display):
    filled = 0 if maximum <= 0 else round(width * value / maximum, 1)
    return "".join((
        text(x, y - 10, label),
        f'<rect x="{x}" y="{y}" width="{width}" height="24" rx="12" fill="#e8edf2"/>',
        f'<rect x="{x}" y="{y}" width="{filled}" height="24" rx="12" fill="{ACCENT}"/>',
        text(x + width + 18, y + 20, display, 20, "#213047", "bold"),
    ))


def render(path, title, subtitle, sections, footnote):
    height = max(620, max(y0 + 54 + 62 * len(items) + 120 for _, items, _, y0, _ in sections))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img">',
        f'<title>{escape(title)}</title><desc>{escape(subtitle + ". " + footnote)}</desc>',
        f'<rect width="1000" height="{height}" fill="#ffffff"/>',
        f'<rect width="1000" height="12" fill="{ACCENT}"/>',
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


visitors = DATA["visitor_types"]
product_pages = DATA["product_page_bands"]
render(
    ROOT / "chart.svg",
    "E-commerce purchase behavior",
    f"{DATA['session_count']:,} shopping sessions · UCI public dataset",
    [
        ("Purchase rate by visitor type", [
            ("New", visitors["New_Visitor"]["purchase_rate_pct"], f"{visitors['New_Visitor']['purchase_rate_pct']:.2f}%"),
            ("Returning", visitors["Returning_Visitor"]["purchase_rate_pct"], f"{visitors['Returning_Visitor']['purchase_rate_pct']:.2f}%"),
        ], "Percent of sessions ending in purchase", 155, 30),
        ("Purchase rate by product pages viewed", [
            (f"{label} pages", values["purchase_rate_pct"], f"{values['purchase_rate_pct']:.2f}%")
            for label, values in product_pages.items()
        ], "Association only; more browsing is not proven to cause purchasing", 420, 35),
    ],
    "Source: UCI Online Shoppers Purchasing Intention · 2018",
)

weekend = DATA["weekend_by_visitor"]
render(
    ROOT / "visitor-weekend.svg",
    "Weekend patterns differ by visitor type",
    "Purchase rate by visitor segment and session day",
    [
        ("Sessions ending in purchase", [
            (f"{label} · {day.lower()}", weekend[visitor][day]["purchase_rate_pct"],
             f"{weekend[visitor][day]['purchase_rate_pct']:.2f}%")
            for visitor, label in (("New_Visitor", "New"), ("Returning_Visitor", "Returning"))
            for day in ("weekday", "weekend")
        ], "Weekend-minus-weekday differences are descriptive", 170, 30),
    ],
    "Traffic source, device, and shopper intent may differ between sessions.",
)

traffic = DATA["traffic_standardization"]
render(
    ROOT / "visitor-traffic.svg",
    "Traffic mix explains part of the visitor gap",
    "New-minus-returning purchase-rate difference · percentage points",
    [
        ("Visitor-rate gap", [
            ("Raw comparison", DATA["visitor_gap"]["new_minus_returning_points"],
             f"{DATA['visitor_gap']['new_minus_returning_points']:.2f} points"),
            ("Common traffic mix", traffic["gap_points"], f"{traffic['gap_points']:.2f} points"),
        ], f"Standardized over {traffic['eligible_traffic_type_count']} traffic categories with at least {traffic['minimum_sessions_per_visitor_group']} sessions per group", 180, 12),
    ],
    f"Common weights use pooled sessions across categories · n={traffic['pooled_sessions']:,}",
)
