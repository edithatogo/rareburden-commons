# WHO ICD duplicate snapshot preservation and idempotency correction

**Purpose:** Preserve the provenance of two equivalent authenticated inventory
runs and prevent future timestamp-only duplication.

## Preserved runs

Two successful runs observed the same 24 top-level WHO ICD API resources but
uploaded them under retrieval-time paths:

- owner-operated local run at `2026-08-15T15:42:11Z`, private Hugging Face
  commit `e88f22d227471b7e421f6e661641c5b32535c67d`;
- GitHub Actions run `31893767934` at `2026-08-15T15:48:52Z`, private Hugging
  Face commit `44db5cf13b0faa6e7a0d021344080a806e63980b`.

Both are retained as truthful provenance. Neither is deleted or rewritten.
They are separate retrieval events, but their endpoint/status/size/SHA-256
observation identities are equivalent.

## Future behavior

`scripts/archive_who_icd_inventory.py` now calculates a snapshot SHA-256 from
the API version, scope and ordered endpoint observation identities while
excluding the retrieval timestamp. Before upload it checks existing private
WHO ICD manifests for the same fingerprint. An equivalent snapshot is reused
and its existing repository revision and path are recorded. A new snapshot is
stored under `licensed-private/who-icd/by-snapshot/<sha256>/` only when its
content identity differs.

This correction does not equate different retrieval times. Each public
metadata manifest retains its own observation timestamp; deduplication applies
only to private response-byte storage.

An owner-operated verification at `2026-08-15T16:02:27Z` calculated snapshot
SHA-256 `f174b234fe278ad2286ff3d583a508350517c5aa4c84078210aaef43bef65084`,
reused the first run's existing path, and left the private repository revision
unchanged at `fda6820164c16e5ce8843e6415180e67da754014`. No third equivalent copy was
uploaded.
