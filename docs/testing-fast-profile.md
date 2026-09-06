# Fast local test profile

The default `make test` command remains the authoritative full suite and is
used by CI. `make test-fast` is an opt-in local feedback profile that excludes
tests marked `@pytest.mark.slow`.

The `slow` marker is registered under strict pytest marker validation. No test
is marked slow by this change: the profile is deliberately additive until a
test has a measured, repeatable reason to be classified. This prevents local
speed claims from being inferred from an unmeasured exclusion.

The fast profile must not be used for coverage, mutation, release, rights,
publication, or Conductor acceptance decisions. When slow tests are added,
record collected and executed counts for both profiles and keep the full suite
as the promotion gate.
