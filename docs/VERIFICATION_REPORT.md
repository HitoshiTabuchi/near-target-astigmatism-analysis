# Verification report

## v1.0.1 — 2026-10-19

Release v1.0.1 changes documentation, metadata and the archived figure files, and moves the manual-audit record fingerprints from `config/analysis.yml` to the private configuration (see CHANGELOG). The analysis rules and `reference/model_outputs/` are unchanged from v1.0.0.

### Exact frozen release (rerun for v1.0.1)

- Archived imputations pooled: 20
- Coefficient: -0.2744225929999175 D
- Standard error: 0.05596893781087016 D
- 95% CI: -0.384121711109223 to -0.164723474890612 D
- Model checks against `reference/expected_results.json`: all passed
- Submitted figure files archived and replayed: 8/8
- SHA-256 of the archived figure files (identical to the files submitted with the revised article):

  - `Figure_1_study_flow_and_availability.png`: `928334f8d399440d5012b8c0e4c3e0cd793f7e00691d74dde64aef9c434c71de`
  - `Figure_2_unified_diagnostics_and_sensitivity.png`: `845d8737a84f6ba2df04e0d69795e09f7ca6aa954e0e390bb6c1c66a4df53948`
  - `Figure_3_target_interaction_and_monovision.png`: `065ac3ddaeaff8a84ec48334de9918928d5e9909bff1bee1fc2ae4bcfc391ead`
  - `Supplementary_Figure_S1_toric_by_stratum.png`: `13bfeca113077681a6dff69b6bed11b0f46eda0d8619ac7c97bd3631370d2e51`
  - `Supplementary_Figure_S2_near_target_VA.png`: `6e7bddad6946893f4ceffbbe3b72dabe0d094adffedcba780aaf6889cecd7464`
  - `Supplementary_Figure_S3_continuous_achieved_SE.png`: `fc4f6b6276a3937c34258a3cf4679cf26563fdac946553751ebd8e74a5dc2cb0`
  - `Supplementary_Figure_S4_vector_rotation.png`: `c7d853dd66910b1d37b1fbadf36d1d4e6ecbaa744798eea85c20ea682fa9290c`
  - `Supplementary_Figure_S5_exploratory_alpins.png`: `c1e6249c06377d6a68fb5d8d96ecd1ad7259e4525e2c6f43a7b1524539cdaf13`

- Overall frozen-release verification: **PASSED**

### Automated tests (rerun for v1.0.1)

- Public tests: 8 passed, 1 skipped (private identifier list not supplied), 2 private tests deselected (`outputs/pytest_public.txt`)
- The identifier check was also run with the authors' private token list: passed (no internal record number appears anywhere in the release).
- Private source-data tests were not rerun for v1.0.1. Relative to v1.0.0 the only change on that path is that the audit fingerprints are read from the private configuration instead of `config/analysis.yml`; the v1.0.0 results below were obtained with the same fingerprints.

### Environment used for the v1.0.1 rerun

Python 3.13.16; numpy 2.5.4; pandas 2.3.3; scipy 1.18.1; statsmodels 0.15.0; scikit-learn 1.9.1; matplotlib 3.11.2; PyYAML 6.0.3; openpyxl 3.1.5; pytest 8.4.2.

## v1.0.0 — 2026-09-14

### Exact frozen release

- Archived imputations pooled: 20
- Coefficient: −0.2744225929999175 D
- Standard error: 0.0559689378108702 D
- 95% CI: −0.3841217111092230 to −0.1647234748906120 D
- Final PNG figures replayed: 8/8
- Figure SHA-256 identity: 8/8 passed
- Overall frozen-release verification: **PASSED**

### Private raw-source reconstruction

- Source-file SHA-256 checks: 10/10 passed
- Eligible eyes: 60,302 — exact
- Near-target eyes/patients: 9,088 / 6,168 — exact
- Manifest-observed eyes/patients: 3,301 / 2,355 — exact
- Primary eyes/patients: 3,290 / 2,348 — exact
- Toric/non-toric eyes: 988 / 2,302 — exact
- Independently reconstructed coefficient: −0.28061427835638175 D
- Difference from frozen coefficient: −0.006191685356464249 D
- Computational-equivalence margin (`reference/expected_results.json`): ±0.03 D
- Raw-source verification: **PASSED**

### Automated tests

- Public tests: 6 passed, 2 private tests deselected
- Private tests: 2 passed, 6 public tests deselected

### Interpretation

The exact submitted numerical result is reproducible from the preserved 20 imputation-level frozen outputs, and the figure files archived at v1.0.0 were replayed byte-for-byte. The independently reconstructed source-data pipeline reproduces all denominators exactly and yields a coefficient within 0.0062 D of the frozen estimate. The small stochastic difference is reported rather than concealed because the transient original interactive imputation state was not preserved.
