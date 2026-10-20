# Near-target astigmatism analysis — frozen BMC Ophthalmology release

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#installation)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This repository contains the author-reviewed Python implementation and frozen computational record for:

> **Residual astigmatism and toric intraocular lens correction in near-targeted cataract surgery: a single-centre retrospective cohort study** (BMC Ophthalmology)

Release **v1.0.1** is the version cited in the revised manuscript. It changes no analysis rule or numerical output relative to v1.0.0. It also removes two items that release v1.0.0 should not have made public — internal record numbers encoded in a test file and reversible record fingerprints in the configuration — so **v1.0.0 must not be used**; see [CHANGELOG](CHANGELOG.md).

## What this repository is — and is not

All results reported in the manuscript were generated in a single unified analysis that was run interactively in OpenAI ChatGPT Advanced Data Analysis. That transient session was not a persistent, version-controlled notebook. Its final 20-row imputation-component table, pooled outputs, non-patient-level diagnostic and sensitivity tables, and the submitted figure files were preserved and are archived here.

This repository is therefore **a frozen release replay and an independent reconstruction of the primary estimate**. It is **not** the exact code that produced every reported result:

- The **primary model** (20 multiple imputations, propensity-score overlap weighting, patient-clustered Gaussian GEE, Rubin pooling) is both replayed exactly from the archived components and independently re-implemented from the source data (see the two verification modes below).
- The **stratified, secondary and sensitivity analyses** are **not rerun** by this code. Their principal non-patient-level estimates are archived in `reference/model_outputs/` (listed in [docs/REPRODUCIBILITY_NOTES.md](docs/REPRODUCIBILITY_NOTES.md)), from which `figures.py` regenerates aggregate diagnostic plots. Descriptive counts, vector/rotation and Alpins summaries and plotted acuity means are reported in the article and its Additional file 1 but are not archived as separate tables.
- The **eight figure files submitted with the article** are archived unchanged in `reference/figures/`; their SHA-256 hashes are listed in `RELEASE_MANIFEST.sha256` and recorded again by the frozen replay.

## Verified final result

The archived 20-imputation component estimates pool to:

- toric coefficient: **−0.274422593 D**
- standard error: **0.055968938 D**
- 95% CI: **−0.384121711 to −0.164723475 D**
- imputations: **20**

The final source-data denominators are:

- eligible cataract-surgery records: **60,302 eyes**
- near-target cohort: **9,088 eyes / 6,168 patients**
- postoperative manifest-refraction observed: **3,301 eyes / 2,355 patients**
- primary analytic set: **3,290 eyes / 2,348 patients**
- toric / non-toric eyes: **988 / 2,302**

## Two verification modes

### 1. Frozen release replay — exact

`near-target-pipeline frozen`:

- applies Rubin's rules to the archived 20 imputation-level estimates of the primary model;
- reproduces the reported coefficient, standard error and confidence interval to floating-point precision;
- copies the eight submitted figure files from `reference/figures/` and records their SHA-256 hashes, which can be compared with `RELEASE_MANIFEST.sha256` and with the files published with the article;
- regenerates aggregate diagnostic plots from the archived non-patient-level CSV outputs.

### 2. Private raw-source verification — independent reconstruction of the primary estimate

`near-target-pipeline raw`:

- verifies SHA-256 hashes of the private source workbooks;
- independently reconstructs the full cohort and all denominators;
- reruns a documented 20-imputation, propensity-score overlap-weighted, patient-clustered Gaussian GEE for the primary model;
- compares the reconstructed coefficient with the frozen coefficient using the **±0.03 D computational-equivalence margin** defined in `reference/expected_results.json`.

On the source files used for the revision, the independent rerun produced **−0.280614278 D**, differing from the frozen estimate by **−0.006191685 D**, while reproducing every final denominator and treatment count exactly. This is an independent computational verification, not a claim that the unavailable transient random draws were reconstructed verbatim.

See [Reproducibility notes](docs/REPRODUCIBILITY_NOTES.md) for the full rationale.

## Repository structure

```text
near-target-astigmatism-analysis/
├── README.md
├── LICENSE
├── CITATION.cff
├── CHANGELOG.md
├── RELEASE_MANIFEST.sha256
├── pyproject.toml
├── requirements.txt
├── environment.yml
├── Dockerfile
├── Makefile
├── config/
│   ├── analysis.yml
│   └── raw_files.example.yml
├── src/near_target_pipeline/
│   ├── data_io.py
│   ├── classification.py
│   ├── cohort.py
│   ├── covariates.py
│   ├── models.py
│   ├── figures.py
│   ├── frozen.py
│   └── cli.py
├── reference/
│   ├── expected_results.json
│   ├── raw_input_manifest.json
│   ├── model_outputs/      # archived non-patient-level outputs, including stratified and sensitivity analyses
│   └── figures/            # the eight figure files submitted with the article
├── data/synthetic/
├── scripts/
├── tests/
├── docs/
└── outputs/                # outputs of the frozen replay, raw verification and tests
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Conda users may instead run:

```bash
conda env create -f environment.yml
conda activate near-target-astigmatism
```

## Exact frozen release verification

```bash
near-target-pipeline frozen --output outputs/frozen_release
```

Expected result (the last one or two digits of the standard error can differ across numerical-library versions, i.e. at floating-point precision):

```text
passed: true
coefficient: -0.2744225929999175
standard_error: 0.0559689378108702
all_figures_identical: true
```

The same operation can be invoked with:

```bash
python scripts/run_frozen_release.py
```

## Private raw-source verification

The source clinical workbooks are **not** included. Copy the template and point it to the institutionally controlled directory:

```bash
cp config/raw_files.example.yml config/raw_files.yml
# edit raw_data_root and filenames
near-target-pipeline raw \
  --raw-config config/raw_files.yml \
  --output outputs/raw_verification
```

The private configuration must also contain the `private_audit` block (manual-audit record fingerprints; template in `config/raw_files.example.yml`). These fingerprints are deliberately not public. The runner stops if required files or the `private_audit` block are absent. It reports whether each source-file hash matches the frozen manifest.

## Automated tests

Public tests, requiring no clinical data:

```bash
pytest -q -m "not private_data"
```

Private end-to-end tests:

```bash
NEAR_TARGET_RAW_CONFIG=config/raw_files.yml pytest -q -m private_data
```

Verification record (details in [docs/VERIFICATION_REPORT.md](docs/VERIFICATION_REPORT.md)):

- public tests: **8 passed, 1 skipped** (rerun for v1.0.1; the skipped test checks the tree against a private list of identifiers held by the authors)
- private source-data tests: **2 passed** (v1.0.0 preparation environment; v1.0.1 changes only where the audit fingerprints are read from)
- final denominators: **all exact**
- reconstructed estimate: **within the ±0.03 D margin**

## Terminology in archived outputs

Some archived CSV files in `reference/model_outputs/` label the final results "final frozen pipeline". In the article these results are described as the **unified analysis**; the two terms refer to the same results.

## Frozen cohort rules

- Valid surgery record: numerical patient ID, right/left eye, valid surgery date and target.
- Near target: intended target **< −0.50 D**.
- Distance target for interaction analyses: **−0.50 to +0.50 D**.
- Postoperative manifest refraction: numerical cylinder measured **30–180 days** after surgery, visit closest to postoperative day **70**.
- Manifest-observed cohort: selected visit also contains a numerical sphere.
- Achieved spherical equivalent: sphere + signed cylinder / 2.
- Primary analytic set: achieved spherical equivalent **−8 to +8 D**.
- Both eyes may contribute; inference is clustered by patient.

## Primary model

- 20 multiple imputations using chained iterative regression with posterior sampling.
- Propensity score for toric implantation using the frozen covariate list in `config/analysis.yml`; in this reimplementation surgeon group and corneal-astigmatism axis type enter the model as integer codes.
- Overlap weights: `1 − PS` for toric eyes and `PS` for non-toric eyes.
- Gaussian GEE for absolute residual manifest cylinder with patient-level clustering and independence working correlation.
- Rubin pooling across 20 completed datasets.

## Privacy and data governance

The repository contains **no source Excel workbook, direct patient identifier, exact patient-level surgery date or patient-level analytic dataset**. The public synthetic dataset is entirely artificial. Source data remain controlled by Tsukazaki Hospital and are available only under the institutional conditions stated in the manuscript.

The file `reference/raw_input_manifest.json` contains source-file roles, byte sizes and SHA-256 checksums solely to verify that an authorised rerun uses the same private inputs. Manual-audit record fingerprints are not public: unsalted fingerprints of patient ID, eye, surgery date and IOL model can be reversed by exhaustive search, so they are kept in the private configuration.

## Citation and archive

- GitHub: <https://github.com/HitoshiTabuchi/near-target-astigmatism-analysis> (release `v1.0.1`)
- Zenodo: release `v1.0.1` is archived in Zenodo by direct deposit of the GitHub release archive; the DOI is given in the article's Availability of data and materials statement.
- Citation metadata: [CITATION.cff](CITATION.cff)

## Responsibility statement

OpenAI ChatGPT Advanced Data Analysis was used interactively for the original exploratory analysis and for the final unified analysis, and assisted in preparing this version-controlled implementation. Anthropic Claude assisted with documentation and metadata updates in v1.0.1. The authors reviewed the code, reran the tests, verified the reported outputs and retain full responsibility for the analysis and manuscript.
