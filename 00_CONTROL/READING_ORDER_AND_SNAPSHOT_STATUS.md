# Read this first: current conclusions versus historical snapshots

**Status:** living index of document roles, established after the October 15–16, 2026 reconciliation.

This project deliberately keeps prior errors and raw records as evidence of the research process. **A historical assertion is not an active verified claim.** When two files disagree, review their role, source, retrieval date, and whether an explicit correction superseded one of them. Never silently rewrite an original agency capture merely to make it agree with a newer interpretation.

## Current controlling documents

1. [Active assertion consistency](ACTIVE_ASSERTION_CONSISTENCY_2026-10-15.md): bounded source-backed facts and explicitly unknown questions; enforced by `tools/check_repository_consistency.py`.
2. [Claim ledger](EVIDENCE_LEDGER.csv), [claim→source links](CLAIM_SOURCE_LINKS.csv), [exhibit index](EXHIBIT_INDEX.csv), [source register](SOURCE_REGISTER.csv) and [chronology](CHRONOLOGY.csv): crosscheck **primary-record claims**. In multi-property statements the ledger's `source_exhibit` field uses `|` to list every separate primary exhibit.
3. [Current homeowner drafts](../15_RECONCILED_DRAFTS/README.md) and [five-page PDF](../15_RECONCILED_DRAFTS/pdf/Tom_Street_Reconciled_Public_Meeting_Draft.pdf): **unsigned DRAFTS**, not engineering or legal findings. The PDF manifest is authoritative for what went into the bundle.
4. [Open questions](OPEN_QUESTIONS.md) and [records/next actions](NEXT_ACTIONS.md): unknowns that may be resolved only by agency records, photos and professional site measurements.

## Historical files that may intentionally contain contradicted statements

| Frozen artifact | What it represents | Why its status is not a current assertion |
| --- | --- | --- |
| `INDEPENDENT_AUDIT_2026-10-16.md` | Independent review of historical commit `f929cc9` (170-file snapshot) | Its findings describe defects as they existed in that revision; several later received documented corrections |
| `INDEPENDENT_REMEDIATION_REGISTER.csv` | The independent audit's **51 original issue dispositions** | `REMEDIATION_STARTED_REVIEW_REQUIRED` and `OPEN` are **baseline audit labels**, not a continuously refreshed current-work tracker. Refer to newer committed changes and CI before judging present status |
| `CURRENT_STATE_RECONCILIATION.md` | An earlier local workstation/Git baseline | References paths, omissions and file counts that were true then; it is explicitly marked historical |
| `ACQUISITION_CHECKPOINT.md`, `ACQUISITION_RESULTS.md`, `PROGRESS.md`, `CORRECTION_HISTORY.md` | Previous discovery runs and corrections | Some original overly confident remarks are quoted intentionally to preserve the audit trail; their governing revisions are in current ledgers |
| `FINAL_FILE_SCOPE_INVENTORY_2026-10-15.csv` and `FINAL_REVIEW_READINESS_2026-10-15.md` | **Frozen 210-file** audit at commit `c76cef9` | A later repository contains additional tools/corrections; the old file count is not a current file-count claim |
| `../14_MEETING_PACKET/` and `../releases/2026-10-15/` | Former public-style meeting packets | **WITHDRAWN/SUPERSEDED**, retained for traceability, not current distribution |

## Important unresolved facts, not internal contradictions

- 2266 appears in historical MGO addresses but no entry was found in the archived current Property Appraiser street-roll query. We have no documentary basis to explain any renumbering.
- ERP 9220-2 is a nearby research lead, not a permit with proven coverage of the two lots.
- Inspection instructions, fees, task assignments and customer-portal attachment responses are distinct facts, **not proof of approved/stamped as-built drainage plans**.
- The 2023 and 2024 DEP quarterly PDFs are **filing indexes**, not the signed underlying consent orders.
- Fifteen resident JPEG **copies** hash-matched a separate private archive; device originals, authentic capture times, and permission for public release remain unresolved.
- Five foundational Chapter 119 drafts plus two supplemental unsent drafts exist; no proof of transmission or receipts.
- Engineering causation, drainage capacity, boundary lines, historical grade and maintenance responsibility require plans, survey measurements and agency responses.

**Quality rule:** Only claim zero **known internal conflicts among tested current assertions** when the latest CI checks pass. Do not claim zero unanswered questions, no historical errors, or complete acquisition of engineering records.

## October 16: verified road classification and remaining questions

**October 16 follow-up:** the target road is **County Maintained** in County GIS; asset ownership/maintenance remains unresolved. Actual Ordinances 2025-25 and 2026-03 and the generic grading guideline are now preserved. Clerk-certified electronic transmission dates are not separate Department of State filing receipts. No lot-specific approved plan, exemption, surveyed invert/outfall, or matched ERP/CGP authorization was obtained. See [17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md](../17_CURRENT_RESEARCH/FIVE_QUESTION_FINDINGS_2026-10-16.md) and its source links.
