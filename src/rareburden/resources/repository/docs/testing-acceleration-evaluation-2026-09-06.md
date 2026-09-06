# Testing acceleration evaluation — 2026-09-06

This records the remaining bounded evaluation for GitHub issue #255. The full
suite remains the promotion gate; selective or accelerated execution is local
feedback only.

## Baseline evidence

On the owner-operated macOS environment, `make test-fast` completed 2,208
tests successfully. The full suite also completed 2,208 tests successfully in
67.97 seconds. No tests are currently marked `slow`, so the fast profile
currently has the same coverage as the full suite by construction.

`python -X importtime -c 'import rareburden'` completed successfully; the
reported `rareburden` import self-time was 2,096 microseconds in that process.
The existing bounded synthetic benchmark completed 10,000 iterations in
0.24140499999999998 seconds of process CPU time, below its 15-second ceiling,
with scientific output hash
`a22833dbe273df624861cb191e079287102e5fd6adec790191292a90b19564fd`.

## Decisions

| Proposal | Decision | Reason and boundary |
|---|---|---|
| `pytest-xdist` | Defer | No measured parallel bottleneck; file-mutating and resource-sensitive tests require a serial lane, so adding workers now would add unverified scheduling risk. |
| `pytest-testmon` | Defer | No dependency-aware database lifecycle is currently required; ordinary full tests remain authoritative. |
| `python -X importtime` | Evaluated, no change | Import timing was captured; no import-structure change is justified by this bounded measurement. |
| Scalene | Defer | Not installed in the locked development environment; no profiling claim is made. |
| `pytest-gremlins` | Defer | Existing mutation checks and ordinary tests are the promotion gates; no bounded target was identified that would add evidence without duplicating them. |
| `pytest-benchmark` | Defer | The existing benchmark emits a stable output hash and bounded CPU-time diagnostic; no brittle wall-clock assertion is added. |
| VCR.py | Defer | The repository uses deterministic in-process transports and has no approved public replay cassette set; credentials and restricted payloads must never be recorded. |
| `sysmon` coverage | Defer | Coverage plugins and branch coverage are part of the authoritative suite; no compatibility evidence supports changing the tracer. |
| Freezegun | Defer | Tests use explicit or local clocks where needed; global time freezing is not justified around concurrency. |
| `pytest-picked` | Defer | The fast profile already provides the required bounded local feedback without a second selection mechanism. |

These decisions preserve full CI, coverage, mutation, rights, disclosure,
publication, and Conductor gates. Any future adoption requires a new measured
comparison of collected/executed counts and failure behavior.
