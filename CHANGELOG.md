# Changelog

## 1.0.1 — 2026-10-19

Release for the revised manuscript. No analysis rule, model output (`reference/model_outputs/`) or numerical result changed; the frozen replay and public tests were rerun and pass.

**Privacy correction — do not use v1.0.0.**

- `tests/test_no_identifiers.py` in v1.0.0 encoded, in split form, four internal record numbers from the manual audit. They are removed; the identifier check now reads its token list from a private file (`NEAR_TARGET_PRIVATE_TOKENS`) and is skipped when that file is absent.
- `config/analysis.yml` in v1.0.0 listed unsalted SHA-256 fingerprints of five manually audited records (patient ID, eye, surgery date and IOL model), which can be reversed by exhaustive search. They are removed from the public configuration and are now supplied in the private raw-source configuration (`private_audit` block; template in `config/raw_files.example.yml`). `near-target-pipeline raw` and the private tests read them through `data_io.load_private_audit`; the classification and validity rules themselves are unchanged.
- New public tests: one fails if any record fingerprint reappears in `config/analysis.yml`; two check that the private-audit block is read from the private configuration and that the raw run stops when it is missing.

**Other changes**


- `reference/figures/` now holds the exact eight figure files submitted with the revised article (byte-identical; hashes in `RELEASE_MANIFEST.sha256`). Relative to v1.0.0:
  - Figures 1 and 2: the overall title inside the graphic was removed (titles are given in the figure legends); Figure 2 panel B was retitled "Imputation-specific estimates" (previously "Frozen-pipeline MI estimates").
  - Figure 1: the panel A flow diagram was redrawn so that its boxes no longer overlap and all text lies inside them; its content is unchanged.
  - Figure 3: the overall title inside the graphic was removed and panel A was retitled "Low-cylinder acuity by target arm" (previously "Defocus floor differs by viewing distance").
  - Supplementary figures were renumbered in order of first citation in the article (v1.0.0 S3 -> S1, S1 -> S2, S5 -> S3, S2 -> S4, S4 -> S5); file names and the figure numbers in the in-image titles were changed accordingly, and no plotted content changed.
  - Former S2 (now S4): the title inside the graphic was removed. Former S4 (now S5): its in-graphic figure number had already been corrected in the submitted version.
- README, `docs/CODE_AVAILABILITY.md` and `docs/REPRODUCIBILITY_NOTES.md`: scope stated explicitly — this release is a frozen replay and an independent reconstruction of the primary estimate, not the exact code that produced every reported result; the principal estimates of the stratified, secondary and sensitivity analyses are archived outputs and are not rerun.
- `CITATION.cff`: repository URL completed; version and release date updated. Placeholders removed from `docs/CODE_AVAILABILITY.md`.
- `RELEASE_MANIFEST.sha256` regenerated; it lists exactly the files of the public repository (excluding `outputs/` and the manifest itself). The v1.0.0 manifest also listed three hidden configuration files (`.gitattributes`, `.gitignore`, `.zenodo.json`) that were not part of the public upload.
- Package version set to 1.0.1 (`pyproject.toml`, `__init__.py`); default archive name in `scripts/create_release_archive.py` updated.

## 1.0.0 — 2026-09-14

- Frozen the BMC Ophthalmology R1 analysis outputs.
- Added exact Rubin pooling of the archived 20 imputation-level estimates.
- Added byte-identical replay and SHA-256 verification of all final PNG figures.
- Added independent reconstruction of the source cohort from the private Excel workbooks.
- Added a documented 20-imputation overlap-weighted patient-clustered GEE verification run.
- Added public and private-data automated tests.

Superseded exploratory estimates of −0.317 D and −0.299 D are not used as the final manuscript estimate. The archived final estimate is −0.274422593 D.
