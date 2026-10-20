# Index Intelligence

Interactive NIFTY performance and valuation dashboard generated from an audited daily-snapshot warehouse.

## Views

All published indices are visible by default. The sector view includes all 34 entries in the official sectoral catalogue checked on 20 October 2026, including MidSmall and Healthcare variants. Special variants remain visible under All indices but are excluded from standard-equity leadership bars.

Rankings and charts support present month (MTD), 1M, 3M, 6M, 1Y, 2Y, 3Y and 5Y. Cumulative returns are the default. An optional CAGR toggle annualizes 1Y and longer only. Charts always show cumulative/rebased levels. MTD uses the previous month-end close; other periods use calendar anniversaries with month-end clamping and at most a 7-day backward baseline tolerance. Actual baseline dates are exported and shown in details. A missing or zero baseline stays unavailable.

Includes index search, sortable columns, P/E-P/B scatterplot, browser-local watchlists, comparison of up to three indices on common dates, filtered CSV generation and a prebuilt latest-performance matrix CSV.

## Data coverage

Initial extended release: 10,166 observations, 79 stored dates from 19 October 2021 through 19 October 2026. Historical paths are monthly snapshots plus explicit return anchors and recent daily points, not complete daily five-year histories. Latest snapshot has 167 indices. Available verified baseline coverage: MTD 166, 3M 161, 6M 146, 1Y 143, 2Y 123, 3Y 103 and 5Y 87. Newer indices remain listed with N/A for unavailable periods.

Case and punctuation differences in index names are normalized for dashboard history matching. PR/TR/currency/leverage tokens remain distinct; ambiguous same-date alias collisions fail the build. Original names/bytes stay in SQLite and archived CSVs.

## Build and tests

Python 3.10+; no external Python packages.

```sh
python build_dashboard.py
python -m unittest discover -s . -v
```

The sibling downloader rebuilds the self-contained `../nifty-automation/data/reports/dashboard.html`, `performance-latest.csv`, and publication output `dist/` after downloading. It also refreshes the exact rolling baseline files for the latest snapshot.

## Storage and hosting

Working data lives in the sibling `nifty-automation/data/warehouse.sqlite` and `data/raw/`. The user explicitly requested the source CSVs, database backup and reports in https://github.com/ethereum007/niftyindices-analysis, a public repository. Secrets are excluded. SQLite backups are made with the backup API; raw CSVs use Git -text attributes so source checksums survive cloning.

The private Sites publication at https://kiran-index-intelligence.kirandnyc.chatgpt.site is a fixed publication snapshot. The local Windows task refreshes local files at 19:00 and 21:00 IST weekdays while the PC is on and the user is logged in. There is no cloud data-refresh connection yet.

Browser QA covered all horizons, all-index and 34-sector counts, numeric sorting/CAGR, comparison, source-date changes and mobile layout. Automated browser download saving was canceled by the browser environment; CSV payload/schema and the prebuilt matrix are separately verified. Source attribution is not a redistribution licence. No blanket licence is applied to third-party market data.
