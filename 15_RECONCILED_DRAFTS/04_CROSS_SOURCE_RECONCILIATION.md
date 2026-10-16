# Cross-source reconciliation and release blockers
Date: 2026-10-15. **This is an audit log, not a certification of completeness.**

## Compared materials and access boundary
- Current GitHub `main` files, including saved official PA/MGO JSON, inspection summaries, requests, and historical release package.
- Project Library textual audits `Tom_Street_Independent_Audit_2026-10-15.md` (18 principal findings) and `00_Independent_Audit_Report.md` (Gemini Argon assessment of another workspace).
- Project Library metadata for `tom.street.drainage-main (1).zip`, `Tom_Street_Corrected_Workspace_2026-10-15.zip`, `Tom_Street_Drainage_Investigation_Complete_Workspace.zip`, `Tom_Street_Corrected_Meeting_Packet_AND_Evidence_Workspace_2026-10-15.zip`, plus newly supplied `Tom_Street_Record_Preservation_Toolkit_2026-10-15(1).zip` and `Tom_Street_Drainage_Investigation_Complete_Workspace(1).zip`.
- **Limitation:** ZIP bytes of Library archives were not available to extract in this execution. Metadata and prior independent audit reports are *not* equivalent to current independent per-entry archive verification. No claim is made that all historical archives/photos have been merged into GitHub.

## Material corrections identified
| Issue | Earlier claim | Current disposition |
| --- | --- | --- |
| Permit status | Some derivative permit records said `None` | Raw MGO `data.status` is `Active` as captured; corrected the two public-facing permit records and inspection headers |
| Drainage-certification workflow | `Assigned` means the certification does not exist or was never submitted | **Unproven**; the task is not proof of document presence, absence or breach |
| Fee and document availability | Grading/erosion fee means specific approved plans must exist | **Unproven**; fee does not demonstrate a particular file |
| 2266 identity | Never existed | Historical MGO permits use 2266 although the current PA roll does not; disposition unknown |
| 2268 historical mobile home | 2000 permit proven to relate to current 2268 lot | **Unproven**; cited historic parcel points to present 2274 |
| 2260 parcel | Some engineering summaries put 2260 on `...0QQ00-1030` | Independent audit indicates `...0QQ89-0000`; current `...1030` is associated with 2270; re-check official export |
| 2264 stormwater connection | Inspector's installation direction proves as-built pipe/easement/capacity | **Unproven** until installation and site/legal geometry documented |
| 2268 flat roadway | Qualitative grade instruction proves numeric grade/freeboard | **Unproven**, no measurements |
| Nearby ERP 9220-2 | Proximity confirms applicable development permit | **Unproven**, project/parcel intersection not established |
| ORB 3492/700 | Official deed image recovered and ownership proved | Saved artifact is a Clerk search-results grid, not a recorded deed image |
| 2026 LDC source date | PDF CreationDate 2026-01-13 equals ordinance adoption date | **Incorrect equivalence**; distinguish cover/ordinance date, internal PDF metadata, and effective applicability; review actual enacted revisions |
| Archived original photos | A past checkout had none so entire homeowner project has none | **Incorrect inference**; project Library includes separate photo packages, which require original/EXIF and permissions review |

## Outstanding verification and release gates
1. Acquire/read/check SHA-256 of *all* source ZIP bytes, especially two newest supplied archives. Crosswalk contents/hashes, provenance, versions and all photo originals; preserve originals separately from derivatives.
2. Correct older source narratives/registers containing the above claims; rebuild downstream CSVs and PDF outputs and compare headings, dates, citations and exhibit pagination.
3. Confirm County LDC editions and actual controlling sections as of March 2026 permit issuance, including any applicable exceptions and effective amendments; do not mistake PDF CreationDate for ordinance effective date.
4. Obtain approved grading design, site surveys, final certifications, ROW/swale/invert survey, true site outfall and erosion controls, actual Clerk deed instrument, documented ERP scope and current permit status.
5. Verify primary Florida case-law opinions and subsequent treatment; legal rules are context, not proof of a Tom Street violation.
6. Recheck resident photographic originals, authorizations, EXIF and accurate exhibit numbers. **Do not automatically publish the archived photo packages into a public GitHub repository.**
7. Render and visually inspect readable PDFs from these revised Markdown drafts; regenerate release manifest and SHA256SUMS; run privacy, source-reference and print-layout tests.
8. Keep all five agency requests `DRAFTED_NOT_SUBMITTED` until proof of transmission is recorded.

**Disposition:** These Markdown documents are the *current revised drafts*. No distribution-ready, evidentiary or legally conclusive packet is certified.
