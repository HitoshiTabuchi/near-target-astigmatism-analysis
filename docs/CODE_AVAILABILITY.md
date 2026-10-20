# Code availability wording for the manuscript

Wording used in the revised manuscript (Declarations, Availability of data and materials); the Zenodo DOI is given in the article:

> Analysis code is openly available at https://github.com/HitoshiTabuchi/near-target-astigmatism-analysis (release v1.0.1) and is archived in Zenodo (DOI given in the article; all release versions are listed in the record). Consistent with the repository documentation, the deposit is a frozen release replay and an independent reconstruction of the primary estimate; it is not the exact code that produced every reported result. All reported results were generated in a single unified analysis run in an interactive session that was not itself version-controlled. The repository contains the frozen cohort-definition and validity rules, and code for source-file hash checks, cohort extraction and validity filtering, multiple imputation, propensity-score estimation, overlap weighting, patient-clustered generalised estimating equations and Rubin pooling for the primary model. The replay pools the archived 20 imputation-level estimates of that model and reproduces the reported coefficient, standard error and confidence interval to floating-point precision. The independent reconstruction rebuilds the cohort from the institutionally controlled source files and reruns the primary model; on the source files used for this revision it reproduced every denominator and treatment count exactly and gave -0.281 D against the reported -0.274 D, within the 0.03 D computational-equivalence margin defined in the repository. The stratified, secondary and sensitivity analyses are not rerun by the deposited code; their principal estimates are archived in the repository as non-patient-level tables (listed in the repository documentation), from which the repository's figure code regenerates aggregate diagnostic plots, and the figure files submitted with this article are archived there with their SHA-256 hashes.

Patient-level clinical source data are not publicly deposited because of confidentiality and institutional governance requirements; access to de-identified data is subject to institutional approval as described in the manuscript.

## Where each element is in this repository

| Element | Location |
|---|---|
| Frozen cohort-definition and validity rules | `config/analysis.yml`, `src/near_target_pipeline/cohort.py`, `covariates.py`, `classification.py` (manual-audit record fingerprints are supplied privately; see `config/raw_files.example.yml`) |
| Source-file hash checks | `reference/raw_input_manifest.json`, `src/near_target_pipeline/data_io.py` |
| Imputation, propensity score, overlap weights, GEE, Rubin pooling (primary model) | `src/near_target_pipeline/models.py` |
| Archived 20 imputation-level estimates of the primary model | `reference/model_outputs/primary_mi_components.csv` |
| Archived principal estimates of the stratified, secondary and sensitivity analyses (not rerun) | `reference/model_outputs/` (full list in `docs/REPRODUCIBILITY_NOTES.md`) |
| Figure files submitted with the article | `reference/figures/` (SHA-256 in `RELEASE_MANIFEST.sha256`) |
| Frozen replay and raw-source verification outputs | `outputs/` |

## Use of artificial-intelligence tools

OpenAI ChatGPT Advanced Data Analysis was used interactively for the original exploratory analysis and for the final unified analysis, and assisted in preparing this version-controlled implementation. Anthropic Claude assisted with documentation and metadata updates in v1.0.1. The interactive analysis session was not itself a persistent version-controlled computational environment; the repository therefore distinguishes (1) exact replay of the archived, non-patient-level frozen release outputs and (2) an independent raw-source reconstruction of the primary estimate. The authors reviewed the scripts, verified the outputs and accept full responsibility for the analysis.
