"""Reproduce the e-commerce portfolio metrics using the Python standard library."""
import csv
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
print(f"Overall: {rate(rows)} (sessions, purchases, purchase rate %)")

by_visitor = defaultdict(list)
by_month = defaultdict(list)
by_pages = defaultdict(list)
for row in rows:
    by_visitor[row["VisitorType"]].append(row)
    by_month[row["Month"]].append(row)
    pages = int(row["ProductRelated"])
    bucket = "0–5" if pages <= 5 else "6–20" if pages <= 20 else "21–50" if pages <= 50 else "51–100" if pages <= 100 else "101+"
    by_pages[bucket].append(row)

report("Visitor type", by_visitor)
report("Product pages visited", by_pages)
report("Month", by_month)
