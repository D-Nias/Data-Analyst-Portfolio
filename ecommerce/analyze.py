"""Reproduce the e-commerce portfolio metrics using the Python standard library."""
import csv
import math
from collections import defaultdict
from pathlib import Path

path = Path(__file__).parent / "data" / "online_shoppers_intention.csv"
rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
assert len(rows) == 12330
assert all(row["Revenue"] in ("TRUE", "FALSE") for row in rows)

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
for row in rows:
    by_visitor[row["VisitorType"]].append(row)
    by_month[row["Month"]].append(row)
    pages = int(row["ProductRelated"])
    bucket = "0–5" if pages <= 5 else "6–20" if pages <= 20 else "21–50" if pages <= 50 else "51–100" if pages <= 100 else "101+"
    by_pages[bucket].append(row)
    by_visitor_weekend[(row["VisitorType"], row["Weekend"])].append(row)

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
total_weight = sum(len(by_month[m]) for m in eligible_months)
standardized = {}
for visitor in ("New_Visitor", "Returning_Visitor"):
    standardized[visitor] = sum(
        len(by_month[m]) / total_weight * rate(month_groups[m][visitor])[1] / len(month_groups[m][visitor])
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
