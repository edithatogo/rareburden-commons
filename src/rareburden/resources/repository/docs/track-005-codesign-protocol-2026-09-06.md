# Track 005 co-design, accessibility and compensation protocol

Status: pre-collection planning document only (2026-09-06). No participant has
been engaged, no consent has been collected, no ethics approval exists, no
compensation funding is secured and no survey collector is implemented. This
document supplies the documented protocol that the amended Track 005 completion
criterion 5 requires to exist before any use of the survey with people. It does
not report performed co-design and does not authorize collection.

Authority chain: Route A adoption and the criterion 5 amendment are recorded in
the [Track 005 completion decision](track-005-completion-decision-2026-09-05.md)
and the [owner completion disposition](decisions/2026-09-05-track-005-owner-completion-disposition.yml).
The corrected gate semantics are documented in the
[survey core protocol](economic-survey-core-protocol.md): the fail-closed gate
validates caller-declared prerequisites and always returns
`collection_authorized: false`.

## 1. Non-claims

- No community co-design, lived-experience participation, community
  representation, consent or endorsement exists or is claimed. The simulated
  panel in [track-005-agent-panel-review-2026-09-05.yml](track-005-agent-panel-review-2026-09-05.yml)
  is not participation.
- Permission to write this plan is not consent, compensation or approval to
  collect data.
- Nothing here changes the fail-closed collection gate, the deferred Route A
  boundary, the archived track state or any owner-disposition claim.

## 2. Co-design process (to be executed only when funded and resourced)

1. **Partner identification.** Engage accredited patient advocacy
   organisations, per the [data gap plan](economic-data-gap-plan.md) Phase 2.
   Partners are named in a dated revision of this protocol before any
   recruitment.
2. **Composition.** Lived-experience participants (patients, family
   caregivers, siblings where relevant), an independent facilitator and a
   methods advisor. Participant roles are recorded; no participant is counted
   as representing a community.
3. **Sessions.** Structured workshops over the five core domains of the
   [RBC-P001D survey core](track-005-rbc-p001d-protocol.md) and the reference
   items in `src/rareburden/economic_survey.py`: comprehension, cultural fit,
   response burden, and whether each item asks what participants would ask.
   The reference core is a starting draft, not a fixed instrument; items may
   be added, removed or reworded.
4. **Versioning.** Outcomes are recorded as a new dated survey-core revision
   with provenance per change. The reference core remains bound to its
   historical evidence; it is not silently rewritten.
5. **Dissent.** Disagreement is recorded verbatim with the participant's
   disposition requested. Unresolved items stay open; they are never silently
   resolved.
6. **Attribution.** Contributions are attributed with permission; anonymous
   contribution is supported. Attribution statements appear in the revision
   record.

## 3. Accessibility and linguistic adaptation plan

- Plain-language rewrite pass with a documented readability target and review.
- Cognitive pretesting (for example think-aloud interviews) before any wider
  use.
- Accessible formats: screen-reader compatible digital forms, large print,
  low-bandwidth alternatives, and non-digital options where partners require.
- Translation and cultural adaptation with independent back-translation
  review; currency brackets, household composition and caregiver-role wording
  are reviewed per locale.
- The plan must be marked approved by partners before it can be declared in a
  gate authorization packet (`accessibility_and_adaptation_plan.approved`).

## 4. Compensation schedule structure

- Co-design time is paid work. An hourly rate is set before recruitment, with
  an explicit three-letter uppercase currency code and a positive finite rate,
  mirroring the gate's `participant_remuneration` requirements.
- Payment method and timing, tax responsibility, and travel or childcare
  reimbursement are documented per engagement.
- No unpaid labour: a session without confirmed compensation terms does not
  proceed. This mirrors the gate's rejection of uncompensated community
  labour.
- Advisory input and co-design participation are both compensated; neither is
  volunteered labour.

## 5. Consent for design participation and withdrawal

- Design-phase consent covers workshop participation, note-taking and
  quotation permissions only. It is distinct from any future research
  data-collection consent and never substitutes for it.
- Withdrawal is supported at any time. Contributions are removable on request
  until the revision record is published, after which corrections are made by
  dated erratum.
- Design-phase material is never reused as survey response data.

## 6. Ethics, custodian and gate-field prerequisites

The gate checks these caller-declared fields. None exists today.

| Gate field | Requires | Supplied by | When |
| --- | --- | --- | --- |
| `hrec_irb_approval_id` | Institutional human research ethics approval reference for the collection study | HREC / IRB | Before any collection |
| `informed_consent_protocol` | Consent and withdrawal protocol for data collection | Study team with partners | Before any collection |
| `participant_remuneration` | `compensated: true`, positive finite `rate_per_hour`, explicit currency | Funder | Before recruitment |
| `accessibility_and_adaptation_plan` | Approved plan (Section 3) | Partners and owner | Before recruitment |
| `custodian_authorization` | Data custodian agreement id | Data custodian | Before any collection |

Supplying these fields can at most yield `gate_status:
"prerequisites_declared"`. `collection_authorized` remains `false`; a new
owner disposition plus an implemented and governed collector would still be
required before any collection.

## 7. Stop triggers

- Any recruitment or collection attempt before ethics approval, compensation
  funding and a custodian agreement exist.
- Any unpaid contribution session.
- Any claim that this document constitutes performed co-design, community
  endorsement or collection authorization.
- Any instrument change without recorded provenance and a dated revision.
