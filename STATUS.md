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
