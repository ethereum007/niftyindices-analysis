# Release status

The extended dashboard is deployed at https://kiran-index-intelligence.kirandnyc.chatgpt.site (private). Code and the full requested source-data snapshot are stored in this public repository.

- 167 published indices; 34 sectoral entries.
- MTD, 3M, 6M, 1Y, 2Y, 3Y, 5Y rankings and charts, plus 1M/daily.
- Cumulative returns and annual CAGR are explicitly separate.
- 10,166 observations, 79 accepted dates, 81 archived raw responses (two are rejected responses).
- Historical coverage is monthly snapshots, specific return baselines and recent daily points, not full daily history.
- 14 automated tests and browser interaction checks passed. Generated CSV content and static CSV delivery verified; browser-managed blob saving was canceled in the test environment.

Local Windows data refresh is scheduled at 19:00 and 21:00 IST weekdays. The private hosted publication is a fixed snapshot and has no automatic cloud data connection yet. A 30-minute Codex continuation cadence is enabled to continue the scoped build, data coverage and operational improvements.

Next work: better ingestion-health reporting, bounded daily-history expansion, consolidation of working directories, and a verified durable cloud data-refresh path. Credentials and personal customer data remain excluded.

## Daily archive update — 21 October 2026

46 additional daily snapshots loaded: 17,714 observations over 125 accepted dates and 127 archived raw responses. Two requested dates returned non-CSV responses; they are recorded without assuming holidays. Bounded resume tool: nifty-automation/backfill_daily.py.

The dashboard uses a compact indexed payload and selected-snapshot calculations. Browser/Python parity passed for 11,067 values over four dates; 19 Python tests and browser interaction checks passed. Page size reduced from 6.6 MB to 1.2 MB. Five-year daily backfill is still incomplete; monthly samples plus expanding daily coverage remain explicitly disclosed.

The daily-history/compact-payload release is now published at the same private URL. Deployment succeeded from Sites source 6ffd6cb21fcb2b7c59c50f92e94c5ca624fa8eec. GitHub code/data commit: ba5ce91. All 127 Git source blobs retain their original checksums; the database snapshot passes integrity_check. Full five-year daily coverage and cloud data refresh remain incomplete.

## Daily-history batch 2

Added 46 accepted snapshots after checking another 48 weekday files. Current totals: 24,785 observations over 171 accepted dates; 174 archived raw responses. The backward daily scan reached 12 May 2026. Two requests in this batch returned non-CSV responses and are not declared holidays. The latest market snapshot remains 19 October 2026; this is historical expansion, not live-market freshness.

Batch 2 publication succeeded at the existing private dashboard URL. Source commit: 05b6d50cc30fcf8d99e7bc82980cce061b59b582. Data backup commit: b994231. All 174 raw-file hashes and SQLite integrity verified; browser/Python parity passed for 10,983 values over four snapshot dates, including newly added June observations. All requested horizon/sector/export/mobile checks passed. Daily five-year history remains incomplete; 1,130 weekday candidates still unchecked/retryable.

## Daily-history batch 3

### Daily-history batch 3

Checked another 48 weekday candidates: 42 accepted snapshots, six non-CSV responses. Current archive: 30,953 observations over 213 accepted dates; 216 raw responses. The backward scan reached 2 March 2026. The latest market snapshot remains 19 October 2026; full five-year daily history and special weekend sessions are not yet audited. Compact dashboard size: 2,141,140 bytes.

Batch 3 publication succeeded at the existing private URL from source 762590ebae4683ddc59dc3e757d1823ca2dac6c5. Data commit: 3e435f7. Raw source hashes (216) and consistent SQLite snapshot verified. Browser/Python parity passed for 10,752 values including newly added March data; horizon, sector, export and mobile checks passed. Full five-year daily coverage remains incomplete; 1,082 weekday candidates still unchecked/retryable.

## Daily-history cadence batch 4

### Daily-history cadence batch 4

Two bounded batches checked 96 weekday candidates: 91 accepted snapshots and five non-CSV responses, with no rate-limit/access stop. The daily scan now reaches 9 October 2025. Current archive: 44,012 observations over 304 accepted dates; 308 archived raw responses. The dashboard is 3,049,129 bytes. Full five-year daily coverage and weekend sessions remain unaudited. Latest snapshot date is still 2026-10-19; this is historical expansion.

Batch 4 publication succeeded at the existing private URL from source 8e0047272972d39ead5c5c6633e76bc3c363bfac. Data commit: fed0a04. All 308 raw-file hashes and consistent SQLite integrity verified. Browser/Python parity passed for 14,224 values, including prices, valuations and source hashes as well as returns/CAGR; horizon, sector, CSV and mobile checks passed. Full five-year daily coverage remains incomplete, with 986 weekday candidates unchecked/retryable and special weekend sessions unaudited.

## Daily-history cadence batch 5

### Daily-history cadence batch 5

Checked 96 weekday candidates: 93 accepted snapshots, three non-CSV responses, no access/rate-limit stop. Backward daily scan reached 21 May 2025. Archive now has 57,080 observations over 397 accepted dates and 401 raw responses. Compact dashboard size is 3,953,729 bytes. Latest market snapshot remains 2026-10-19; full daily five-year coverage and weekend-session audit remain incomplete.

Batch 5 publication succeeded at the existing private URL from source c7f3996fc66e7a8ebc2ea6a10c563c1c98c8ffc3. Data commit: 160e0a2. All 401 raw source-file hashes and consistent SQLite integrity verified. Browser/Python parity passed for 14,140 values including newly added July 2025 data; horizon, sector, CSV and mobile checks passed. Five-year daily history remains incomplete, with 890 weekday candidates unchecked/retryable and special weekend sessions unaudited.


### 2026-10-21 cadence batch 6
Added 89 accepted daily snapshots from 96 attempts, scanning through 2025-01-01. Archive: 69,122 observations / 486 accepted dates / 491 unique raw responses. Latest market date remains 2026-10-19. There are 794 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity passed; browser/Python parity passed for 14,028 values over four dates including 2025-03-03. Compact dashboard: 4,790,623 bytes.
