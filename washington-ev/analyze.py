"""Analyze Washington's current EV registry snapshot (Python standard library)."""
import csv
from collections import Counter
from pathlib import Path

path = Path(__file__).parent / "data" / "ev_population.csv"
if not path.exists():
    raise SystemExit("Download the source CSV from https://data.wa.gov/d/f6w7-q2d2 into data/ev_population.csv")

all_rows = 0
wa_rows = 0
ids = set()
types = Counter()
counties = Counter()
makes = Counter()
years = Counter()
with path.open(newline="", encoding="utf-8-sig") as source:
    for row in csv.DictReader(source):
        all_rows += 1
        if row["State"] != "WA":
            continue
        wa_rows += 1
        ids.add(row["DOL Vehicle ID"])
        types[row["Electric Vehicle Type"]] += 1
        counties[row["County"]] += 1
        makes[row["Make"]] += 1
        years[row["Model Year"]] += 1

print("Source rows:", all_rows)
print("Washington rows:", wa_rows)
print("Unique WA DOL vehicle IDs:", len(ids))
print("Vehicle types:", types.most_common())
print("Top counties:", counties.most_common(10))
print("Top makes:", makes.most_common(10))
print("Model years 2023-2027:", [(y, years[str(y)]) for y in range(2023, 2028)])
