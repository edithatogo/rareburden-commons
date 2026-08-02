# Panel review packet template

Use `schemas/panel-review-packet.schema.json` for repository-owned panel
preparation. Bind every packet to the exact reviewed commit and evidence
manifest SHA-256. Use synthetic or lawfully accessible evidence only.

The `accountable_gate_status` must remain `pending` unless a qualifying receipt
is attached outside the panel packet. `recommendation` records preparation
advice, not authority. Any dissent and unresolved finding must be retained.

The synthetic fixture at
`examples/fixtures/panel-review-packet-synthetic.json` is shape validation only;
its zero digests are deliberately not release evidence.
