# Track 003 exact package and reproduction plan

Status: candidate preparation. No retained governed reference execution or owner
decision is recorded by this plan. Routine code/test/PR work remains authorized.

## Bound scope

`scripts/track003_reference_package.py` prepares a content-hashed manifest binding
the eighteen assumed inputs, complete Python implementation, environment lock,
source applicability evidence, twelve scenario contexts, seed 20260830 and
10,000 iterations. No article data become model inputs. The historical one-output
disposition is neither rewritten nor extended.

The exact candidate produces three files: `reference-results.json`,
`reference-report.md` and `reference-tables.csv`. Each is synthetic. Calculation
claim flags describe what the mathematics does not authorize; a separate owner
decision and execution receipt are required to establish permission and execution.
Original code, inputs, metadata and the approved synthetic package may be retained
through the authorized public Git workflow. This is public repository distribution,
not a production release, DOI registration, external deployment or clinical use.

## Exact decision

After code checks and advisory review, bind the candidate commit/tree and raw
manifest SHA-256 in the standard agent-owner decision packet. Present two options:
accept this execution/retention/reproduction scope, or defer/revise it. Preserve
uncertainty and the governance-interpretation dissent. Owner decision remains
pending unless attributable direction supports this exact decision; agents must
not fabricate an unseen candidate selection or a decision timestamp.

The command rejects pending decisions, non-acceptance, different candidate hashes,
modified input/code/plan files and a checkout not at the exact candidate commit.
It refuses an existing output directory. It does not fetch data or contact any
external source. Run only after the accountable disposition is recorded.
Imported implementation roots must match the verified checkout. The decision
bytes are captured once and checked again before retention; code, manifest and
Git identity are revalidated after calculation and before output creation.
Decision validation requires the exact track, unique options, a valid selected
acceptance option and a real UTC timestamp. The two-copy retention limit remains
an operational rule, not a global execution counter enforced by the command.
The runtime gate requires the actual Python 3.13 interpreter in this checkout's
`.venv` and a read-only, offline `uv sync --check --frozen --extra dev` check
against its locked dependencies before calculation and publication. UV environment
overrides are removed from that check. All three files are written and fsynced
in a temporary sibling, then published by a single directory rename after final
revalidation. A sibling exclusive lock coordinates command writers. An interrupted
hidden staging directory or lock is not a completed package: inspect and recover
that exact temporary path before retrying; never treat a partial write as success.

## Execution and separate reproduction

1. Create a clean detached worktree at the exact candidate commit; verify the
   manifest, owner packet and panel receipts. Keep the decision outside that
   checkout so its later recording does not change candidate identity.
2. Use `uv sync --frozen --extra dev --python 3.13` in the clean checkout.
3. Execute `uv run python -m scripts.track003_reference_package --decision
   /absolute/path/to/decision.json --output /absolute/path/to/new-output-directory`.
4. Retain the printed candidate/decision and output digest receipt, not just an
   exit code. Check the exact three-file inventory and inspect report/table
   labels, partitions, interval definitions, unknown scope and source limitations.
5. In a separate clean worktree/environment at the same candidate, run the same
   command into a second new directory. Compare all three file SHA-256 values
   exactly. This is separately executed owner-operated reproduction, not
   independent review or external scientific validation.
6. The approved retention inventory is one three-file package plus this separate
   reproduction copy; do not create additional retained analytical variants.
   Review outputs and reproduction evidence before a scoped public-package PR.
7. Record final panel findings/disposition and all original acceptance criteria
   before completing or archiving Track 003. Held empirical sources, missing
   service-use rates and source-rights gaps remain explicitly separate.

Fixture tests may render in-memory reports to test presentation without creating
a governed output directory. Fixtures do not count as an approved execution,
empirical validation, public analytical package or completed demonstrator.
