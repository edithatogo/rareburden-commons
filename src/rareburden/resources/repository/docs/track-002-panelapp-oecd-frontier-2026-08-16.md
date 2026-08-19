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

The publisher-authorized non-API alternative is the download menu on each
official panel page. The publisher documents TSV downloads for the current
panel and a user-selected previous version. This route is operator-triggered,
per-panel and non-automated: each obtained file must be hashed and registered,
and it cannot support a claim that every panel or every historical version was
captured. The NHS GMS signed-off resource is a distinct corpus and is not a
substitute for PanelApp history.

PanelApp Australia exposes a public listing API, reports 263 panels in the
bounded first-page observation, and returns HTTP 404 for `robots.txt`. No exact
content-reuse terms were located. The repository therefore permits only a
single-page, rate-limited, non-retained metadata/hash probe. Raw response and
per-version detail archival remain disabled.
The supporting Australian Genomics resource calls the service an open online
platform, while its separate website terms require permission for use of site
intellectual property. Neither statement is an exact licence for PanelApp
content. The public download control and API therefore establish access
mechanics only, not redistribution or unattended bulk-automation rights.

OECD general terms permit extraction, copying, adaptation and distribution of
OECD-owned data with attribution unless dataset-specific or third-party rights
apply. The current API is SDMX-based and rate limited. The exact health dataflow
structure route is used only as a metadata canary; dataset values remain
disabled until the selected dataflow's source metadata, third-party interests,
citation, version and exact query are dispositioned.
The exact public dataset page identifies OECD Health Statistics 2026, and the
2026 metadata index maps topics to definitions, sources and methods. It does
not establish that every selected series is wholly OECD-owned. Under the OECD
terms, the source tab must be checked at the selected series/indicator level;
until that is recorded, values and derived outputs remain disabled while
metadata hashes may be retained.

The evidence-bound observations and response hashes are in
`docs/track-002-panelapp-oecd-terms-matrix-2026-08-16.json`. A page hash proves
what was observed at that time, not a perpetual licence grant.

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
