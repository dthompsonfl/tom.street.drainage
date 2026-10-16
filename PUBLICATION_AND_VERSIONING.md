# Sharing, correcting and versioning the Tom Street evidence

**Public repository: treat anything committed as permanently discoverable.** Even deleting a file does not remove its earlier Git history or copies.

## Neighbor review versus official submission

The current Markdown and draft PDFs are **available for neighbor fact-checking**. That means neighbors can read them and point out mistakes; it does **not** mean the letters have been signed, sent, or approved by the County. See [the review guide](NEIGHBOR_REVIEW_GUIDE.md). Individual households should keep their own versioned notes and original evidence privately.

## Which version should neighbors use?

Start with the [README](README.md), then the [current draft folder](15_RECONCILED_DRAFTS/README.md) and [plain-English source guide](PUBLIC_EVIDENCE_GUIDE.md). Everything inside [14_MEETING_PACKET](14_MEETING_PACKET/RELEASE_README.md) and [releases/2026-10-15](releases/2026-10-15/) is **SUPERSEDED**. Earlier documents are kept as historical research records and may contain mistakes.

**Draft does not mean approved.** The Markdown sources and built PDFs are published for review. No packet becomes a signed, sent or Commissioner-approved document merely because a CI workflow passes.

## Safe five-step process

1. **Receive privately.** A neighbor keeps the unmodified original photo, document or email and tells the coordinator privately where it came from. Never ask anyone to upload personal material to a public GitHub issue.
2. **Log it.** Assign an evidence ID, date received, agency/source, record date, filename, original SHA-256, location in protected storage and permission/restrictions.
3. **Check the claim.** Compare the exact assertion with its supporting source, date, parcel and limitations. Record contrary evidence or uncertainty. Do not present inference as an official finding.
4. **Prepare a public-safe copy.** Remove unnecessary private details and metadata; label it DERIVED / REDACTED and link it to the retained original evidence ID. Check the rendered PDF or image, not just its raw text.
5. **Review and publish.** A homeowner checks the words being attributed to them. A second reviewer checks the source link, privacy, references, dates and that the current PDF matches current text. Record review status and commit ID.

## How to handle revisions

- Correct **current homeowner summaries** and link to the new record with the date it was obtained.
- Preserve official original bytes. Do **not** overwrite source imagery, agency JSON or prior audit logs to force agreement.
- Keep the old claim and correction in the [contradiction log](00_CONTROL/CONTRADICTION_LOG.csv) if the correction is material.
- Use descriptive changes: "records: add County response dated YYYY-MM-DD" or "docs: correct uncertain inspection wording." A Git commit records when the repository changed, not when an event happened.
- Never report an agency request as sent without an outgoing copy and transmission/receipt evidence. Never claim a phone call was an official decision without dated notes and verification.

## Public release checklist (must be manually checked)

- [ ] Homeowner or speaker personally approves every first-person statement.
- [ ] All names, address/parcel IDs, permit IDs, dates and current-versus-archived statuses are checked.
- [ ] Every consequential claim has a traceable source or is explicitly marked an observation.
- [ ] No statement converts a proposed pipe, assigned task or online search gap into a proven field fact.
- [ ] Any private contacts, original photos, GPS and account data are absent from public files and document metadata.
- [ ] Superseded packets are not part of the distribution package.
- [ ] The printable PDF matches the current Markdown and is visually legible.
- [ ] The County receipt, responses and case numbers are recorded separately from unsent drafts.
- [ ] An actual person approves the specific version for sending.

**Until all release gates are met, the public meeting packet remains DRAFT_NOT_APPROVED_FOR_EXTERNAL_DISTRIBUTION.** The repository's current automated tests are technical checks, not a privacy or engineering sign-off.

## Remaining unavoidable outside dependencies

The County must produce its governing plans, surveys and records; a qualified professional must measure actual conditions if required; agencies must confirm ERP/CGP applicability; neighbors must authorize release of their material. Nothing in a repository refactor can manufacture those facts.

**Known historical privacy issue:** earlier authenticated captures may still be reachable through Git history. A history rewrite or credential response requires separate owner-reviewed remediation. Do not assume changing today's files solved historic exposure.
