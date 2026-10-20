# NIFTY automatic reports â€” working local foundation

Python 3.10+, no external dependencies. No database credentials needed.

## Run

```powershell
python pipeline.py
```

Discovers published daily snapshot CSV links from the official daily reports page, downloads with bounded retries, archives original bytes, validates the entire batch, writes SQLite, then creates HTML, CSV and JSON reports. Reruns skip identical files. Revised files update observations while preserving original batches and raw files.

Open `data/reports/latest.html`. Run status is `data/last-run.json`; exit code 1 means failed or partial. If acquisition fails, existing reports retain their original observation date. Always inspect run status, not just report existence.

## Reports

- Latest published daily price-change rankings, with close and available valuations.
- 1M, 3M and 1Y price returns once enough history has accumulated or been imported.
- Explicit calendar-day return methodology and base dates in the JSON/CSV.
- Blank means unavailable. These are PRICE returns, not total returns; daily snapshots do not establish TRI coverage.

```powershell
python pipeline.py --file path/to/official-snapshot.csv
python pipeline.py --from-date 2026-10-01 --to-date 2026-10-19
python pipeline.py --report-only
python -m unittest -v
```

Backfill uses the observed public dated-file naming pattern, not an undocumented API. Weekends are excluded; holiday files can be absent and are reported as errors. A missing file is not interpreted as proof of a holiday. Range limit: 366 days. Normal discovery only collects links currently visible on the page; it does not guarantee full historical recovery.

## Storage

`data/raw/<sha256>.csv` holds originals, including files subsequently rejected by validation. `data/warehouse.sqlite` holds batches and index/date observations. Keep the entire data folder on persistent storage and back it up. A rejected CSV does not alter accepted observations. No production Supabase database has been selected or modified.

## Scheduling / deployment

`run.ps1` is a scheduler entry point. Proposed schedule: 19:00 IST every weekday with a later retry. Windows Task Scheduler task `NiftyIndices Daily Reports` is installed at 19:00 and 21:00 IST Monday–Friday, with catch-up when available and overlapping runs disabled. The second run is a delayed-publication check. The task runs in the current logged-in user session; this PC must be on and the user logged in. No notification channel is configured. Inspect data/last-run.json for errors. The computer must be awake for a local scheduler. For cloud operation, deploy the Python script on a worker with a persistent volume; do not use ephemeral storage without a durable database/object-store adapter. Run only one worker per data directory.

## Current verification limits

Live acquisition passed on 20 October 2026: the 16 and 19 October snapshots each loaded 167 indices (334 observations total). A second live run skipped both identical files. Six automated tests passed for batch validation, deduplication/revisions, return calculations, missing history and allowed URL discovery. Initial network probes failed; the production downloader subsequently succeeded. Existing HTML/CSV/JSON reports contain real published snapshot data. TRI and long historical horizons are not yet populated.

This is the first daily-snapshot pipeline, not the complete earlier report suite. TRI, historical valuations beyond stored snapshots, monthly factsheets, membership changes, SIF NAV comparisons, cloud storage and notifications require additional source adapters and report definitions. Existing public-free source restrictions and provenance should be preserved when integrating the earlier Supabase warehouse. Public download availability does not itself establish commercial redistribution rights.
