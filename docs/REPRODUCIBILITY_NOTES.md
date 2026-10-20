# Reproducibility notes

## Why two verification modes are supplied

All results reported in the manuscript were generated in a single unified analysis run interactively in ChatGPT Advanced Data Analysis. The exact transient notebook state, including every stochastic imputation draw, was not preserved as a version-controlled artifact. The final revision did preserve the complete 20-row imputation-level result table of the primary model, pooled estimates, the principal non-patient-level diagnostic, stratified, secondary and sensitivity estimates, and the submitted figure files.

For scientific transparency, this repository does **not** represent reconstructed code as a verbatim export of the original interactive session. Instead it provides two complementary modes:

1. **Frozen release replay** — pools the archived 20 imputation-level estimates with Rubin's rules, verifies the exact final coefficient, standard error and confidence interval, and records the SHA-256 hashes of the archived submitted figure files.
2. **Raw-source verification** — independently rebuilds the cohort from the private source workbooks, reproduces every final denominator and treatment count, and reruns a documented 20-imputation overlap-weighted, patient-clustered GEE. The raw-source estimate is compared with the frozen estimate using the ±0.03 D computational-equivalence margin defined in `reference/expected_results.json`.

This distinction prevents a reconstructed stochastic implementation from being mislabelled as the unavailable original session code while still permitting exact verification of the reported frozen result and an independent source-data reanalysis.

## Scope

The repository is a frozen release replay and an independent reconstruction of the **primary estimate**. It is not the exact code that produced every reported result. The stratified, secondary and sensitivity analyses reported in the manuscript (preoperative-cylinder strata, acuity slopes, target interactions, paired monovision, continuous achieved-refraction interaction, optical-design exclusions, era restriction, observation weighting, complete-case, deterministic-imputation, full optical-covariate and spline propensity models) are **not rerun** by this code.

Archived as non-patient-level tables in `reference/model_outputs/`: the 20 imputation-level estimates and pooled primary estimate; stratum estimates with eye counts and effective sample sizes; deterministic-imputation and complete-case estimates; balance diagnostics (Table 2); near-target acuity slopes (Table 4); target interactions (Table 5); paired monovision; the continuous achieved-refraction interaction; the sensitivity summary (Table 6) and observation weighting; Table 1, the observed-versus-not-observed comparison (Table S4) and absolute residual cylinder (Table S5); the IOL model inventory; and the numerical harmonisation audit.

Reported in the article and its Additional file 1 but **not** archived as separate tables: outcome availability by target arm (Table S1), covariate availability (Table S3), vector and rotation summaries (Figure S4), Alpins-style metrics (Figure S5) and the plotted acuity means of Figure 3A and Figure S2A.

The age range given in `config/analysis.yml` (18-100 years) is documented but not enforced by this reimplementation; the reconstruction nevertheless reproduces every reported denominator. A further known simplification: this reimplementation enters surgeon (raw surgeon labels) and corneal-astigmatism axis type into the propensity model as single integer codes, whereas the article describes adjustment for 12 higher-volume surgeon categories and an Other category. Together with the unrecoverable imputation draws, this may contribute to the difference between the reconstruction (-0.281 D) and the reported estimate (-0.274 D); the code is left unchanged so that the reported reconstruction result remains reproducible.

## Frozen estimand

- Near target: intended target < −0.50 D.
- Postoperative refraction: numerical cylinder, 30–180 days after surgery, closest to day 70.
- Manifest-observed cohort: selected visit also has a numerical sphere.
- Primary analytic set: achieved spherical equivalent between −8 and +8 D.
- Treatment: toric IOL classification from model/procedure audit.
- Estimand: overlap-population association between toric implantation and absolute residual manifest cylinder.
- Model: 20-imputation overlap weighting and Gaussian GEE clustered by patient.

## Patient privacy

No source workbook, direct identifier, record number, surgery date, patient-level analytic table or notebook output containing clinical records is included in the public release. The raw-source runner operates only on locally supplied private files. The public repository stores SHA-256 values of the source files only.

Manual-audit record fingerprints (SHA-256 of patient ID, eye, surgery date and IOL model for the four records adjudicated as toric and the one record whose axial length was excluded) are kept in the private configuration, because unsalted fingerprints of such low-entropy fields can be reversed by exhaustive search. Release v1.0.0 published them, together with internal record numbers encoded in a test file; both were removed in v1.0.1 and v1.0.0 must not be used.
