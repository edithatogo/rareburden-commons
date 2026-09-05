# Patient and family economic and social burden survey protocol

## 1. Purpose and scope

This document defines the core survey protocol and governance boundaries for assessing patient and family economic and social burden in rare diseases under RareBurden Commons (RBC-P001D).

## 2. Core survey domains

1. **Direct healthcare out-of-pocket costs:** specialist gap fees, unlisted medications, non-reimbursed diagnostics, and allied health.
2. **Direct non-medical costs:** specialized travel, accommodation for distant tertiary centre visits, home and vehicle modifications.
3. **Caregiver and household time:** hours per week dedicated to care coordination, medication administration, physical therapy, and daily assistance.
4. **Productivity and career impact:** employment withdrawal, reduction in hours, missed promotions, early retirement, and absenteeism.
5. **Education and development:** school absences, home schooling needs, educational aides, and developmental therapies.

## 3. Co-design and community labour safeguard

Actual survey administration is deferred under Route A. When funded and resourced, survey implementation must satisfy:

- **Attributable co-design:** survey questions must be reviewed and refined with representative patient organisation leaders.
- **Fair compensation:** lived-experience contributors must be compensated at standard consultative rates; uncompensated community labour is strictly prohibited.
- **Linguistic and accessibility adaptation:** plain language, accessible digital formats, and translated instruments across diverse linguistic communities.

## 4. Executable fail-closed collection gate

The codebase provides `rareburden.economic_survey.check_collection_gate`, which fails closed unless cryptographically bound approvals exist for:
1. Institutional HREC / IRB approval identifier.
2. Participant consent and withdrawal protocol.
3. Verified remuneration schedule.
4. Accessibility and translation audit.
5. Data custodian agreement.
