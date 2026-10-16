# Receiving records and updating the Tom Street evidence registers

**Operational procedure | October 16, 2026 | Public guidance, not a confirmation of submitted requests.**

The purpose is to receive agency productions and neighbor observations without losing originals, falsely marking draft requests as submitted, or publishing a resident's personal information. The repository is public; the private evidence store is separate and permission controlled.

## A. When a records request is actually sent

1. Check the requested custodian and exact permit/parcel identifiers. Use the current draft in `13_PUBLIC_RECORDS_REQUESTS/` only after the individual sender approves its words. Separate Chapter 119 existing-record requests from service/inspection requests.
2. Store an exact outgoing copy, full attachment set, method and send timestamp **privately**, with any acknowledgment or transmission receipt. Avoid putting a resident's name, phone, email, authenticated portal session or raw email headers into public Git history.
3. Only after checking that evidence, update the applicable `00_CONTROL/MISSING_RECORDS_AND_ACTIONS.csv` row: `submitted=TRUE`, actual `submission_date`, and a non-sensitive `receipt_id`. Preserve the original outgoing proof in the private evidence store; record only a safe reference in the public log.
4. Update the request tracker with the custodian, response date, expected production batches, fee estimate and unanswered items. A drafted request is **not sent**, and a transmitted request is **not a completed records production**.

## B. When a document or response arrives

1. Preserve the source file **exactly as received** in controlled storage. Assign a unique source ID; record its original filename, custodian, record date, time received, retrieval URL (if public), SHA-256 and byte count.
2. Examine file type and pages. Do not confuse a portal error, placeholder, search index or download redirect with the requested original document. Retain failed attempts and limitations in the search/acquisition log.
3. Determine privacy/release scope. Official files may still include signatures, account fields, personal addresses and embedded document metadata. Restrict access until reviewed. Do not commit unreviewed documents to public GitHub.
4. Link the production to each request and gap it actually addresses. Update `SOURCE_REGISTER.csv`, `PERMIT_DOCUMENT_INVENTORY.csv`, `EXHIBIT_INDEX.csv`, `CLAIM_SOURCE_LINKS.csv` and `CHRONOLOGY.csv` **as applicable**, with exact provenance and correct parcel scope.
5. Change a gap to closed **only after** a source-linked closure entry demonstrates its exact closure criteria. A partial production, no-match query, unanswered email, or future promise does not close it. Record contrary and alternative evidence rather than deleting it.
6. Review affected neighbor brief/letters and regenerate PDFs. The revised source narrative must still distinguish County records, resident observations, possible explanations and unknowns. No generated PDF is a signed or submitted letter without separate human action.

## C. Source identity and version safeguards

- The 1946 Crescent Shores original **PLAT A/70**, two sheets (the second marked 70 A), is already preserved. Continue obtaining later deeds, Lot QQ conveyances, recorded easements and maintenance rights. Do not reclassify the original plat as absent.
- Archived MGO permit status (Active when captured) is not live status. An assigned as-built task does not prove filing or absence. County GIS road maintenance classification does not determine ownership/maintenance of individual structures.
- A consultant or surveyor should supply datum, benchmark and documented measurement locations before current elevation comparisons are treated as measurements. GIS imagery and terrain models are context, not certified 2026 field grades.
- Unverified NWFWMD/FDEP proximity records do not establish regulatory coverage, an exemption, or misconduct.

## D. Mechanical checks and release decision

Run in a checkout from repository root:

```bash
python -m unittest discover -s tools -p 'test_administration.py' -v
python tools/check_administration.py --strict
python tools/report_current_status.py
python tools/autonomous_evidence_pipeline.py --mode full --dry-run
```

These are **read-only** checks. The existing `reconciled-public-packet.yml` workflow also builds draft PDFs, validates evidence/source joins and regenerates privacy-inventory hashes. A passing automated check is not a homeowner sign-off, an independent engineering review, a County inspection or a certification that no private evidence was exposed in historic commits.

## E. Publication and correction

Before any public summary is published, obtain the resident's approval for attributed statements and independent source/privacy review. Save the public-safe derivative separately, with its source ID, source date, redactions and version. Consult [`PUBLICATION_AND_VERSIONING.md`](../PUBLICATION_AND_VERSIONING.md). Avoid posting original residents' media, file metadata, complete contact details and authenticated pages in a public issue or commit. Historical Git privacy exposure requires a separate authorized review; deleting a current file alone does not erase earlier history.

## F. Optional controlled helpers for private originals and request receipts

- For an **external, privately stored** evidence folder, `python tools/private_evidence_audit.py --vault /your/private/vault` computes counts and duplicate hashes without printing filenames, hashes or location metadata. Add `--private-manifest /your/private/vault/audit.json` only when the destination is permission controlled. The audit does not establish camera authenticity, capture date or permission to publish.
- To record an **actually transmitted** records request, use `python tools/record_submission_receipt.py --gap-id GAP-01 --sent-date YYYY-MM-DD --public-reference REF-001 --private-proof /your/private/outgoing.eml --private-audit /your/private/custody/receipt.json`. This first shows a read-only preview and current register SHA-256. Only after a person personally verifies the outgoing/acknowledgment evidence should they rerun it with `--apply --confirmed-proof-reviewed --expect-sha256 <value-from-preview>`. No email is sent by the script. The public reference must be non-identifying, and the original proof stays outside Git.
- `tools/test_private_operations.py` uses only synthetic fixture files; no resident photographs or real receipt data are used in tests. Never place proof files, private audit manifests or completed forms in `18_NEIGHBOR_TOOLKIT/` or any other public repository directory.

## G. Prevent historical code from overwriting current evidence

Historical scripts in `00_CONTROL/tools/` may contain frozen assumptions about earlier permits, parcel labels and the original 2026 investigation. The archived `build_registers.py`, `build_registers2.py`, `build_canonical_registers.py`, `build_claim_source_links.py`, `build_public_extracts.py`, and `build_packet_pdfs.py` are intentionally non-executable as command-line generators. **Do not remove their safety guards or substitute their fixed historical arrays for current evidence.** Use current append-safe reconciliation, actual agency records and source-backed manual review. The CI `test_retired_builders.py` checks that each legacy main entrypoint stops before writing any CSV or public handout.
