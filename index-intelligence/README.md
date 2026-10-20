# Index Intelligence

Private NIFTY research dashboard built from the audited daily-snapshot warehouse.

## Features

- Snapshot-date selector, index search and curated research groups.
- Daily / 1M / 3M / 1Y rankings, sortable numeric columns and filtered CSV exports with baseline dates.
- P/E versus P/B scatterplot with index selection and keyboard interaction.
- Index detail, October observed-data chart, comparison of up to three indices on common dates.
- Browser-local watchlist; no account sync or order execution.
- Source attribution, sampled-history disclosure and separate special variants.

## Local update path

The existing Windows task `NiftyIndices Daily Reports` invokes the sibling `nifty-automation/pipeline.py`. That script imports `build_dashboard.py` after generating reports, rebuilding both:

- `../nifty-automation/data/reports/dashboard.html` (self-contained local dashboard)
- `dist/index.html` (static publication copy)

Build manually with `python build_dashboard.py`. The warehouse remains local SQLite with checksum-addressed raw files. No server or dependency install is needed to open the self-contained HTML.

## Hosted copy

Sites identity is in `.openai/hosting.json`. The private hosted copy contains the dataset baked into the last published `dist/index.html`. It does not read the PC's files or scheduler. Publishing new data requires rebuilding and republishing; there is no unattended cloud sync yet. Do not imply that reloading the hosted page fetches newer NSE reports.

## History

Initial warehouse coverage: 15 sampled dates, 2,474 observations. October snapshots plus 17 October 2025, 17 July 2026 and 18 September 2026 provide available 1Y/3M/1M baselines as of 19 October 2026. Indices absent at a baseline remain N/A. The dataset is not a complete daily history. Returns use 30/90/365 calendar days with a maximum 7-day baseline tolerance, not calendar-month or exact trading-day returns.

The broad-market/sector lists and special-variant name rules are local navigation aids, not official classifications. Do not interpret index breadth as stock breadth or low valuation as a buy signal. Source variants include specialized indices; the standard filter separates inverse, leveraged, volatility, currency, futures and selected non-equity variants.
