# David L Nias — Data Analytics Portfolio

Three public-data case studies focused on business decisions, reproducible calculations, data quality, and clear limits on what the evidence can support.

| Project | Decision question | Key result |
| --- | --- | --- |
| [E-commerce purchase behavior](ecommerce/README.md) | Where should a commerce team investigate purchase-rate improvement? | New visitors purchased at 24.91% versus 13.93% for returning visitors; the gap remains after a month-mix check. |
| [Washington EV registry](washington-ev/README.md) | Which markets warrant deeper charging-demand research? | King, Snohomish, and Pierce hold 69.29% of Washington's registered EVs in the snapshot. |
| [NYC 311 service operations](nyc-311/README.md) | Which request types drive workload and long closure tails? | Illegal Parking led volume at 13,694 requests; long-cycle categories show much higher medians and 90th percentiles. |

## How to read these projects

Each project page opens with a chart and an executive brief, then explains the KPI definitions, checks, recommendation, limitations, and reproduction steps. Python analyses use only the standard library; SQL examples show the core grouping and validation logic. Standalone HTML pages provide a presentation view.

`build_charts.py` regenerates the GitHub charts from the dated, verified summary figures. Each project's `analyze.py` shows how those figures were calculated from source data.

The projects are public-data practice analyses, not client or employer work. Data sources and licenses are credited in their respective READMEs. The Washington source CSV is omitted because it is about 82 MB; its download instructions are included. No personal contact information is stored here.
