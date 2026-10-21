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

Batch 6 publication verified: GitHub main data commit 3ea012c; all 491 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source a87bd869c6a5fc2e763b040926c162152d8af3ee deployed successfully as appgdep_6ad7d87fc4f08191a07b959ca4cead66. Browser horizon/sector/CAGR/CSV/mobile suite passed. Next cadence continues before 2025-01-01; 794 weekday candidates remain unchecked/retryable.


### 2026-10-21 cadence batch 7
Added 91 accepted daily snapshots from 96 attempts, scanning through 2024-08-12. Archive: 80,357 observations / 577 accepted dates / 582 unique raw responses. Latest market date remains 2026-10-19. There are 698 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity passed; browser/Python parity passed for 13,636 values over four dates including 2024-10-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 5,554,331 bytes.

Batch 7 publication verified: GitHub main data commit b18ba9f; all 582 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source dcb11167ab5fcc897e3c5887cecc2e3b56eef622 deployed successfully as appgdep_6ad7df6ff0b081919d3b4366b50debe1. Next cadence continues before 2024-08-12 with max-requests96, same delay/stop rules; 698 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 8
Added 88 accepted daily snapshots from 96 attempts, scanning through 2024-03-22. Archive: 90,432 observations / 665 accepted dates / 671 unique raw responses. Latest market date remains 2026-10-19. There are 602 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 665 accepted source files. Browser/Python parity passed for 13,384 values over four dates including 2024-06-04. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 6,240,060 bytes.

Batch 8 publication verified: GitHub main data commit 9f47bbf; all 671 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 305d63591102bd129424ca67723c2dbcf8af5bb3 deployed successfully as appgdep_6ad7e6742a5c8191a3c2da9ce62f9a65. Next cadence continues before 2024-03-22 with max-requests96, same delay/stop rules; 602 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 9
Added 90 accepted daily snapshots from 96 attempts, scanning through 2023-11-03. Archive: 100,167 observations / 755 accepted dates / 761 unique raw responses. Latest market date remains 2026-10-19. There are 506 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 755 accepted source files. Browser/Python parity passed for 13,272 values over four dates including 2024-02-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 6,902,145 bytes.

Batch 9 publication verified: GitHub main data commit 9aa3f99; all 761 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 47bd6c94f407fcd496657454223a0f8a5e503899 deployed successfully as appgdep_6ad7ed7e4bf4819196b7da18ade68922. Next cadence continues before 2023-11-03 with max-requests96, same delay/stop rules; 506 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 10
Added 91 accepted daily snapshots from 96 attempts, scanning through 2023-06-14. Archive: 109,892 observations / 846 accepted dates / 852 unique raw responses. Latest market date remains 2026-10-19. There are 410 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 846 accepted source files. Browser/Python parity passed for 13,216 values over four dates including 2023-08-23. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 7,560,963 bytes.

Batch 10 publication verified: GitHub main data commit 63becba; all 852 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 5ac2738772774cfd47adb38974db367dd596f3fc deployed successfully as appgdep_6ad7f48221dc819188ce2354597d77e8. Next cadence continues before 2023-06-14 with max-requests96, same delay/stop rules; 410 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 11
Added 89 accepted daily snapshots from 96 attempts, scanning through 2023-01-24. Archive: 119,272 observations / 935 accepted dates / 941 unique raw responses. Latest market date remains 2026-10-19. There are 314 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 935 accepted source files. Browser/Python parity passed for 13,188 values over four dates including 2023-04-20. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 8,195,372 bytes.

Batch 11 publication verified: GitHub main data commit 3d64ffc; all 941 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source e790588b38ed90bde423efc4cea93167a0b6b2d4 deployed successfully as appgdep_6ad7fba52e08819186b17c987fbbe7ec. Next cadence continues before 2023-01-24 with max-requests96, same delay/stop rules; 314 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 12
Added 93 accepted daily snapshots from 96 attempts, scanning through 2022-09-06. Archive: 128,920 observations / 1,028 accepted dates / 1,035 unique raw responses. Latest market date remains 2026-10-19. There are 218 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 1,028 accepted source files. Browser/Python parity passed for 13,104 values over four dates including 2022-11-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 8,858,203 bytes.

Batch 12 publication verified: GitHub main data commit 5681800; all 1,035 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 8fd2c7ba1e6023db26fa4340e3074dc5e61f27de deployed successfully as appgdep_6ad8028ea2b08191a758d6387d1a390d. Next cadence continues before 2022-09-06 with max-requests96, same delay/stop rules; 218 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 13
Added 92 accepted daily snapshots from 96 attempts, scanning through 2022-04-18. Archive: 138,030 observations / 1,120 accepted dates / 1,127 unique raw responses. Latest market date remains 2026-10-19. There are 122 unchecked or retryable weekday candidates; full daily history and weekend sessions remain incomplete. SQLite integrity and requested/embedded date agreement passed for all 1,120 accepted source files. Browser/Python parity passed for 12,964 values over four dates including 2022-07-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 9,505,508 bytes.

Batch 13 publication verified: GitHub main data commit b7367db; all 1,127 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 7ff3689b00fbca3d53a9def58ac70d56a1189959 deployed successfully as appgdep_6ad809a234748191947e927debdb715b. Next cadence continues before 2022-04-18 with max-requests96, same delay/stop rules; 122 weekday candidates remain unchecked/retryable. Latest market snapshot remains 2026-10-19. No source code changes; continue data integrity, requested/embedded date agreement and browser parity verification. Full exchange-calendar/weekend audit and cloud refresh remain incomplete.


### 2026-10-21 cadence batch 14 — weekday discovery finished
Ran bounded batches of 96 and 26 requests, accepting 91 and 24 snapshots (115 total). All 1,305 weekday candidates from 2021-10-19 through 2026-10-19 are checked: 1,235 accepted dates and 70 recorded unavailable/rejected responses; zero unchecked/retryable candidates. Missing files do not prove holidays. Archive: 148,914 observations / 1,235 accepted dates / 1,243 unique raw responses. Latest market date remains 2026-10-19. Full daily history remains unverified until weekend/special-session coverage and recorded gaps are audited. SQLite integrity and requested/embedded date agreement passed for all 1,235 accepted source files. Browser/Python parity passed for 12,908 values over four dates including 2022-02-15. All seven requested horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Compact dashboard: 10,281,340 bytes. Next work: audit weekend/special sessions against official sources, investigate recorded gaps as needed, preserve honest coverage states; no additional product features. Cloud refresh remains incomplete; hosted Site is still a fixed publication snapshot.

Batch 14 publication verified: GitHub main data commit c240852; all 1,243 staged raw SHA-256 checks and SQLite backup integrity passed. Owner-private Sites source 20765c8153e0d5c7bc84121c52bbcf89eccead05 deployed successfully as appgdep_6ad810def0488191ae2312fbc7476e10. Weekday discovery finished: zero unchecked/retryable candidates. NEXT: audit weekend and special trading sessions using official sources and reconcile 70 recorded weekday gaps without assuming holidays from missing responses. Do not rerun an empty weekday pass or claim complete daily history yet. Retain all downloaded bytes and consistent database in public GitHub, maintain owner-private publication, verify dates and browser/Python parity on added sessions. Latest market snapshot remains 2026-10-19. Full session-calendar audit and cloud refresh remain incomplete; hosted publication is a fixed snapshot. No new product features.


### 2026-10-21 cadence batch 15 — verified special sessions
Added six official-notice-backed weekend sessions: 2023-11-12, 2024-01-20, 2024-03-02, 2024-05-18, 2025-02-01 and 2026-02-01. All six files accepted, adding 706 observations. Explicit session manifest special-sessions.json records official notice URLs and partial-audit scope; --sessions uses separate special-backfill.json ledger, existing date validation, bounded requests, resume and rate-limit stop rules. Added meaningful tests for duplicate/out-of-range explicit dates, weekend ingestion/resume and wrong embedded date rejection/archive. 21 Python tests passed (13 pipeline/backfill + 8 history). Archive: 149,620 observations / 1,241 dates / 1,249 raw responses. Source-date agreement passed for all 1,241 accepted files. Browser/Python parity: 14,252 values across four dates including 2026-02-01; all horizons, 167 indices, 34 sectors, CAGR, missing history, CSV and mobile checks passed. Dashboard: 10,331,421 bytes. Weekday gaps70 and remaining special-session/calendar audit are unresolved; no complete-daily-history claim. Latest date remains 2026-10-19; hosted publication remains a fixed snapshot.

Batch 15 release complete: GitHub main b6bb3f3; all 1,249 staged raw blobs matched SHA-256; SQLite backup integrity passed. Private Sites source 9662a5d4004c9b7e4487c46077d2677eb2f3de84 deployed successfully as appgdep_6ad817f8fc28819194f98d5df1f7a002. Next: continue official annual calendars 2021–2026 and ad-hoc closure/session notices to reconcile70 weekday gaps and find any additional weekend sessions; six verified sessions are not an exhaustive calendar. Annual2023 notice https://archives.nseindia.com/content/circulars/FAOP54759.pdf and May2024 notice https://nsearchives.nseindia.com/content/circulars/MSD61893.pdf have been inspected. Use --sessions manifest rather than empty weekday pass. Full session audit remains incomplete; no complete daily-history claim. work/verify-staged.py now uses Git cat-file batch for efficient full staged-byte verification. No new features outside requested scope.


### 2026-10-21 cadence batch 16 — weekday gap reconciliation
Reconciled all 70 non-CSV weekday responses against explicit official calendar evidence. 69 match verified NSE capital-market closures; 2024-01-22 remains pending direct-notice verification (CMTR60338 unavailable in web tool, corroborated by NSE-hosted issuer filing). Saved calendar-evidence.json with date-level source URLs, evidence type and scope, and data/calendar-audit.json generated by audit_calendar.py. The June2023 holiday amendment is applied: June29 closed, June28 accepted. Muhurat sessions with accepted files are not called closed. Four new tests prevent missing-file/holiday inference, accepted-date conflicts, duplicate evidence and mixing pending with verified states. 17 pipeline/backfill/audit tests passed; existing8 history tests unchanged (25 total). No market observations or dashboard assets changed: 149,620 observations / 1,241 dates / 1,249 raw files. Existing private publication remains current. Direct Python PDF downloads timed out with no bytes obtained; official pages/notices inspected using web tools; evidence JSON records this limitation. Remaining: resolve direct Jan22 notice, exhaustively audit special/weekend sessions and session coverage; no claim complete daily history.
