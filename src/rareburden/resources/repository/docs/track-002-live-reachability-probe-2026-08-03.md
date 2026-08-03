# Track 002 live reachability probe — 2026-08-03

This read-only probe records HTTP reachability only. It does not establish
licence, scientific fitness, redistribution rights, completeness or production
activation. Responses were not retained as source evidence by this probe.

| Candidate | Result | Content type | Bytes observed | Interpretation |
| --- | ---: | --- | ---: | --- |
| Orphadata `en_product9_prev.xml` | 200 | `application/xml` | 16,178,169 | Reachable; exact terms and semantics remain gated |
| Orphadata `en_product1.xml` | 200 | `application/xml` | 54,026,799 | Reachable; exact terms and semantics remain gated |
| UN WPP compact workbook | 200 | XLSX | 26,142,942 | Reachable; exact extraction and terms remain gated |
| WHO GHE year-2000 candidate workbook | 200 | XLSX | 12,756,114 | Reachable; third-party terms and scientific scope remain gated |
| World Bank `SP.POP.TOTL` probe | timeout (`http=000`) | unavailable | 0 | Fail closed; retain prior response manifest and do not substitute silently |

The World Bank timeout is an access observation, not evidence that the endpoint
or its terms have changed. A later probe must capture a bounded response hash
before any source promotion. All candidate activation states remain unchanged.
