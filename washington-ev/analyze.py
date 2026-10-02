"""Analyze Washington's current EV registry snapshot (Python standard library)."""
import csv
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data" / "ev_population.csv"
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
    reader = csv.DictReader(source)
    required_columns = {
        "State", "DOL Vehicle ID", "Electric Vehicle Type", "County", "Make", "Model Year"
    }
    missing_columns = required_columns - set(reader.fieldnames or [])
    if missing_columns:
        raise SystemExit(f"Source CSV is missing required columns: {', '.join(sorted(missing_columns))}")
    missing_ids = 0
    repeated_id_rows = 0
    missing_counties = 0
    missing_vehicle_types = 0
    for row in reader:
        all_rows += 1
        if row["State"].strip() != "WA":
            continue
        wa_rows += 1
        vehicle_id = row["DOL Vehicle ID"].strip()
        county = row["County"].strip()
        vehicle_type = row["Electric Vehicle Type"].strip()
        if not vehicle_id:
            missing_ids += 1
        elif vehicle_id in ids:
            repeated_id_rows += 1
        else:
            ids.add(vehicle_id)
        missing_counties += not bool(county)
        missing_vehicle_types += not bool(vehicle_type)
        types[vehicle_type] += 1
        counties[county] += 1
        makes[row["Make"]] += 1
        years[row["Model Year"]] += 1

print("Source rows:", all_rows)
print("Washington rows:", wa_rows)
print("Unique WA DOL vehicle IDs:", len(ids))
print("Washington rows missing DOL vehicle ID:", missing_ids)
print("Repeated nonblank DOL vehicle ID rows:", repeated_id_rows)
print("Washington rows missing county:", missing_counties)
print("Washington rows missing vehicle type:", missing_vehicle_types)
print("Vehicle types:", types.most_common())
print("Top counties:", counties.most_common(10))
print("Top makes:", makes.most_common(10))
print("Model years 2023-2027:", [(y, years[str(y)]) for y in range(2023, 2028)])
print("BEV share:", round(100 * types["Battery Electric Vehicle (BEV)"] / wa_rows, 2), "%")
print("Top-three county share:", round(100 * sum(n for _, n in counties.most_common(3)) / wa_rows, 2), "%")
print("Top-five county share:", round(100 * sum(n for _, n in counties.most_common(5)) / wa_rows, 2), "%")
