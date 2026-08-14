# Conductor and GitHub issue reconciliation

Snapshot date: 2026-08-15  
Repository revision audited: `3e746bc` (merged PR #49)  
Issue range: #2–#16

## Authoritative status

The repository-native roadmap validator reports 18 valid tracks across 10
releases. The current status remains:

- archived: Tracks 001, 006 and 018;
- in review: Tracks 002 and 007;
- blocked: Tracks 003, 004, 005, 008, 009, 010, 011, 012 and 013;
- planned: Tracks 014, 015, 016 and 017.

No track was promoted or closed during this reconciliation. Repository-owned
preparation is substantial, but unchecked acceptance tasks and qualifying
external or independent gates remain.

## Issue synchronization rule

Issues #2–#16 are execution mirrors, not an alternative source of truth. Their
bodies and status labels must agree with each track's `plan.md`, `metadata.json`
and `review.md`. A checked repository task does not satisfy a source-rights,
scientific, patient/community, custodian, independent-operator, security or
release-authority receipt unless the qualifying evidence is recorded.

## Dependency sequence

1. Close Tracks 002 and 007 only after their remaining exact-source,
   registration, screening and accountable review evidence is received.
2. Complete and freeze Track 008 after 002 and 007.
3. Complete and freeze Track 009 after 002 and 008.
4. Complete and freeze Track 010 after 009.
5. Complete Tracks 003 and 011 after 008–010; complete Track 004 after 009–010;
   complete Track 005 after 009–010.
6. Complete Track 012 after 004, 005 and 008–010.
7. Complete Track 013 after 003, 005, 007, 010, 011 and 012.
8. Complete Track 014 after 002, 009, 010 and 013; complete Track 015 after
   006, 007 and 013.
9. Complete Track 016 after 004 and 014.
10. Complete Track 017 after 013–016 and only then consider a stable release.

## Integrity compatibility note

`uv run make validate-roadmap` is the repository's normative validator and
passes. The separately installed generic Conductor validator currently reports
the table-based `conductor/tracks.md` entries as unregistered because it expects
list entries linking to per-track `index.md` files. This is a tooling-format
compatibility issue, not evidence that the roadmap tracks are absent. Migrating
the registry format should be handled as a separate, tested change so that it
does not silently alter the established programme contract.
