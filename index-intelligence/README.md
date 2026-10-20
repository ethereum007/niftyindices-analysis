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

## Daily-history continuation — 21 October 2026

Added a bounded resumable weekday-file backfill. First batch attempted 48 dates: 46 accepted daily snapshots and two non-CSV responses recorded separately. Current database: 17,714 observations over 125 accepted dates; raw archive: 127 responses. Weekday candidates are not an audited exchange calendar; special weekend sessions remain unaudited. Missing/non-CSV files never prove holidays.

The publication now uses an indexed data payload, storing repeated names, dates and source hashes once. Historical period results are computed when a snapshot is selected, with the same calendar targets, 7-day tolerance and CAGR formula as Python. Browser/Python parity passed for 11,067 values over four dates. The self-contained dashboard fell from 6,630,090 to 1,224,476 bytes despite the larger dataset. Full original observations remain in SQLite and source CSVs.

Validation: 19 Python tests, all requested horizons, 167-index and 34-sector counts, CSV payload/static route, comparisons and mobile no-overflow. Hosted refresh is still a fixed publication; local task and GitHub data backup remain distinct.

### Daily-history batch 2

Another 48 weekday files checked: 46 accepted, two non-CSV responses. Current archive: 24,785 observations, 171 accepted dates and 174 raw responses. The bounded daily scan reached 12 May 2026. Source dates still span October 2021–October 2026 through monthly samples and explicit anchors; full daily five-year coverage remains incomplete. The dashboard is approximately 1.7 MB.

### Daily-history batch 3

Checked another 48 weekday candidates: 42 accepted snapshots, six non-CSV responses. Current archive: 30,953 observations over 213 accepted dates; 216 raw responses. The backward scan reached 2 March 2026. The latest market snapshot remains 19 October 2026; full five-year daily history and special weekend sessions are not yet audited. Compact dashboard size: 2,141,140 bytes.

### Daily-history cadence batch 4

Two bounded batches checked 96 weekday candidates: 91 accepted snapshots and five non-CSV responses, with no rate-limit/access stop. The daily scan now reaches 9 October 2025. Current archive: 44,012 observations over 304 accepted dates; 308 archived raw responses. The dashboard is 3,049,129 bytes. Full five-year daily coverage and weekend sessions remain unaudited. Latest snapshot date is still 2026-10-19; this is historical expansion.

### Daily-history cadence batch 5

Checked 96 weekday candidates: 93 accepted snapshots, three non-CSV responses, no access/rate-limit stop. Backward daily scan reached 21 May 2025. Archive now has 57,080 observations over 397 accepted dates and 401 raw responses. Compact dashboard size is 3,953,729 bytes. Latest market snapshot remains 2026-10-19; full daily five-year coverage and weekend-session audit remain incomplete.


### 2026-10-21 cadence batch 6
Added 89 accepted daily snapshots from 96 attempts, scanning through 2025-01-01. Archive: 69,122 observations / 486 accepted dates / 491 unique raw responses. Latest market date remains 2026-10-19. There are 794 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity passed; browser/Python parity passed for 14,028 values over four dates including 2025-03-03. Compact dashboard: 4,790,623 bytes.


### 2026-10-21 cadence batch 7
Added 91 accepted daily snapshots from 96 attempts, scanning through 2024-08-12. Archive: 80,357 observations / 577 accepted dates / 582 unique raw responses. Latest market date remains 2026-10-19. There are 698 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity passed; browser/Python parity passed for 13,636 values over four dates including 2024-10-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 5,554,331 bytes.


### 2026-10-21 cadence batch 8
Added 88 accepted daily snapshots from 96 attempts, scanning through 2024-03-22. Archive: 90,432 observations / 665 accepted dates / 671 unique raw responses. Latest market date remains 2026-10-19. There are 602 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 665 accepted source files. Browser/Python parity passed for 13,384 values over four dates including 2024-06-04. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 6,240,060 bytes.


### 2026-10-21 cadence batch 9
Added 90 accepted daily snapshots from 96 attempts, scanning through 2023-11-03. Archive: 100,167 observations / 755 accepted dates / 761 unique raw responses. Latest market date remains 2026-10-19. There are 506 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 755 accepted source files. Browser/Python parity passed for 13,272 values over four dates including 2024-02-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 6,902,145 bytes.


### 2026-10-21 cadence batch 10
Added 91 accepted daily snapshots from 96 attempts, scanning through 2023-06-14. Archive: 109,892 observations / 846 accepted dates / 852 unique raw responses. Latest market date remains 2026-10-19. There are 410 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 846 accepted source files. Browser/Python parity passed for 13,216 values over four dates including 2023-08-23. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 7,560,963 bytes.
