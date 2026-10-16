# Tom Street | Reconciled homeowner drafts
Prepared 2026-10-15. **Status: SOURCE-RECONCILED, EVIDENCE-LIMITED DRAFTS; NOT AN APPROVED FINAL PACKET.**

These documents supersede the narrative text in `14_MEETING_PACKET/`. The old PDF files and `releases/2026-10-15/` ZIP are retained *solely for historical traceability*; their SHA checks establish file identity, not factual accuracy. They must not be circulated as the final meeting packet.

## Start here
- `01_HOMEOWNER_BRIEF.md` — short, evidence-bounded explanation
- `02_COUNTY_LETTER_DRAFT.md` — homeowner request for records and engineering clarification
- `03_PROXY_MEETING_NOTES.md` — prepared remarks, without legal or engineering allegations
- `04_CROSS_SOURCE_RECONCILIATION.md` — conflicts and release blockers

## Evidence status
Saved Property Appraiser and MGO project records support these address/parcel/permit pairs **as of their capture date**:

| Site | Parcel | Permit | Captured MGO status |
| --- | --- | --- | --- |
| 2264 Tom St | 21-2S-26-0780-0QQ00-1020 | BP-2026-1621 | Active |
| 2268 Tom St | 21-2S-26-0780-0QQ00-1490 | BP-2026-1612 | Active |

This review does **not** establish violation, flooding causation, drainage capacity, historic fill thickness, or maintenance liability. Open `Certified Drainage as Built: Assigned` tasks **do not prove a document exists, is missing, or is late**. Inspector remarks are instructions/observations, not sealed engineering drawings or proof of completed installations.

The `13_PUBLIC_RECORDS_REQUESTS/` directory contains **five foundational Chapter 119 record-request drafts plus two supplemental unsent drafts** (FDEP construction stormwater and County Public Works service request). All seven are draft-only; **no transmission or receipt has been verified**. The original, approved lot-grading documents; surveys; as-builts; easements; outfall measurements; and relevant agency approvals have not been recovered as verified signed originals.

## Release and preservation rules
The repository is **public**. Do not push homeowner original photos, embedded EXIF/GPS metadata, identifying residents' details, authenticated permit captures, login/session state or raw investigation archives without express consent, privacy review, and evidence-custody controls. Prior private-data publication in Git history was identified in `00_CONTROL/CURRENT_STATE_RECONCILIATION.md`; removing tracked files does not remove their old Git history.

Additional Project Library inputs include `Tom_Street_Record_Preservation_Toolkit_2026-10-15(1).zip` and `Tom_Street_Drainage_Investigation_Complete_Workspace(1).zip`. Their bytes **were obtained, CRC-tested and hashed** in the subsequent continuation run. The toolkit SHA-256 is `3e667a7794f8ee098ff35c56df77a2ad613c8fbbd855b42a55b9cc8bd4494e53`; the investigation-workspace SHA-256 is `a459d9f3cbeaf63548c05badac0981333911275f47fabad2f12a58d8fe72506a`. The nested private resident package contains **15 JPEG copies, all 15 matching archived hashes**. Original phone-capture authenticity and times are **not verified**. Other earlier Library archives not exposed as byte streams still need comparison; see `16_ARCHIVE_RECONCILIATION`. Earlier independent audits report missing primary plans/photos in *their particular source archives*, not necessarily in the wider homeowner collection.

**Release gate:** review every primary-source quotation and snapshot date; reconcile all photo originals/permission; validate current permit statuses and applicable code edition; regenerate and inspect print PDFs; sign off by homeowner. Do not relabel as FINAL before those steps.

## Printable packet generation

The canonical public text comprises `01_HOMEOWNER_BRIEF.md`, `06_COMMISSIONER_COVER_LETTER_DRAFT.md`, `02_COUNTY_LETTER_DRAFT.md`, `03_PROXY_MEETING_NOTES.md`, and `05_RECORDS_STATUS_AND_FOLLOW_UP.md`. Run `python3 tools/build_reconciled_packet.py` to build five Letter-size PDFs, one combined packet and checksum/manifest files. The release status remains `DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION` until homeowner verification of current records and a print review. Never reuse the superseded `14_MEETING_PACKET` PDFs as final.

## Preserved legal source PDFs

Three previously missing **public primary/legal record PDFs** were downloaded and byte-hashed via the governed GitHub workflow: the 1989 Florida Supreme Court corrected *Westland* opinion and two FDEP final-order quarterly **indexes**. These are under [`08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/`](../08_LEGAL_AND_REGULATORY/SOURCE/PRIMARY_AUTHORITY/) with an acquisition manifest. No signed DEP consent order or lot-specific approved engineering plan was recovered by this legal-source acquisition. This legal-reference annex is **not part of the current five-page draft homeowner meeting handout**.
