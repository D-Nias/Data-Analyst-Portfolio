# David L Nias — Data Analytics Portfolio

Four portfolio case studies focused on business decisions, reproducible calculations, data quality, and clear limits on what the evidence can support. Three use public datasets; one uses clearly labeled synthetic data to demonstrate a healthcare operations scorecard.

| Project | Decision question | Key result |
| --- | --- | --- |
| [E-commerce purchase behavior](ecommerce/README.md) | Where should a commerce team investigate purchase-rate improvement? | New visitors purchased at 24.91% versus 13.93% for returning visitors; the difference narrows to 8.25 points after a common traffic-mix check. |
| [Washington EV registry](washington-ev/README.md) | Which markets warrant deeper charging-demand research? | King, Snohomish, and Pierce hold 69.29% of Washington's registered EVs in the snapshot. |
| [NYC 311 service operations](nyc-311/README.md) | Which request types drive workload and long closure tails? | Illegal Parking led volume at 13,694 requests; long-cycle categories show much higher medians and 90th percentiles. |
| [Digital care operations scorecard](healthcare-ops/README.md) | Are onboarding and early member touchpoints happening on time? | Demonstrates mature-cohort KPI reporting, channel segmentation, SQL, and data-quality checks using synthetic data. |

## How to read these projects

Each project page opens with a chart and an executive brief, then explains the KPI definitions, checks, recommendation, limitations, and reproduction steps. Python analyses use only the standard library; SQL examples show the core grouping and validation logic. Standalone HTML pages provide a presentation view.

`build_charts.py` regenerates the public-data charts from dated summary figures. The healthcare-operations project generates its own fictional dataset and scorecard; its `analyze.py` reproduces the calculations.

These are practice analyses, not client or employer work. Public-data sources and licenses are credited in their respective READMEs; the healthcare-operations dataset is synthetic and clearly labeled. The Washington source CSV is omitted because it is about 82 MB; its download instructions are included. No personal contact information is stored here.
