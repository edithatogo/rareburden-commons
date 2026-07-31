# Track 004 independent synthetic execution record

**Scope:** local synthetic fixture only; no network, persistence, custodian, or
controlled data.

**Procedure:** a second invocation of `uv run make node-reproducibility` was run
after the package/runtime checks. Both serialised outputs matched byte-for-byte;
the command reported `Synthetic node reproducibility passed`.

**Observed controls:** multi-diagnosis fixture included; small cell suppressed;
participant-field negative test passed; manifest and lockfile fingerprints were
present; no credentials or host paths were emitted.

This is repository evidence of repeatability, not independent custodian execution
or pilot approval.
