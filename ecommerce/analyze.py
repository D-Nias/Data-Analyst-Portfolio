"""Reproduce the e-commerce portfolio metrics using the Python standard library."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

path = Path(__file__).parent / "data" / "online_shoppers_intention.csv"
month_order = ("Jan", "Feb", "Mar", "Apr", "May", "June", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
expected_columns = {
    "Administrative", "Administrative_Duration", "Informational", "Informational_Duration",
    "ProductRelated", "ProductRelated_Duration", "BounceRates", "ExitRates", "PageValues",
    "SpecialDay", "Month", "OperatingSystems", "Browser", "Region", "TrafficType",
    "VisitorType", "Weekend", "Revenue",
}
if not rows or not expected_columns.issubset(rows[0]):
    raise SystemExit(f"Input CSV is missing required columns: {sorted(expected_columns - set(rows[0] if rows else []))}")
if len(rows) != 12330:
    raise SystemExit(f"Expected 12,330 sessions, found {len(rows)}")
if not all(row["Revenue"] in ("TRUE", "FALSE") for row in rows):
    raise SystemExit("Revenue must contain only TRUE or FALSE")
blank_fields = sum(not value for row in rows for value in row.values())
if blank_fields:
    raise SystemExit(f"Input CSV has {blank_fields} blank fields")

def rate(group):
    n = len(group)
    purchases = sum(row["Revenue"] == "TRUE" for row in group)
    return n, purchases, round(100 * purchases / n, 2)

def report(label, groups):
    print("\n" + label)
    for key, group in groups.items():
        print(f"{key}: sessions={rate(group)[0]}, purchases={rate(group)[1]}, purchase_rate={rate(group)[2]}%")

print(f"Rows: {len(rows)}; blank fields: {sum(not value for row in rows for value in row.values())}")
print("Identical feature rows retained:", len(rows) - len({tuple(row.items()) for row in rows}))
print(f"Overall: {rate(rows)} (sessions, purchases, purchase rate %)")

by_visitor = defaultdict(list)
by_month = defaultdict(list)
by_pages = defaultdict(list)
by_visitor_weekend = defaultdict(list)
by_visitor_traffic = defaultdict(list)
for row in rows:
    by_visitor[row["VisitorType"]].append(row)
    by_month[row["Month"]].append(row)
    pages = int(row["ProductRelated"])
    bucket = "0–5" if pages <= 5 else "6–20" if pages <= 20 else "21–50" if pages <= 50 else "51–100" if pages <= 100 else "101+"
    by_pages[bucket].append(row)
    by_visitor_weekend[(row["VisitorType"], row["Weekend"])].append(row)
    by_visitor_traffic[(row["VisitorType"], row["TrafficType"])].append(row)

report("Visitor type", by_visitor)
report("Product pages visited", by_pages)
report("Month", by_month)
print("\nVisitor type by weekend")
for (visitor, weekend), group in sorted(by_visitor_weekend.items()):
    print(f"{visitor}, weekend={weekend}: sessions={rate(group)[0]}, purchases={rate(group)[1]}, purchase_rate={rate(group)[2]}%")

new = by_visitor["New_Visitor"]
returning = by_visitor["Returning_Visitor"]
p_new = rate(new)[1] / len(new)
p_returning = rate(returning)[1] / len(returning)
gap = p_new - p_returning
se = math.sqrt(p_new * (1 - p_new) / len(new) + p_returning * (1 - p_returning) / len(returning))
print(f"\nNew minus returning: {100 * gap:.2f} percentage points")
print(f"Approximate 95% interval for descriptive gap: {100 * (gap - 1.96 * se):.2f} to {100 * (gap + 1.96 * se):.2f} points")

eligible_months = []
month_groups = defaultdict(lambda: defaultdict(list))
for row in rows:
    month_groups[row["Month"]][row["VisitorType"]].append(row)
for month, groups in month_groups.items():
    if len(groups["New_Visitor"]) >= 30 and groups["Returning_Visitor"]:
        eligible_months.append(month)
total_weight = sum(
    len(month_groups[m]["New_Visitor"]) + len(month_groups[m]["Returning_Visitor"])
    for m in eligible_months
)
standardized = {}
for visitor in ("New_Visitor", "Returning_Visitor"):
    standardized[visitor] = sum(
        (len(month_groups[m]["New_Visitor"]) + len(month_groups[m]["Returning_Visitor"]))
        / total_weight * rate(month_groups[m][visitor])[1] / len(month_groups[m][visitor])
        for m in eligible_months
    )
print("Months with >=30 new visitors:", len(eligible_months))
print(f"Month-standardized new rate: {100 * standardized['New_Visitor']:.2f}%")
print(f"Month-standardized returning rate: {100 * standardized['Returning_Visitor']:.2f}%")

print("\nWeekend minus weekday rate within visitor type")
for visitor in ("New_Visitor", "Returning_Visitor"):
    weekday = by_visitor_weekend[(visitor, "FALSE")]
    weekend = by_visitor_weekend[(visitor, "TRUE")]
    p_weekday = rate(weekday)[1] / len(weekday)
    p_weekend = rate(weekend)[1] / len(weekend)
    difference = p_weekend - p_weekday
    difference_se = math.sqrt(
        p_weekday * (1 - p_weekday) / len(weekday)
        + p_weekend * (1 - p_weekend) / len(weekend)
    )
    print(
        f"{visitor}: {100 * difference:.2f} points "
        f"(approx. 95% interval {100 * (difference - 1.96 * difference_se):.2f} to "
        f"{100 * (difference + 1.96 * difference_se):.2f})"
    )

traffic_types = sorted({traffic for _, traffic in by_visitor_traffic})
eligible_traffic = [
    traffic for traffic in traffic_types
    if len(by_visitor_traffic[("New_Visitor", traffic)]) >= 30
    and len(by_visitor_traffic[("Returning_Visitor", traffic)]) >= 30
]
pooled_sessions = sum(
    len(by_visitor_traffic[(visitor, traffic)])
    for traffic in eligible_traffic
    for visitor in ("New_Visitor", "Returning_Visitor")
)
print("\nVisitor type by traffic category (eligible strata)")
for traffic in eligible_traffic:
    new_group = by_visitor_traffic[("New_Visitor", traffic)]
    returning_group = by_visitor_traffic[("Returning_Visitor", traffic)]
    print(
        f"TrafficType={traffic}: new={rate(new_group)}, "
        f"returning={rate(returning_group)}"
    )
standardized_traffic = {}
for visitor in ("New_Visitor", "Returning_Visitor"):
    standardized_traffic[visitor] = sum(
        (len(by_visitor_traffic[("New_Visitor", traffic)])
         + len(by_visitor_traffic[("Returning_Visitor", traffic)]))
        / pooled_sessions
        * rate(by_visitor_traffic[(visitor, traffic)])[1]
        / len(by_visitor_traffic[(visitor, traffic)])
        for traffic in eligible_traffic
    )
traffic_gap = standardized_traffic["New_Visitor"] - standardized_traffic["Returning_Visitor"]
raw_gap = p_new - p_returning
print(f"Eligible traffic categories: {len(eligible_traffic)}; pooled sessions: {pooled_sessions}")
print(f"Raw new-minus-returning gap: {100 * raw_gap:.2f} percentage points")
print(
    f"Traffic-mix-standardized new rate: {100 * standardized_traffic['New_Visitor']:.2f}%; "
    f"returning rate: {100 * standardized_traffic['Returning_Visitor']:.2f}%; "
    f"gap: {100 * traffic_gap:.2f} percentage points"
)


def summary_for(group):
    sessions, purchases, purchase_rate = rate(group)
    return {
        "sessions": sessions,
        "purchasing_sessions": purchases,
        "purchase_rate_pct": purchase_rate,
    }


visitor_gap_se = se
weekend_summary = {}
for visitor in ("New_Visitor", "Returning_Visitor"):
    weekday = by_visitor_weekend[(visitor, "FALSE")]
    weekend = by_visitor_weekend[(visitor, "TRUE")]
    p_weekday = rate(weekday)[1] / len(weekday)
    p_weekend = rate(weekend)[1] / len(weekend)
    difference = p_weekend - p_weekday
    difference_se = math.sqrt(
        p_weekday * (1 - p_weekday) / len(weekday)
        + p_weekend * (1 - p_weekend) / len(weekend)
    )
    weekend_summary[visitor] = {
        "weekday": summary_for(weekday),
        "weekend": summary_for(weekend),
        "weekend_minus_weekday_points": round(100 * difference, 2),
        "approx_95_ci_points": [
            round(100 * (difference - 1.96 * difference_se), 2),
            round(100 * (difference + 1.96 * difference_se), 2),
        ],
    }

traffic_summary = []
for traffic in eligible_traffic:
    new_group = by_visitor_traffic[("New_Visitor", traffic)]
    returning_group = by_visitor_traffic[("Returning_Visitor", traffic)]
    traffic_summary.append({
        "traffic_type": int(traffic),
        "new": summary_for(new_group),
        "returning": summary_for(returning_group),
        "new_minus_returning_points": round(
            100 * (rate(new_group)[1] / len(new_group) - rate(returning_group)[1] / len(returning_group)), 2
        ),
    })

summary = {
    "source": "UCI Online Shoppers Purchasing Intention Dataset",
    "source_year": 2018,
    "session_count": len(rows),
    "purchasing_session_count": sum(row["Revenue"] == "TRUE" for row in rows),
    "overall_purchase_rate_pct": rate(rows)[2],
    "quality": {
        "blank_fields": blank_fields,
        "identical_feature_rows_retained": len(rows) - len({tuple(row.items()) for row in rows}),
    },
    "visitor_types": {
        "New_Visitor": summary_for(by_visitor["New_Visitor"]),
        "Returning_Visitor": summary_for(by_visitor["Returning_Visitor"]),
        "Other": summary_for(by_visitor["Other"]),
    },
    "visitor_gap": {
        "new_minus_returning_points": round(100 * raw_gap, 2),
        "approx_95_ci_points": [
            round(100 * (raw_gap - 1.96 * visitor_gap_se), 2),
            round(100 * (raw_gap + 1.96 * visitor_gap_se), 2),
        ],
    },
    "product_page_bands": {label: summary_for(group) for label, group in by_pages.items()},
    "weekend_by_visitor": weekend_summary,
    "month_standardization": {
        "eligible_months": sorted(eligible_months, key=month_order.index),
        "excluded_months": sorted(set(by_month) - set(eligible_months), key=month_order.index),
        "pooled_sessions": total_weight,
        "new_purchase_rate_pct": round(100 * standardized["New_Visitor"], 2),
        "returning_purchase_rate_pct": round(100 * standardized["Returning_Visitor"], 2),
        "gap_points": round(100 * (standardized["New_Visitor"] - standardized["Returning_Visitor"]), 2),
    },
    "traffic_standardization": {
        "minimum_sessions_per_visitor_group": 30,
        "eligible_traffic_type_count": len(eligible_traffic),
        "pooled_sessions": pooled_sessions,
        "new_purchase_rate_pct": round(100 * standardized_traffic["New_Visitor"], 2),
        "returning_purchase_rate_pct": round(100 * standardized_traffic["Returning_Visitor"], 2),
        "gap_points": round(100 * traffic_gap, 2),
        "categories": traffic_summary,
    },
}
reconciliation_checks = {
    "visitor_sessions_equal_total": sum(value["sessions"] for value in summary["visitor_types"].values()) == len(rows),
    "visitor_purchases_equal_total": sum(value["purchasing_sessions"] for value in summary["visitor_types"].values()) == summary["purchasing_session_count"],
    "page_band_sessions_equal_total": sum(value["sessions"] for value in summary["product_page_bands"].values()) == len(rows),
    "page_band_purchases_equal_total": sum(value["purchasing_sessions"] for value in summary["product_page_bands"].values()) == summary["purchasing_session_count"],
}
if not all(reconciliation_checks.values()):
    raise SystemExit(f"Summary reconciliation failed: {reconciliation_checks}")
summary["reconciliation_checks"] = reconciliation_checks
Path(__file__).with_name("summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
