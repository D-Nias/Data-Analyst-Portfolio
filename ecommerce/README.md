# Entry-level data analytics portfolio

![Bar charts comparing purchase rates by visitor type and product-page browsing depth](chart.svg)

Open `index.html` for the finished case study. The project uses the [UCI Online Shoppers Purchasing Intention dataset](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset) (12,330 sessions; CC BY 4.0). Source credit: Sakar, C. & Kastro, Y. (2018), DOI: 10.24432/C5F88Q.

## What this project demonstrates

- A defined business question and practical recommendation
- Data quality checks and documented limitations
- Reproducible analysis in Python and SQL
- Clear communication through a standalone case-study page

## Reproduce

The original CSV is in `data/online_shoppers_intention.csv`. Run `python analyze.py` from this folder to print the core metrics. The script uses Python's standard library. `queries.sql` runs in SQLite after importing the CSV as a table named `sessions` (booleans should be imported as 0/1).

## Honest use in applications

This is a public-data practice project, not work for a client or employer. Review the code and be ready to explain each number before claiming this project as your own. Identical rows are retained because the source describes sessions from distinct users; identical attributes do not prove duplicate events. The dataset has no session timestamps, order values, marketing spend, or experiment assignments, so this analysis cannot establish causation, revenue lift, or ROI.
