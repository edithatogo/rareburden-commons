# Track 002 ontology-portal archival frontier — 2026-08-16

This bounded frontier distinguishes a portal observation from an upstream
ontology release. BioPortal, OLS4 and HeTOP improve discovery, but their
visibility or service licence does not replace the licence attached to each
underlying ontology and its imported components.

## Routing disposition

| Surface | Repository action | Byte action |
| --- | --- | --- |
| BioPortal CDO/CDMO | retain versions, language, canonical URI and blank-licence observation | disabled because the ontology reports a SNOMED-derived hierarchy and no exact ontology licence was observed |
| BioPortal TARA | retain versions, language and PURL/repository route | disabled until the exact repository and component licences are recorded |
| BioPortal OCMR | retain BioPortal metadata plus the canonical Git repository identity | disabled until its Apache-2.0 repository licence, publication CC BY 3.0 statement and imported/merged components are reconciled in a file matrix |
| BioPortal TCDO | retain versions, language, repository and import inventory | disabled because the repository has no detected licence and contains imported ontologies |
| EBI OLS4 | run the bounded metadata-only workflow and route each record to its canonical `fileLocation` | never bulk-mirror OLS term responses; source bytes need their own rights decision |
| HeTOP | retain discovery metadata and source links where access permits | no scraping or concept-corpus mirror; resolve each terminology to its publisher |
| Global Health Informatics article | retain citation, timestamp, URL and response hash | none; the page is a pointer to HeTOP, not a dataset |

BioPortal's terms permit downloads subject to the underlying provider's
applicable licence and attribution requirements. Accordingly, `Public`
visibility is not treated as a redistribution grant. OLS4's service/API
licence likewise does not supersede the rights annotations and canonical source
terms of its indexed ontologies.

## Bounded OLS4 observation

`scripts/discover_ontology_portal_frontier.py` reads no more than ten pages of
500 metadata records each, sequentially, under an 8 MB response ceiling. Live
runs require at least one second between pages; the workflow uses two seconds.
It records response hashes, upstream versions, canonical file locations and
licence/rights annotations. Duplicate portal aliases collapse only when their
canonical source URL and upstream version match. No ontology file is fetched.

The official documentation publishes no numeric request ceiling. The workflow
therefore uses low request volume, sequential access and bounded retries at the
workflow level. A `429`, access denial, malformed response or changed
pagination fails the run; it does not trigger scraping or infer absence.

## OCMR contingency

The canonical Git repository and its commit history are discoverable, but no
bytes are copied by this frontier. Public materialisation remains disabled
until a component matrix identifies the licence and provenance of the core
ontology, imports, spreadsheets, merged outputs and other repository files.
If that matrix closes only for a subset, archive only that subset and retain
metadata/hashes for the rest.

This work does not establish portal, release, language or ontology-family
completeness and does not activate any source for clinical or production use.
