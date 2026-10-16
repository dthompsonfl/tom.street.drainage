# Independent archive-byte reconciliation | 2026-10-15

**Status:** two newly attached ZIPs verified offline. This does not certify official engineering document completeness.

| Supplied archive | SHA-256 | Files (non-directory entries) | Integrity |
| --- | --- | ---: | --- |
| Tom_Street_Record_Preservation_Toolkit_2026-10-15(1).zip | `3e667a7794f8ee098ff35c56df77a2ad613c8fbbd855b42a55b9cc8bd4494e53` | 21 | ZIP CRC passed |
| Tom_Street_Drainage_Investigation_Complete_Workspace(1).zip | `a459d9f3cbeaf63548c05badac0981333911275f47fabad2f12a58d8fe72506a` | 79 | ZIP CRC passed |
| Nested seed Tom-Street-Drainage-Investigation.zip | `4b40a6bd00f277c2e4ad73d4d48aa9f7bef9ed7802e3d773171d1253b4cab7d8` | 47 | ZIP CRC passed |
| Nested corrected resident submission ZIP | `e262c4997352960c17f31343544561f3bb883793c6d81d54514e8ef8cbb6553d` | 32 | ZIP CRC passed |

**179 nested and top-level file entry positions** were read and SHA-256-hashed independently (21 + 79 + 47 + 32). The underlying files may duplicate one another; do not count them as 179 independent evidence sources.

## Resident photographs — private evidence

- 15 JPEG copies extracted from the nested corrected resident package; **15/15 matched its original SHA-256 inventory**.
- **0/15** have the standard EXIF DateTimeOriginal value; **1/15** retains GPS fields. Other location and capture-time assertions are not independently verified; the one GPS reading has non-trivial positional uncertainty.
- Exhibit labels P01–P15 are archive inventory labels, not surveyed site positions or proof of cause.
- Photos visibly depict construction frontage/ponding and separate nighttime storm conditions. They are observations, not quantified runoff, field-survey or violation proof.
- **Do not publish the JPEG copies, EXIF, detailed custody register or private ZIP on this PUBLIC repository** without explicit approval and privacy review. The full byte-level inventories remain in the separate local private working area.

## Legacy workspace source-evidence defect

The independently inspected 79-file workspace has **45 source-register rows**. Every listed `Local_Preserved_Path` resolves to a Markdown or TXT file (**31 MD / 14 TXT**) rather than original native governmental permit/deed/drawing PDFs. The local report's title `FINAL_SUBMISSION` and generated PDFs do not change this evidentiary limitation. The worksheet cites 13 material claims and contains 10 drafted agency requests with no proof of dispatch.

## Highest-priority records still missing

Approved lot grading plans, original/revised signed engineering drawings, drainage calculations, preconstruction and current surveys, recorded deeds/plats/easements, accurate ROW/invert/outfall and maintenance plans, certified completed works, and time-stamped verified site-level rainfall observations. The permit data and LDC are context, not proof of deficiency.

## Audit provenance and limitations

Verification performed with Python `zipfile` CRC and independent SHA-256 of each member, using the *two exact newly supplied attachments*. The archived source control data and resident evidence bytes were not modified. Additional older Library archives not provided as byte streams cannot be claimed to have been compared in this run. No inspection, official record certification, hydraulic modeling or legal adjudication was performed.

**Release decision:** Revised homeowner text may be used as an *accurate request for documents and review*, subject to homeowner validation. A causation/violation submission is not ready.
