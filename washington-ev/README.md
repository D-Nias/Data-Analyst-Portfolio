# Washington electric vehicle registry snapshot

**Question:** Where are registered electric vehicles concentrated in Washington, and what is their vehicle-type mix?

**Source:** [Washington State Department of Licensing, Electric Vehicle Population Data](https://data.wa.gov/d/f6w7-q2d2), accessed September 28, 2026. Public data, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). This repository credits the original data provider and links to the current source.

## Results from the September 28, 2026 download

- 299,705 records in the full source file; 298,916 have `State = WA`.
- The Washington subset has 298,916 distinct DOL vehicle IDs.
- 241,125 battery-electric vehicles (80.67%) and 57,791 plug-in hybrids (19.33%).
- King County has 144,257 registrations (48.26% of the Washington subset), followed by Snohomish (37,818) and Pierce (25,042).
- Tesla is the most common make in this snapshot, with 122,573 registrations (41.00%).

## Method and limits

The unit is a **registered vehicle in the current snapshot**, not a sale. Counts by model year therefore do **not** represent annual sales or adoption. This file includes records outside Washington, so the analysis filters to `State = WA`. County shares are counts of registered EVs, not adoption rates; population or total vehicle registrations would be needed for fair county comparisons. The source changes over time, so rerunning the script against a later download can yield different counts.

The full CSV is about 82 MB and is intentionally excluded from the upload. Download the source CSV from the data portal and save it as `data/ev_population.csv`, then run `python analyze.py` from this folder. The script uses only Python's standard library.
