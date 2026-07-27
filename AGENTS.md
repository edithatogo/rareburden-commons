# Instructions for human and AI contributors

Before changing this repository:

For the portable autonomous handoff branch, also read `docs/handoff/implementation-status.md` and `docs/handoff/CODEX_AUTONOMOUS_CONTINUATION.md` before changing code, Git history or GitHub configuration.

1. Read `conductor/index.md`, `conductor/product.md`, `conductor/tech-stack.md`, `conductor/workflow.md` and `conductor/roadmap.yml`.
2. Read the active track's `spec.md`, `plan.md` and `metadata.json`.
3. Work only on a defined task, update its checkbox and make a focused Git commit.
4. Do not mark a track Complete without passing acceptance criteria and adding `review.md`.
5. Preserve provenance: every external datum identifies source, release/version, retrieval event, licence and transformation.
6. Never add participant-level, row-level, small-cell or controlled data to public Git.
7. Distinguish observed data, transformed parameters, modelled estimates and assumptions in every output.
8. Do not imply endorsement, access or partnership without written confirmation.
9. Prefer open standards, portable code and analyses that can run behind a custodian firewall.
10. Run `make check` before committing and ensure programme validation remains offline.
11. Do not describe a planned capability as implemented merely because its specification exists.

Where documents conflict, the active track specification governs the task; project-level Conductor context and the stable-v1 acceptance contract govern everything else.
