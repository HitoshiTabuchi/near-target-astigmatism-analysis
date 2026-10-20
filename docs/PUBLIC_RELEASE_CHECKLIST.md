# GitHub + Zenodo release checklist

1. Review `README.md`, `docs/REPRODUCIBILITY_NOTES.md`, and the source code.
2. Confirm that no clinical workbook, patient-level file, record number or record fingerprint is present (supply the private token list):
   ```bash
   NEAR_TARGET_PRIVATE_TOKENS=/path/to/private_tokens.txt pytest -q tests/test_no_identifiers.py
   ```
3. Run public tests:
   ```bash
   pytest -q -m "not private_data"
   ```
4. Run the institutionally controlled private verification:
   ```bash
   NEAR_TARGET_RAW_CONFIG=config/raw_files.yml pytest -q -m private_data
   ```
5. Recreate the exact frozen release:
   ```bash
   near-target-pipeline frozen --output outputs/frozen_release
   ```
6. Confirm that `CITATION.cff` and `docs/CODE_AVAILABILITY.md` contain no placeholders.
7. Regenerate `RELEASE_MANIFEST.sha256` (all files except `outputs/` and the manifest itself) and check it with `sha256sum -c RELEASE_MANIFEST.sha256`.
8. Push the changes to https://github.com/HitoshiTabuchi/near-target-astigmatism-analysis. Do not copy the private raw configuration or source workbooks.
9. Create a GitHub release with a new tag (v1.0.1 for the revised manuscript). Never alter an archived release silently.
10. Confirm that Zenodo archived the release, and cite the Zenodo DOI that resolves to all versions (concept DOI) in the manuscript and response.
