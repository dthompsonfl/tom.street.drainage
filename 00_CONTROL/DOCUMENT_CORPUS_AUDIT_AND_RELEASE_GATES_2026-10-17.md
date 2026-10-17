# October 17, 2026 | Document corpus audit and release gate

**State: AUTOMATED CORPUS SCREEN COMPLETED; HUMAN SEMANTIC AND FULL-PDF VISUAL REVIEW INCOMPLETE.**

**Provenance:** Repository dthompsonfl/tom.street.drainage, baseline main commit 6c4813317b7e57557bb746cae3e6c5b3402b215d. Successful automated review run [39063897425](https://github.com/dthompsonfl/tom.street.drainage/actions/runs/39063897425) scanned review commit 4eca604cc2d942ff854bb3dfba6ebc038ad116e5. The seven-day unapproved artifact contains exact per-file and per-location CSVs plus JSON summary. All source documents are left untouched. Git commits, automated checks and source hashes are **not** external approval.

## Verified machine coverage

| Type | Files | Coverage | Limit |
| --- | ---: | --- | --- |
| Markdown | 101 | Each physical text line traversed and risk/reference patterns screened | Does not validate every sentence, link anchor or external URL |
| HTML | 21 | Each physical text line traversed | Many are archived official/public-system captures, not editable narratives |
| TXT | 7 | Each physical text line traversed | Includes dated metadata/checksum snapshots |
| PDF | 38 | All 1,375 pages parsed for available text; 0 PDF parse errors | Extraction is not a visual/legal/engineering content review |

**Total:** 167 tracked documents, 129 text files / **22,460 physical source lines**, 38 PDFs / **1,375 pages**, 93,382,953 source bytes at the pinned scan commit.

**Pages without extractable PDF text: 73.** Two are the original scanned Crescent Shores Clerk PLAT A/70; 71 belong to the original NOAA 2018 Panhandle acquisition report. These are **not** demonstrated empty pages. They require visual reading of imagery, maps and content rather than a fabricated OCR transcription.

The automated scan identified seven possible parcel-association matches in historic correction/acquisition narratives, and eight undated-looking permit-status statements in **superseded** meeting materials and their PDFs/HTML. The old wrong parcel numbers are intentionally quoted to record correction history. Treat flags as leads requiring manual context review, not as independently confirmed current errors. The superseded packet is not distribution-ready. Relative Markdown links were checked against existing tree files or directories; external site availability and assertion support were not certified.

## Actual visual review performed in this session

A pre-existing **unapproved** neighborhood candidate artifact was downloaded and the following four PDFs were rendered at 125 dpi for contact-sheet visual inspection:

- Current reconciled draft meeting PDF: five pages.
- Neighbor documentation blank master: eighteen pages.
- Event observation form: one page.
- GIS reference map: one page.

**25 pages received limited visual contact-sheet examination.** Separately, all **five current combined packet pages** were rendered at 175 dpi and visually read page-by-page against the corresponding Markdown narratives, including parcel and permit IDs, headings, archived-status caveats, unsubmitted-request wording and draft disclaimers. Those five pages appeared legible without visible clipping, missing sections or broken page numbers. This is **not** an exact-character PDF/Markdown parity test, accessibility certification, approval of attribution or permission to distribute. The GIS map is a location reference, not a survey or engineering elevation map.

## Material source reconciliation

- The original historical [Crescent Shores Clerk Plat A/70](../02_PROPERTY_AND_PARCELS/PRE_REQUEST_OCT16_PRIMARY_LOOKUPS/ORIGINAL_CLERK_PLAT_BOOK_A_PAGE_70.pdf) was obtained. Later Lot QQ title chains, deeds, splits, easements, road acceptance and maintenance duties remain unknown. Parcel summaries and the derived permit-document inventory have been corrected on the review branch. **Preserve the original scan and metadata.**
- Archived August 6, 2026 and October 1, 2026 inspections document a pipe/inlet work instruction and a passed pre-pour entry for 2264. No signed approved design, installed pipe profile, invert measurements, receiving outfall or hydraulic evaluation has been obtained.
- Both active-project IDs showed Active **when archived in October 2026**. The stored status-refresh JSON is derived from older captures, not evidence of a new live MGO query. Current approvals, COs, inspection and certified-as-built states remain open.
- FDOT public indices list county collections for 2022 and 2025, but site-covering original frames and exact capture dates are not in the evidence archive.
- The original 509-page County LDC PDF is machine-text-extractable, but parsing does not establish the permit-date controlling amendments, exceptions or whether any given section governs these lots.
- No drainage-caused damage, regulatory violation, improper grading, installed-system inadequacy, or specific legal fault is professionally established. Historical stormwater mapping may predate the new construction.
- The eight current public-request draft files contain nine agency-specific request/service templates. There are no verified submissions or receipts.

## Human signoff required before literal full-review and release claims

1. Individually read each active Markdown narrative and reconcile all factual claims, quotes, dates, scope and contradictory evidence to primary records. Mark old errors historical rather than erasing evidence.
2. Visually inspect all relevant original PDF pages, explicitly including 73 non-text pages and all drawings, tables, maps and footnotes. If literal **all-pages** approval is intended, document human visual review across the full set of 1,375 pages.
3. Compare current Markdown sources against every derivative PDF to verify text, page order, claim numbers, citations, disclaimer language, legibility, print usability and accessibility.
4. Verify March 2026 applicable laws and code amendments from primary instruments, not PDF creation metadata; request current permit status, County approved plans, installer/inspection evidence and surveyed actual outfall.
5. Secure homeowner approval of first-person drafts, independent source/privacy reviewer signoff and authorized immutable-edition publication approval. A successful CI run must not imply any of these human decisions.
6. Track real County/Clerk/FDOT request transmission and response receipts. Neither an unsent template nor a portal empty customer-files result establishes that a record does not exist.

**Reproduction:** Execute the [read-only corpus scanner](../tools/audit_document_corpus.py) with the pinned PDF parser requirements and an output directory outside the checkout, or inspect the [read-only workflow](../.github/workflows/document-corpus-review.yml). Reports are review metadata, not original primary evidence.

**Next practical decision:** focus on approved County engineering drawings and reliable physical surveys before further conclusions. The source archive is extensive; engineering facts are still incomplete.
