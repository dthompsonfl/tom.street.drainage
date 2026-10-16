# Historical Git exposure | preliminary technical assessment (2026-10-16)

**Scope:** public repository `dthompsonfl/tom.street.drainage`, live baseline `257c712d232f2d5e5495e26b6a6e9572dc452c22`. This is not a security-clearance certificate or authorization to rewrite Git history.

## Verified from GitHub and saved contemporaneous evidence

- `main` is a public branch and at this baseline contains **451 tracked files**, including 27 workflows. The current tree no longer contains the ten restricted portal captures listed in `00_CONTROL/RESTRICTED_EVIDENCE_INDEX.csv`.
- The historical public commit `5ddbac9ba37f824b298ee715cb413cc309fe7c52` (2026-10-16 01:29:16 UTC) exists. Its changed-file list includes earlier authenticated MGO portal HTML captures. The contemporaneous `00_CONTROL/CURRENT_STATE_RECONCILIATION.md` documents ten tracked captures containing a requester's name/email and subsequent vault/untrack operations. **History is still publicly accessible.**
- Earlier audit TS-001 reported account-specific matching strings in source code. Current `00_CONTROL/tools/classify_for_release.py` uses generic patterns without literal personal markers, but this does not purge past commits.
- Reviewed GitHub's first 100 recent main commits and reported branch/pull refs at the baseline. This is **not** a full scan of every reachable historical blob, tag or fork, or an independent verification of credential validity.
- Public portal access with ordinary free registration does not make the downloaded government record inherently confidential. **Account-specific identity/session artifacts are different from the official record itself.** Do not delete a public permit, plat or GIS original just because of the prior capture incident.

## Risk and required private follow-up

1. **Known historical personal-identification exposure:** verified by contemporaneous repository evidence and the earlier public commit's file list; scope/copy persistence remains unresolved. Avoid republishing personal fields in summaries.
2. **Possible authentication/session exposure:** **UNRESOLVED**, not proven a live credential by current source inspection. An authorized account holder/security reviewer must privately examine historic capture content and session artifact types, invalidate any affected live sessions or tokens as warranted, and retain proof privately. Never paste token values in public issues or reports.
3. **External history copies and forks:** not comprehensively assessed. Deleted-from-HEAD is not deleted-from-history; do not claim otherwise.
4. **No destructive remediation performed:** no Git history rewrite, repository-visibility change, evidence deletion, or fabricated rotation/approval record. Any rewrite requires owner authorization, privacy-preserving backup, signed rollback/remote coordination plan and impact review.
5. **Human decision still pending:** the independent privacy reviewer and publication approver must record a version-specific disposition for documents/derivatives before any broader neighborhood edition is authorized.

The separate 67-row [technical disposition register](INDIVIDUAL_PRIVACY_TECHNICAL_REVIEW_2026-10-16.csv) records what was actually screened and which binary/rights reviews remain. The mechanical `RELEASE_PRIVACY_CLASSIFICATION.csv` is **not** a publication approval register.
