# Track 002 MedLexSp and KIOM evidence frontier — 2026-08-16

This frontier records identity, provenance, rights and failed-access evidence
without retaining or uploading lexicon or ontology payload bytes. Its executable
record is `docs/track-002-medlexsp-kiom-frontier-2026-08-16.json`.

## MedLexSp

Digital CSIC handle `10261/270429` is the Spanish Medical Lexicon (MedLexSp),
DOI `10.20350/digitalCSIC/14656`; it is not an ontology. The landing page exposed
three documentation bitstreams whose exact sizes and SHA-256 digests are recorded
in the JSON frontier. No dataset payload was present in that public bitstream list.

The observed licence requires a signed agreement, restricts use to
non-commercial/non-profit research, prohibits modification, and requires the
lexicon to be held confidentially without copying, publication, distribution,
transfer or third-party access. Consequently the lexicon must not be placed in a
public repository, private Hugging Face repository or other third-party cloud
unless the rights holder expressly authorizes that processor and storage route.
Public metadata, citation, source URLs and hashes are the only active route.
`openAccess` metadata and the README's description of a restriction-filtered
version do not override those exact licence terms.

## KIOM ontology

Jang et al., *Bioinformatics* 2010;26(18):2359–2360,
DOI `10.1093/bioinformatics/btq424`, is the authoritative publication provenance
for the named `TraditionalKoreanMedicine.rdf-xml.owl` URL. The host failed DNS
resolution during the bounded observation, so no response bytes, exact version,
language inventory or digest were observed. The publication's availability
statement is not a redistribution or cloud-storage licence. Only metadata,
citation and the failed-access receipt may be archived until an authoritative
artifact and explicit rights are observed.

## Non-duplication boundary

KIOM covers Traditional Korean Medicine medicinal materials. TARA covers
acupoints and anatomical mappings; OCMR covers anti-rheumatism traditional
Chinese medicines; TCDO covers traditional Chinese drugs. These resources have
thematic overlap but are not alternate copies of one artifact. They must retain
separate identifiers, release histories, language inventories, licences and
hashes. No availability or rights conclusion for one transfers to another.

Stop on a payload appearing in repository history, a public/private-cloud route
being enabled without the required grant, a hash mismatch, or any completeness,
language, version or duplicate claim not supported by exact evidence.
