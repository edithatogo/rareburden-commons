# Track 003 synthetic reference report

All numbers are modelled from invented assumptions, not empirical observations.
This calculation/report is not an execution permission or independent validation.
Clinical use, policy allocation, country rankings and ancestry biology are unsupported.

Seed: 20260830; iterations: 10000.
Intervals describe invented parameter uncertainty, not empirical confidence.
Deterministic values are central-input plug-ins, not nonlinear expectations.
No observed diagnoses or total-population prevalence are available.
Costs are fictional constant-2025 currency for one full case-year per expressed person.
Complications are hypothetical, with full follow-up and no competing events.
Treatment changes imply no efficacy; overlapping outcome groups must not be summed.
Assumed conditional inputs remain labelled even when the conditioning set is empty.
Invented parameter uncertainty conditional on structure, not empirical confidence; fixed design assumptions have unquantified uncertainty; zero width is not certainty.

## Definitions and interpretation sources

Fictional geography: synthetic-rbc-p002; ages 0-100; all sexes.
D=1 denotes synthetic diabetes membership; E=1 is expressed aetiologic case status.
G=1 is a person-carrier flag, not an allele frequency or clinical variant interpretation.
Delay: first joint D=1/E=1 to first synthetic detection, conditional on detection.
Every expressed person is assumed complication-free at year start and followed all year.
Input definitions: examples/demonstrators/track-003-reference-inputs.json.
Interpretation evidence: docs/track-003-reference-runner-contract-2026-08-30.md
Interpretation evidence: docs/track-003-outcome-service-ledger-2026-08-30.yml
Interpretation evidence: docs/track-003-licensed-pathway-evidence-2026-08-30.yml
Interpretation evidence: docs/track-003-additional-source-screen-2026-08-30.md
Interpretation evidence: docs/track-003-reference-package-plan-2026-08-30.md
Interpretation evidence: docs/track-003-aetiologic-evidence-qualification-2026-08-30.yml
Interpretation evidence: docs/track-003-outcome-source-qualification-2026-08-30.md
Interpretation evidence: docs/track-003-evidence-gap-register-2026-08-30.yml
Interpretation evidence: docs/track-003-full-reference-acceptance-2026-08-30.md

## primary

Year: 2025; full fictional diabetes cohort.
Independent assumed parameter uncertainty; no event sampling

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2009.02 | 1676.94 | 245.493 to 5591.99 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1200 | 1201.67 | 974.637 | 131.944 to 3589.73 |
| undetected_people (people; modelled undetected expressed cases) | 800 | 807.348 | 625.857 | 72.9175 to 2575.72 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 480 | 482.892 | 360.177 | 42.1821 to 1641.46 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.8657 | 26.3762 | 1.93946 to 159.944 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03987e+06 | 3.22178e+06 | 434958 to 1.21694e+07 |

## denominator_low

Year: 2025; full fictional diabetes cohort.
Compatible denominator scaled by assumed low factor

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 80000 | 80010.7 | 80001.2 | 76084.1 to 84008.4 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 1600 | 1607.21 | 1341.55 | 196.394 to 4473.6 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 960 | 961.336 | 779.71 | 105.555 to 2871.78 |
| undetected_people (people; modelled undetected expressed cases) | 640 | 645.878 | 500.686 | 58.334 to 2060.58 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 384 | 386.314 | 288.142 | 33.7457 to 1313.17 |
| complication_people (people; one hypothetical event at most per case over full year) | 32 | 32.6926 | 21.101 | 1.55157 to 127.955 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 3.2e+06 | 3.23189e+06 | 2.57742e+06 | 347967 to 9.73554e+06 |

## denominator_high

Year: 2025; full fictional diabetes cohort.
Compatible denominator scaled by assumed high factor

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 120000 | 120016 | 120002 | 114126 to 126013 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2400 | 2410.82 | 2012.33 | 294.591 to 6710.39 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1440 | 1442 | 1169.56 | 158.333 to 4307.68 |
| undetected_people (people; modelled undetected expressed cases) | 960 | 968.817 | 751.029 | 87.501 to 3090.87 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 576 | 579.471 | 432.212 | 50.6185 to 1969.75 |
| complication_people (people; one hypothetical event at most per case over full year) | 48 | 49.0389 | 31.6515 | 2.32735 to 191.933 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4.8e+06 | 4.84784e+06 | 3.86613e+06 | 521950 to 1.46033e+07 |

## ascertainment

Year: 2025; full fictional diabetes cohort.
Perfect detection counterfactual; no causal outcome benefit

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0 | 0 | 0 | 0 to 0 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2009.02 | 1676.94 | 245.493 to 5591.99 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 2000 | 2009.02 | 1676.94 | 245.493 to 5591.99 |
| undetected_people (people; modelled undetected expressed cases) | 0 | 0 | 0 | 0 to 0 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 800 | 806.674 | 624.775 | 76.2803 to 2595.82 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.8657 | 26.3762 | 1.93946 to 159.944 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03987e+06 | 3.22178e+06 | 434958 to 1.21694e+07 |

## carrier_penetrance

Year: 2025; full fictional diabetes cohort.
Conditional person-carrier expression within diabetes

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200815 | 0.0176989 | 0.00441475 to 0.0496802 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.0119932 | 0.0102304 | 0.00232423 to 0.0322081 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2008.35 | 1770.95 | 441.023 to 4982.7 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1200 | 1199.4 | 1022.86 | 231.241 to 3208.53 |
| undetected_people (people; modelled undetected expressed cases) | 800 | 808.944 | 662.352 | 117.526 to 2349.83 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 480 | 481.642 | 382.492 | 65.0996 to 1489.39 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.664 | 28.3818 | 2.74921 to 153.286 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03458e+06 | 3.40717e+06 | 765709 to 1.10619e+07 |

## referral_selection

Year: 2025; full fictional diabetes cohort.
Forward selected fraction only; referral count unavailable

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2009.02 | 1676.94 | 245.493 to 5591.99 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1200 | 1201.67 | 974.637 | 131.944 to 3589.73 |
| undetected_people (people; modelled undetected expressed cases) | 800 | 807.348 | 625.857 | 72.9175 to 2575.72 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 480 | 482.892 | 360.177 | 42.1821 to 1641.46 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.8657 | 26.3762 | 1.93946 to 159.944 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03987e+06 | 3.22178e+06 | 434958 to 1.21694e+07 |
| selected_fraction (proportion; assumed within selected cohort; count unavailable) | 0.0392157 | 0.0390163 | 0.0331038 | 0.00491113 to 0.105612 |

## age_stratified

Year: 2025; full fictional diabetes cohort.
Disjoint 0-19 and 20-100 strata; assumed odds multipliers

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.0248025 | 0.024814 | 0.0208979 | 0.00307398 to 0.0681867 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.0148815 | 0.0148434 | 0.0121094 | 0.00165846 to 0.0439078 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2480.25 | 2482 | 2082.4 | 306.574 to 6843.59 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1488.15 | 1484.55 | 1210.88 | 164.717 to 4398.37 |
| undetected_people (people; modelled undetected expressed cases) | 992.099 | 997.445 | 777.094 | 90.9984 to 3157.21 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 595.26 | 596.538 | 447.033 | 52.6381 to 2008.8 |
| complication_people (people; one hypothetical event at most per case over full year) | 49.605 | 50.4829 | 32.7071 | 2.42202 to 196.007 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4.9605e+06 | 4.99096e+06 | 3.99844e+06 | 543191 to 1.49423e+07 |
| young_expected_people (people; expressed cases in disjoint age 0-19 stratum) | 252.525 | 254.953 | 211.373 | 30.7231 to 718.453 |
| adult_expected_people (people; expressed cases in disjoint age 20-100 stratum) | 2227.72 | 2227.04 | 1871.02 | 275.851 to 6125.13 |

## calendar_2030

Year: 2030; full fictional diabetes cohort.
2030 odds contrast; denominator held fixed; not a forecast

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.0248756 | 0.0249211 | 0.0209499 | 0.00307512 to 0.0687298 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.0149254 | 0.0149075 | 0.012146 | 0.00166039 to 0.0442225 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2487.56 | 2492.7 | 2087.51 | 306.684 to 6896.62 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1492.54 | 1490.96 | 1213.29 | 164.82 to 4430.47 |
| undetected_people (people; modelled undetected expressed cases) | 995.025 | 1001.74 | 779.013 | 91.0427 to 3184.69 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 597.015 | 599.126 | 447.939 | 52.6645 to 2027.54 |
| complication_people (people; one hypothetical event at most per case over full year) | 49.7512 | 50.702 | 32.8154 | 2.42285 to 197.521 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4.97512e+06 | 5.01249e+06 | 4.00901e+06 | 543377 to 1.50344e+07 |

## model_eligibility

Year: 2025; model-covered subset only; uncovered burden unavailable.
Assumed same fraction in covered subset; no ancestry biology

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 50000 | 50006.7 | 50000.8 | 47552.6 to 52505.3 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 50000 | 50006.7 | 50000.8 | 47552.6 to 52505.3 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 1000 | 1004.51 | 838.471 | 122.746 to 2796 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 600 | 600.835 | 487.318 | 65.972 to 1794.87 |
| undetected_people (people; modelled undetected expressed cases) | 400 | 403.674 | 312.929 | 36.4588 to 1287.86 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 240 | 241.446 | 180.089 | 21.0911 to 820.73 |
| complication_people (people; one hypothetical event at most per case over full year) | 20 | 20.4329 | 13.1881 | 0.969729 to 79.9721 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 2e+06 | 2.01993e+06 | 1.61089e+06 | 217479 to 6.08472e+06 |

## unclassified

Year: 2025; classified subset only; unclassified burden unavailable.
Assumed same fraction in classified subset; no missing imputation

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 90000 | 90012 | 90001.4 | 85594.6 to 94509.5 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 10000 | 10001.3 | 10000.2 | 9510.51 to 10501.1 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 1800 | 1808.12 | 1509.25 | 220.943 to 5032.79 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1080 | 1081.5 | 877.173 | 118.75 to 3230.76 |
| undetected_people (people; modelled undetected expressed cases) | 720 | 726.613 | 563.271 | 65.6258 to 2318.15 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 432 | 434.603 | 324.159 | 37.9639 to 1477.31 |
| complication_people (people; one hypothetical event at most per case over full year) | 36 | 36.7791 | 23.7386 | 1.74551 to 143.95 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 3.6e+06 | 3.63588e+06 | 2.8996e+06 | 391463 to 1.09525e+07 |

## strata_independent

Year: 2025; full fictional diabetes cohort.
Independent fraction draws in unnamed disjoint strata

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0201082 | 0.0180511 | 0.00495064 to 0.0468189 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.0120639 | 0.0103772 | 0.00257449 to 0.03097 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2011.05 | 1805.67 | 493.841 to 4710.35 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1200 | 1206.43 | 1035.1 | 257.461 to 3094.68 |
| undetected_people (people; modelled undetected expressed cases) | 800 | 804.622 | 669.943 | 135.888 to 2187.99 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 480 | 484.287 | 387.936 | 70.3958 to 1421.51 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.6848 | 29.1114 | 3.01993 to 141.569 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03874e+06 | 3.44491e+06 | 818784 to 1.04631e+07 |

## strata_shared

Year: 2025; full fictional diabetes cohort.
Perfectly shared fraction draw in unnamed disjoint strata

| Metric (unit; conditioning) | Plug-in | Mean | Median | 95% interval |
|---|---:|---:|---:|---|
| modelled_denominator (people; model-covered/classified diabetes scope) | 100000 | 100013 | 100002 | 95105.1 to 105011 |
| unavailable_denominator (people; diabetes population with unavailable aetiology) | 0 | 0 | 0 | 0 to 0 |
| assumed_case_probability (proportion; assumed within modelled diabetes scope) | 0.02 | 0.0200853 | 0.0168305 | 0.00246161 to 0.0557502 |
| assumed_detected_probability (proportion; assumed within modelled diabetes scope) | 0.012 | 0.012015 | 0.00975735 | 0.0013309 to 0.0358665 |
| assumed_undetected_given_case_probability (proportion; assumed conditional on case) | 0.4 | 0.400995 | 0.396645 | 0.137319 to 0.704068 |
| expected_people (people; expressed cases in modelled diabetes scope) | 2000 | 2009.02 | 1676.94 | 245.493 to 5591.99 |
| detected_people (people; modelled detected cases; not observed diagnoses) | 1200 | 1201.67 | 974.637 | 131.944 to 3589.73 |
| undetected_people (people; modelled undetected expressed cases) | 800 | 807.348 | 625.857 | 72.9175 to 2575.72 |
| assumed_delay_given_detection_years (years; assumed historical conditional delay) | 3 | 3.00552 | 2.99375 | 1.09902 to 4.90353 |
| treatment_change_people (people; hypothetical change among detected cases; no benefit) | 480 | 482.892 | 360.177 | 42.1821 to 1641.46 |
| complication_people (people; one hypothetical event at most per case over full year) | 40 | 40.8657 | 26.3762 | 1.93946 to 159.944 |
| annual_cost (synthetic_currency_units; one full year, constant fictional 2025 prices) | 4e+06 | 4.03987e+06 | 3.22178e+06 | 434958 to 1.21694e+07 |

## Evidence and limitations

The bound runner contract contains source applicability and family dispositions.
Clinical cohorts, genetic-testing duration and referral yields do not validate these
fictional population probabilities, delay endpoints, outcome probabilities or prices.
Source rights, correction, transport and empirical evidence gaps remain open.
Unknown/uncovered burden is unavailable, not zero. No extrapolation is justified.
