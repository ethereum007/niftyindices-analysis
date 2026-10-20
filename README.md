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

Historical ingestion is in progress. Initially this includes monthly historical snapshots from October 2021 onward plus additional baseline and recent daily observations; it is not complete daily history. Missing source files, rejected data and gaps are recorded in `history-backfill.json`. Index availability varies by date; unavailable horizons must remain N/A. No historical index membership is inferred from today's constituents.

Indices include different return variants and asset types. India VIX is volatility, not an equity return. Inverse, leveraged, fixed-income, currency and futures variants are separated in the dashboard. Valuations alone are not investment recommendations.

Source attribution does not grant ownership of third-party data or establish a redistribution licence. No proprietary vendor feed, subscription dataset, credentials or personal customer records are included. This repository has no blanket licence for third-party data.
