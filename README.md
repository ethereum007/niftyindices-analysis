# NIFTY Indices Analysis

Index Intelligence: an automated official-report downloader, checksum-addressed raw archive, SQLite warehouse and interactive index performance/valuation dashboard.

## Contents

- `nifty-automation/`: Python download, validation, storage and report pipeline; tests and backfill utility.
- `nifty-automation/data/raw/`: original published source CSV files, named by SHA-256.
- `nifty-automation/data/warehouse.sqlite`: consistent SQLite snapshot containing observations and source-batch provenance.
- `nifty-automation/data/reports/`: generated HTML, JSON and CSV reports.
- `index-intelligence/`: dashboard template, generator and deployable static output.

## Run locally

Python 3.10 or newer; no external Python dependencies.

```sh
python nifty-automation/pipeline.py
python index-intelligence/build_dashboard.py
python -m unittest discover -s nifty-automation -v
```

Open `nifty-automation/data/reports/dashboard.html` directly. Downloading rebuilds that file and `index-intelligence/dist/index.html`. The local Windows schedule is not installed merely by cloning this repo. The private hosted Site is a publication snapshot, not cloud-synced to the PC.

## Data and interpretation

Source: [NSE Indices daily reports](https://niftyindices.com/reports/daily-reports). Each accepted source file is archived with its retrieval timestamp, original URL, observation date and checksum in `batches`. The database is backed up through SQLite's backup API so WAL activity does not create an inconsistent Git snapshot.

Five-year source-file discovery is finished for every calendar date from 19 October 2021 through 19 October 2026. All 1,827 dates were checked: 1,241 accepted snapshots and 586 recorded unavailable responses, with zero unchecked or retryable candidates. Date-level results are in `data/coverage-audit.json` and the weekday/special ledgers. This certifies file discovery, not completeness of the exchange calendar or history of every index. Index availability varies by date; unavailable horizons remain N/A. No historical index membership is inferred from today's constituents.

Indices include different return variants and asset types. India VIX is volatility, not an equity return. Inverse, leveraged, fixed-income, currency and futures variants are separated in the dashboard. Valuations alone are not investment recommendations.

Source attribution does not grant ownership of third-party data or establish a redistribution licence. No proprietary vendor feed, subscription dataset, credentials or personal customer records are included. This repository has no blanket licence for third-party data.

## Five-year / all-sector release

167 published indices, including all 34 current sectoral catalogue entries. Rank and chart MTD, 3M, 6M, 1Y, 2Y, 3Y and 5Y (plus 1M/daily). Cumulative returns and annualized CAGR are explicitly separate. Available source history determines horizon coverage; newer indices remain listed with N/A. Calendar periods use actual disclosed baselines within 7 days of the requested anniversary; MTD uses the previous month-end.

Current archive: 1,241 accepted snapshot dates and 149,620 observations, from 19 October 2021 through 19 October 2026. Every calendar date in the five-year window was checked; unavailable source files and shorter index histories remain unfilled. There are 1,251 raw responses, including ten rejected responses. The extended matrix is `nifty-automation/data/reports/performance-latest.csv`.

Validation: 29 Python tests plus browser checks for periods, complete sector list, all-index default, comparison, CAGR and mobile. Automated browser download saving was canceled by the browser environment; generated CSV content is independently validated.

Daily history can be expanded with `python nifty-automation/backfill_daily.py --max-requests 96`. It resumes without redownloading accepted files, records non-CSV/HTTP/error results and stops on access denial or rate limits. Browser/Python return parity passed for 14,252 values over four dates. The compact publication is approximately 10.3 MB; original observations remain in the source archive and database.

Weekday discovery pass finished: all 1,305 weekday candidates in the five-year window checked; 1,235 accepted dates and 70 recorded gaps. Weekend discovery is now finished too; see the completed coverage audit below.

Six verified weekend sessions are included. Run `python nifty-automation/backfill_daily.py --sessions nifty-automation/special-sessions.json --max-requests 96` to resume the explicit manifest using its separate ledger. Official notice links and partial-audit scope are saved in that manifest.

Weekday gaps are reconciled in `nifty-automation/data/calendar-audit.json`: 69 directly verified exchange closures and one separately labelled corroborated closure. Evidence URLs are saved in `calendar-evidence.json`; `python nifty-automation/audit_calendar.py` regenerates the audit and fails if closure evidence conflicts with an accepted date. This does not yet establish an exhaustive session calendar.

Exhaustive weekend file discovery uses `--sessions nifty-automation/weekend-candidates.json --max-requests 96`. The 522-date manifest records candidates, not declared trading sessions; zero remain unchecked after all discovery batches. Non-CSV responses do not prove exchange closure.

## Completed five-year discovery audit

All 1,305 weekday and 522 weekend candidates checked. Six official-notice-backed weekend sessions are included. The 70 unavailable weekdays reconcile to 69 directly verified closures and one separately labelled corroborated closure. All other unavailable responses remain unavailable-file states; no holiday is inferred from absence. All 29 Python tests, 14,252 browser/Python comparisons, requested-horizon/sector/CAGR/CSV/mobile checks, raw checksums and consistent backup integrity passed. Dashboard coverage labels show the exact audited range. The private hosted dashboard is still a published snapshot; automatic local downloads require the scheduled Windows PC task.
