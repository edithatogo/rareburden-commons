# Track 002 PanelApp and OECD frontier — 2026-08-16

## Disposition

The official UK and Australian PanelApp deployments are distinct national
curation contexts, not interchangeable samples of global coverage. The
instance registry records both and makes all completeness and representativeness
claims false.

The UK publisher's current `robots.txt` returns HTTP 200 and disallows `/api/`
for every user agent. Automated continuation of the earlier 129-of-433 detail
attempt is therefore disabled. The existing five-page private listing and its
receipt remain bounded historical observations; a publisher-authorized route is
required before any further automated UK API capture.

PanelApp Australia exposes a public listing API, reports 263 panels in the
bounded first-page observation, and returns HTTP 404 for `robots.txt`. No exact
content-reuse terms were located. The repository therefore permits only a
single-page, rate-limited, non-retained metadata/hash probe. Raw response and
per-version detail archival remain disabled.

OECD general terms permit extraction, copying, adaptation and distribution of
OECD-owned data with attribution unless dataset-specific or third-party rights
apply. The current API is SDMX-based and rate limited. The exact health dataflow
structure route is used only as a metadata canary; dataset values remain
disabled until the selected dataflow's source metadata, third-party interests,
citation, version and exact query are dispositioned.

## Executable boundary

`scripts/probe_panelapp_oecd_frontier.py` records response status, byte count,
SHA-256, content type and a minimal PanelApp count/page summary. It never writes
raw response bytes. The manually dispatched workflow allows only the two exact
metadata routes, sleeps before access, retains a receipt for 30 days and has no
schedule.

Stop on changed robots policy, HTTP 429, a redirect outside the named official
host, missing or changed terms, dataset third-party interests, or any request to
infer historical, country or global completeness. No observation activates a
source, estimand, diagnostic use or public raw mirror.
