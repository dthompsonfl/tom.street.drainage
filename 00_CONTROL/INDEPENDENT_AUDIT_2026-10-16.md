> **Historical independent audit of Git commit `f929cc9` (170 files).** This report is preserved as an as-of snapshot, not a statement of the updated branch current readiness. See `RESEARCH_STATUS_AT_COMMIT.md` and `INDEPENDENT_REMEDIATION_REGISTER.csv`.

# Tom Street Drainage Investigation: Independent Repository and Evidence Audit

**Audit date:** October 16, 2026 (UTC; corresponding October 15, 2026 U.S. Central evening)  
**Repository:** `dthompsonfl/tom.street.drainage`, default branch `main`  
**Live Git tree/HEAD examined:** `f929cc9d207e201cc554cda51edf9e097280d2da`  
**Uploaded source:** `tom.street.drainage-main (1).zip`, SHA-256 `7a208cbd59cbe5e2cd71d94c0c3a1a696d7d57fb0ddcae356d0d5bf99ed68bb5`  
**Subject:** 2264 and 2268 Tom Street and connected Tom Street roadside drainage, Navarre, Santa Rosa County, Florida.  
**Use:** Internal evidence-quality review. Not a legal opinion or licensed engineering determination.

## Executive decision

**Hold the existing public meeting packet for correction.** It is suitable as the basis for a neutral request for official documents, but it is **not release-ready in its current form**, because some statements go beyond their sources, the package lacks almost all original public-release-designated exhibits, privacy risks remain on the public Git repository, and automated tests inaccurately report certain controls as passing. No justified finding that Holiday Builders caused a drainage problem or violated a particular requirement can yet be made.

**Preserve the original evidence.** The highest-value next actions are (1) prevent further public exposure of personal/session information; (2) correct assertions in all meeting/source documents; (3) obtain county-approved engineering documents and field inspection; (4) submit the five prepared Chapter 119 requests with homeowner authorization; and (5) conduct targeted survey/engineering work and real storm-event documentation. The repository should not represent any of these outside-dependent actions as completed without receipts or source files.

This audit found **51 tracked gaps, defects, and open dependencies**: **9 P0**, **37 P1**, **5 P2**. See `Tom_Street_Repo_Gap_Register_2026-10-16.csv`, which identifies each finding, concrete source path, remediation, and testable closure criterion. P0 includes evidence not yet obtainable from this repository; that is a blocking research dependency, not necessarily a code defect.

## 1. Exact scope, inventory, and independent checks

| Item | Audited result | Important qualification |
|---|---:|---|
| Archive files / tracked live repository blobs | **170 / 170** | All paths, byte lengths and Git blob SHA-1 values agreed with live GitHub `main` tree. |
| Combined file bytes | **11,776,474** | Excludes ZIP directory entries. |
| ZIP source SHA-256 | `7a208cbd59cbe5e2cd71d94c0c3a1a696d7d57fb0ddcae356d0d5bf99ed68bb5` | Immutable starting snapshot; do not confuse with previous 119-file repository archive. |
| JSON files | **52**, parsed | Parsing tests syntax, not independently authenticated meaning. |
| CSV files | **16**, parsed, rows analyzed for claim/evidence/control registers | Some standalone event registers are not agency evidence. |
| Python source | **36**, syntax/AST inspected; selected evidence-control code examined in detail | No authenticated live portal tests or bulk scraper execution performed. |
| Python bytecode | **2**, hashed and format inspected | Inconsistent with repository statement that compiled caches were removed. |
| PDF files | **6**, structurally parsed | The **509-page LDC** was text-extracted with relevant clauses inspected; the five meeting PDFs total **15 pages**, rendered and examined. This is not a legal opinion on all 509 pages. |
| PNG images | **2**, checked as redacted permit-screen derivatives | They are not homeowner flooding photographs. |
| Public release ZIP | **22/22 members** readable and matching separately published checksum manifest | The checksum file and release manifest are **not inside the ZIP**. |
| CSV claim ledger | **20 claims**, **18** with supporting local files and matching recorded hashes | The other **2** correctly describe missing field evidence; a hash match does not prove a claim is true. |
| Public exhibit index | **15 source exhibits**, all local files exist/hashes match | **14 of 15** underlying source-exhibit paths are **not packaged** for recipients. |
| Source register | **41 records**; **34 local source files** present and hash/size matched | Seven are leads, unavailable/errored or other nonlocal status; older `AUTHENTICATION_REQUIRED` rows not superseded after success. |
| Evidence manifest | **139 rows**; **10** restricted-vault paths not present in public repo | Two manifest hashes/size entries are stale, including self-reference. |
| Privacy classification | **165 paths**, all marked PUBLIC | The actual tracked repository has **170** files; machine classification is not an approval for public release. |
| Chronology | **16 events** | Original homeowner flood-event observation remains undated/unobserved. |
| Design vs field comparison | **10 entries** | None establishes an engineering comparison of approved vs surveyed site conditions. |
| Missing-records tracker | **22 entries** | **19 `REQUEST_DRAFTED`, 3 `NOT_OBTAINED`**. Five distinct request letters exist; **zero submission receipts**. |

The source and GitHub tree were cross-reconciled at the same snapshot; the live Git branch may advance after the date of this audit. The per-file inventory includes `review_depth` and limits for **all 170 members** to distinguish structural review from substantive verification. This audit does **not** assert independent rereading or on-site verification of every one of the 885 MGO search matches or every NOAA measurement, nor that every sentence across 509 code pages has an expert legal interpretation. Treat assertions about unobserved engineering conditions as unresolved.

### Original evidence chain

- The target county Property Appraiser exports and permit API snapshots are intact in the repository. The key permit/evidence files support the corrected parcel mappings and inspector comments as *archived county database observations*.
- The legacy ZIP and earlier independent audit are not a second independent agency source. The 119-file snapshot existed before these changes; the local agent did not possess the separate independent audit files. Its `CURRENT_STATE_RECONCILIATION.md` transparently reports that limitation.
- **A saved permit task marked `Assigned`, a paid permit fee, an inspection direction, and an empty public customer document array are four different facts.** None alone proves a plan exists, has been installed, is adequate, or is overdue.

## 2. High-consequence defects in meeting/public files

### A. As-built status: unsupported certainty (TS-008, TS-014)

`14_MEETING_PACKET/01_EXECUTIVE_HOMEOWNER_BRIEF.md:105-106` expressly says the sealed engineer's certification *does not exist* and *cannot exist* until houses are finished. `14_MEETING_PACKET/03_PROXY_SPEAKING_NOTES.md:65-77` repeats the conclusion. `00_CONTROL/PROGRESS.md:49-50` says the item has not been submitted or approved. But the source is an MGO task labeled `Certified Drainage as Built: Assigned`, not an agency confirmation that the relevant document never existed or was rejected. Under the LDC, §4.04.01.D.1.g describes a sealed conformance letter at substantial completion for applicable lots, while §4.04.01.E states an as-built gate before CO for all lots. **Correct statement:** as of the archived snapshot both administrative tasks remain open, and no certified as-built was obtained through the accessed source; the County must confirm filing, acceptance, applicability, and current status. Distinguish `no CO found in searched system` from `no CO has been issued`.

### B. Roadside connection: instruction versus installed work (TS-009, TS-010)

The August 6, 2026 2264 inspection recorded an instruction for roughly 100 feet of 12-inch perforated ADS pipe with sock, inlet boxes, and work referencing 2260 and 2270 Tom Street. The meeting brief (`...HOMEOWNER_BRIEF.md:62-63,137-143`) and speaking notes (`...PROXY_SPEAKING_NOTES.md:39-50`) instead describe a completed design and installed discharge connection on neighboring **private** properties. The record does not identify exact installed locations, property boundaries, positive outfall, flow direction, approved drawing or final acceptance. Similarly, September 10, 2026's `Flat; Match Existing roadway Grades` does **not** establish a level lot or measured driveway slope. Revise all derived Markdown/HTML/PDF to quote directions and identify the unknowns. Obtain ROW/county plans, location survey, invert elevations and as-built before answering where runoff goes.

### C. Unsupported fee-to-plan inference (TS-011)

`ACQUISITION_RESULTS.md:106` and both parcel `DOCUMENT_COMPLETENESS.md:24` files infer an approved grading/erosion plan exists because an erosion-control/site-grade fee was assessed. A fee establishes a fee, not the contents or approval state of a particular engineering instrument. Seek the actual file or a documented no-record/exemption determination.

### D. Property and deed contradictions (TS-012, TS-013)

`PROGRESS.md:24`, `ACQUISITION_CHECKPOINT.md:52` and `CORRECTION_HISTORY.md:34` say 2266 Tom Street does not/never existed. The broader source ledger correctly documents **no current Property Appraiser situs** and **historical MGO permits under 2266**. `ACQUISITION_RESULTS.md:26-28` further asserts a renumbering without supporting parcel-history records. Correct the summaries; do not assert a parcel merger/renumbering without records. Separately, Book/Page 3492/700 was only a Clerk results-grid capture, **not the downloaded deed image**. Treat assignment to 2274 as a working hypothesis until a recorded instrument and title chain verify it.

### E. Other specific meeting defects (TS-015–TS-018)

- The status refresh JSON stores `status_at_refresh: null` and `status_in_search_index: Active`; actual MGO full-project records contain `data.status: Active`. Fix field accessor and retain timestamp. Avoid “active right now” without a current county refresh.
- `PROXY_SPEAKING_NOTES.md:121` says all inspections passed, but the 2264 chronology identifies a **Partial Pass** unrelated to drainage, and important drainage-final tasks remain incomplete. Correct rather than exaggerate.
- `02_HOMEOWNER_LETTER.md:12` says **“Our parcels”** about property officially registered to Holiday Builders. Change to **“subject construction parcels”**; confirm what neighbor/proxy is actually authorized to represent.
- FEMA zone X is demonstrated **at geocoded sample points**. Parcel polygons have not been overlaid, so neither whole lot nor pluvial street flood risk is definitively characterized by the dataset.

## 3. Exhibit/claim/source cross-reference failure (TS-003, TS-020)

The 15-exhibit index marks **all 15** `public_release=YES`, and the evidence ledger cites those exhibits. The actual 22-member ZIP includes **only the redacted permit-screen derivative (`EX-15`)** at its designated source path. The other **14** source exhibits, including County PA extracts, both permits, inspection comments, public attachments responses, FEMA data and the actual LDC, are absent from the release. **No underlying source file for any of the 20 claims is packaged**, although the ledger is present.

The claim ledger's 18 local files and 15 exhibit files each match their recorded hashes: the problem is **source coverage and distribution**, not a simple file corruption. Specific multi-property claims improperly cite only one supporting file:

| Claim | Assertion | Evidence issue |
|---|---|---|
| `CLM-006` | Applicant business on **both** permits | Only `BP-2026-1621_project_by_uid.json` cited; add 1612. |
| `CLM-010` | As-built task `Assigned` on **both** | Only the 2264 requirements file cited; add 2268. |
| `CLM-011` | Drainage tasks and CO stages on **both** | Only 2268 requirements file cited; add 2264; do not infer CO nonissuance. |
| `CLM-012` | Empty public document lists for **both** | Only 2264 response cited; add 2268. |
| `CLM-016` | Former inspection failures at **2260 and 2270** | Only 2260 source cited; add 2270 permit record. |
| `CLM-014` | **Entire parcels** within FEMA Zone X | Sample points at geocoded coordinates; acquire actual polygons. |
| `CLM-013` | No nearby FDEP ERP; NWFWMD 9220-2 nearest | Geospatial search does not prove full authorization inventory or applicability to these parcels. |
| `CLM-019`, `CLM-020` | Original field media and hydraulic proof missing | Properly represented as evidence gaps, not affirmative factual findings. |

**Resolution:** add a `CLAIM_SOURCE_LINKS.csv` join table with `claim_id`, `source_id`, permit/parcel, exact pointer (e.g. `data.status` or inspection ID), raw local path, hash, timestamp, limitation and human review status. Any material conclusion involving both sites must have a source row for each. Create **public-safe, labeled source extracts**, not unaudited copied private data. The distributed release should either contain an actual redacted exhibit for each reference or clearly mark it as internal-only and supply a direct official source/retrieval route.

## 4. Privacy and provenance: urgent (TS-001, TS-002, TS-005–007, TS-051)

The repository is PUBLIC. Although 10 raw authenticated captures were moved from tracking to a private vault according to the reconciliation, prior published commits still contain them. More seriously, `00_CONTROL/tools/classify_for_release.py:26-34` embeds **account-specific strings and a token-like session identifier split across string literals in the current public source**. The script special-cases itself as PUBLIC (`:51-54`), and the privacy unit test excludes the tools directory. Splitting a secret into two literals does **not** protect it. This report deliberately avoids reproducing any credential or personal address/email.

- Immediately assess and rotate any potentially live session/API credentials and preserve evidence about exposure privately; review public-current and public-history content. A repo-history rewrite or GitHub support action may be appropriate but is destructive and **requires the owner's approval**. A force push alone cannot guarantee that forks/caches disappear.
- Move sensitive matching patterns to ignored, locally restricted configuration or replace with HMAC fingerprints and synthetic test data; ensure detectors inspect themselves under a safe rule instead of trusting them automatically.
- Perform **human approval** of every public release, plus check PDF text/metadata, HTML hidden fields, images, and embedded files, not merely raw literal byte patterns.
- The `RELEASE_PRIVACY_CLASSIFICATION.csv` lists 165 paths despite **170 tracked** and has a stale self-hash; `EVIDENCE_MANIFEST.csv` lists 10 vault paths that cannot be independently rehashed from this public snapshot, and includes invalid self/recycled-register hashes.
- The current public tree **still contains two tracked `.pyc` files** despite `CURRENT_STATE_RECONCILIATION.md` saying both were untracked and removed. Scan their constants for sensitive data without execution; untrack while maintaining any required restricted evidentiary copy.

The release manifest uses an unconditional description `PUBLIC-SAFE`, which is not substantiated by the safeguards above. Replace it with limited check outcomes until explicit review is recorded.

## 5. Test-suite blind spots (TS-039–TS-042)

`00_CONTROL/TEST_RESULTS.txt` reports **29 passed, 0 failed**. That run is an **internal suite result**, not independent proof of evidence adequacy. Static analysis of test source identified defects:

1. `test_evidence.py:71-82`: when the evidence manifest lists itself with a hash **different** from the live hash, the test treats that **as a success**. It should instead require an explicit self-exclusion policy and never silently accept a bogus checksum.
2. `test_evidence.py:129-146`: the release checksum test computes a ZIP path from `SHA256SUMS.txt` by extension changes, leading to a file that does not exist, and skips without recording any assertion. Independently, **all 22 current ZIP member hashes were verified** against the separate checksum file. The *automation* is broken even though the bytes currently match.
3. `test_evidence.py:204-214`: a source claim passes based primarily on file existence, not field-level proof that the proposition is in the cited source; missing second-property sources are unnoticed.
4. `test_evidence.py:248-278`: the privacy check omits public tool source and has a narrow literal match; raw bytes of a compressed PDF do not prove no sensitive text is embedded.
5. `00_CONTROL/tools/validate_evidence.py:60-116`: its manifest can contain itself with a stale hash and excludes scripts and other content without a declared expected-set reconciliation.

**Validation fix:** Write independent adversarial fixtures: inject a stale self-hash; omit a second-site source; include a fabricated “installed pipe” claim referencing only a consultation; mutate a release ZIP member; insert a synthetic secret in a public script and a test PDF. Every one must fail the pre-release gate. Store reviewer decisions separately from machine checks.

## 6. Regulatory/case-law audit

### Applicable local code, with exact PDF pages

Source: the downloaded 509-page Santa Rosa County Land Development Code at `08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf`, **cover dated 11/10/2025** (PDF pp. 1–2; includes Ord. 2025-25). The digital PDF's `CreationDate` is January 13, 2026; this is **not** the printed code date. Verify intervening amendments/effective dates before relying on provisions for March 23, 2026 permits.

| Authority | Source PDF page | Questions and important qualifiers |
|---|---:|---|
| §3.04.04 | 157 | Existing natural/manmade drainageways, obstruction and actual alignment. Does not establish obstruction by builder. |
| §3.04.05.A.3–A.8 | 157–159 | Inlet protection; stockpile storage without blocking natural drainage; stabilization after grading; pavement track-out; phased work, drainage BMPs. Applies based on text/conditions; independently document violations, if any. |
| §3.04.05.C–G | 159 | BMPs and pre-disturbance installation; engineer/contractor responsibilities; SWPPP requirements and NPDES link. Analyze each clause before assuming a specific SWPPP required. |
| §4.04.01.A–D.1 | 267–269 | Stormwater design objective, positive outlet, onsite/offsite contribution, conditional under-one-acre lot grading plans or NWFWMD individual ERP, lot boundary elevations, flow areas, BMPs and sealed engineer letter. Subdivision grading plan-on-file status is unknown. |
| §4.04.01.D.4 | 270 | **Exemptions omitted** from existing matrix: foundation/FFE/fill specifics, 125-ft minimum lot width, and County Engineer/Building Official special circumstances; BMPs still required. Do not allege failure to file a plan until exemptions are checked. |
| §4.04.01.E | 270 | County text says **all lots require a certified as-built before CO**, separate from the D.1.g conditional letter wording. County interpretation/document type should be requested. |
| §4.04.01.G–I | 271–272 | Road ROW swale criteria, slope, plan/calculation requirements, pre/post basin maps and supporting site geotechnical data where appropriate. |
| §4.04.01.I.3 | 273 | Positive outlet and basin design rules; more stringent rules for identified closed/no-outfall basins. **Do not indiscriminately apply the 13.44-inch 100-year storm special rule to every residential lot.** Request how County classified this drainage basin and applicable approved exception. |

### State construction-stormwater program

FDEP official guidance `https://floridadep.gov/water/stormwater/content/construction-activity` explains that a Construction Generic Permit (CGP) can be required for less-than-one-acre individual construction if part of a qualifying larger common development plan, **and** discharging to surface waters or an MS4; the program is **separate from an ERP**. The repository lacks a dedicated FDEP custodian request, common-plan boundary/total acreage proof, operator/NOI/NOT and SWPPP verification. FDEP's July 2026 proposed revisions must **not** be treated as adopted or effective without official confirmation. Also distinguish county erosion controls that apply regardless of CGP triggering conditions.

### Controlling Florida case law

The repository matrix says primary *Westland Skating Center, Inc. v. Gus Machado Buick, Inc.*, 542 So. 2d 959 (Fla. 1989), is unavailable. **A corrected Florida Supreme Court opinion is publicly available** through Florida State University College of Law (`https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf`, docket 72492). Its central holding adopts the **reasonable-use** approach for interference with surface waters. This does **not** create an automatic claim that elevating a residential lot is unlawful; actual circumstances, causation, injury and reasonableness matter. Download and preserve the exact opinion, verify subsequent treatment, and describe it as legal background rather than a site-specific determination. Florida Statute §373.042 on minimum stream flows is not currently a useful basis for the site complaint.

### FEMA flood hazard caveat

Archived FEMA NFHL point responses for both geocoded sites return Zone X, FIRM panel 12113C0587H, effective November 19, 2021. This establishes the values for the queried **points only**. Do not assert the entire parcel geometry was surveyed/intersected or that local street/ditch flooding is ruled out by Zone X.

## 7. Engineering and causation gaps (unresolved; not code violations)

1. **Design baseline:** Approved site plans, grading plans, sealed PE signoffs, parent subdivision grading/drainage plan or documented exemption, original topography, plan revisions and design calculations.
2. **Actual constructed system:** Surveyed road crown/shoulder, property line spot elevations, ditch cross-sections, inlets, pipe material/size/locations, culvert invert and outfall elevations and exact upstream/downstream receiving capacity. The August 6 pipe instruction is not an as-built.
3. **Hydrology:** Positive outlet vs possible closed basin; responsible public/private drainage corridor; upstream/offsite catchment; infiltration, groundwater and seasonal water table; rainfall design event and temporary construction sediment controls.
4. **Historical comparison:** Preconstruction aerials, 2017 NOAA/partner LiDAR and older/later datasets (coverage to be verified), original low-point storage and pre/post fill volumes using compatible datums/uncertainties. A historic bare-earth DEM alone cannot establish current drainage harm.
5. **Impact evidence:** Original homeowner photographs and videos with EXIF and chain of custody, georeferenced repeat observations, severity/duration, preconstruction conditions at 2265 and other affected houses, actual storm rainfall matched to observation times.
6. **Alternative causes:** Existing roadside restrictions, 2260/2270 culvert condition, impervious changes at older homes, downspouts, rainfall anomalies, ditch maintenance, antecedent saturation and groundwater. Do not assume all ponding was newly caused by construction.
7. **Authorization/ownership:** Public/private ROW, recorded easement and abandonment/maintenance instruments, the actual licensed contractor and Florida PE-of-record, county plan reviewer, field inspector and water-management permit holder.

**Highest-value engineering question:** What does the *approved* plan say the drainage will do, what was *actually installed*, and where does the combined system legally and hydraulically discharge during the applicable storm? That requires agency documents and professional measurement; the 170-file repository cannot answer it alone.

## 8. Agency action and evidence custody

There are **five prepared Chapter 119 requests**, each unsubmitted in the repository:

- 2264 building/lot engineering permit file (Santa Rosa County Development Services).
- 2268 equivalent file (Santa Rosa County Development Services).
- Shared Tom Street right-of-way and drainage plans (County Engineering/Public Works).
- Original plats, deeds, easements and legal history (Santa Rosa County Clerk).
- ERP 9220-2 and predecessor NWFWMD engineering documents (water-management district).

**Add a separate FDEP CGP/NOI/NOT search/request** and a **separate Santa Rosa County Public Works drainage service request** after confirming the road maintainer. These are not necessarily completed by the Chapter 119 requests. The County's official road concerns page (`https://www.santarosa.fl.gov/377/Road-Issues`) describes drainage and culvert work requests; obtain a ticket, inspection and written disposition. Verify all recipient contact details from official current sources. Requests should seek existing records and accept phased production/no-record replies rather than demanding creation of non-existing analyses under Chapter 119.

User approval is needed to submit correspondence in their name. Preserve final sent text, timestamp, recipient, receipt and rolling response batches. No correspondence has been sent in this review.

## 9. Public-release gate

**CURRENT VERDICT: NOT READY TO DISTRIBUTE AS EVIDENCE PACKET.** A strictly factual set of questions may be used after removing the identified overstatements, but label it a draft without the raw backup until exhibits are repaired.

Required machine- and person-checklist before release:

- [ ] Public current and historic privacy risks assessed, exposed credentials revoked if warranted, only reviewed redacted derivatives included.
- [ ] As-built status, pipeline ownership/installation, flat-grade, 2266, fee-to-plan, CO and FEMA parcel-level wording reconciled across every document, HTML and PDF.
- [ ] Primary source for each material public claim packaged (or marked clearly unavailable/restricted with official retrieval pointer); claim-source pairing covers **each** site.
- [ ] Exact ordinance/code version and cited clauses verified; Westland official corrected opinion archived; FDEP CGP applicability treated conditionally.
- [ ] Deed/plat titles not implied from clerk results grids.
- [ ] SHA manifest and release provenance included **inside** distribution or an explicit separately delivered companion; an independent checker works on extracted distribution.
- [ ] Automated tests fail intentionally injected stale source/ZIP checksum, fabricated cross-site proof, and synthetic privacy leak.
- [ ] Printable PDFs regenerated from corrected canonical source and visually checked; consent/signature and proxy language confirmed.
- [ ] Known missing engineering measurements, original photos, approvals and agency responses listed as unresolved, not quietly upgraded to verified.

## 10. Prioritized execution sequence and definition of done

**Immediate: owner/agent (security + accuracy).** Apply TS-001,002,003,008,009,011,012,017,039,040,042,051. Correct false statements before any new meeting release. Preserve original files; do not secretly rewrite remote history. Publish source extracts only after privacy approval. Add safeguards to CI/local verifier and produce a new immutable audit snapshot.

**Within the next working day after authorization: records and inspections.** TS-029,030,031,033,034,035,036,038,048. Submit five prepared records requests, file independent Public Works work request, seek FDEP CGP records, obtain neighbor original media, and request County engineering field visit. Document who accepted requests and promised answers.

**As agency documents arrive: engineering and legal reconciliation.** TS-018,019,020,021,022,023,024,025,027,028,032,037,044,049,050. Validate authoritative codes/permit versions, GIS geometry, approved plan vs field survey, rainfall and upstream effects, maintenance responsibility, alternative explanations, and PE findings.

**After verification: corrected public packet.** Rebuild from authoritative Markdown, include exhibits with captions and source dates, signatures as applicable, a concise requested-action list, and a request/response tracking sheet. Publish a ZIP that includes its actual provenance and checksum. Use homeowner professional, non-accusatory voice. The final meeting objective is a documented agency commitment to investigate and report corrective measures **if** an applicable deficiency is verified.

### Actual checks performed and residual uncertainty

**Performed:** exact GitHub/main vs uploaded ZIP inventory reconciliation; hash and parser passes for 170 files; static code/critical test logic inspection; 20-claim/15-exhibit/41-source and 22-gap register reconciliation; actual source-hash validation; SHA check of every release ZIP member; review of current PDF contents/visuals; direct review of official local LDC text and externally located Florida Supreme Court opinion; official FDEP/County Public Works guidance research. **No repository mutation or external submission was performed.**

**Not performed or unavailable:** authenticated live MGO or county engineering back-office retrieval, private vault/hash comparison (not provided in this public archive), homeowner original EXIF/photo originals, on-site measurements, complete official Clerk instrument image, licensed engineer drainage calculations, verified parcel polygon overlays, legal subsequent-case treatment or attorney advice, review of any unpushed agent changes after Git snapshot.

**Least certain:** Whether the two construction projects caused measurable changes in flooding on neighboring property. **No quantified site-level field evidence supports either a yes or a no.**  
**Main blind spot:** Release quality and test-suite pass counts are not engineering proof, and several unsubmitted requests are necessary to get the true source-of-record.  
**Highest-priority verification:** Approved grading/drainage plans plus a documented Public Works field inspection and surveyed existing/actual roadside drainage, with original homeowner observations and storm rainfall.

---

### Source URLs (external primary authorities)

- Santa Rosa County Land Development Code landing: https://www.santarosa.fl.gov/182/Land-Development-Code
- Official code PDF referenced in repository: https://www.santarosa.fl.gov/DocumentCenter/View/5820
- Florida DEP construction activity/CGP: https://floridadep.gov/water/stormwater/content/construction-activity
- Florida DEP CGP rulemaking draft notice: https://floridadep.gov/water/stormwater/content/construction-generic-permit-rulemaking-drafts
- County Public Works drainage work requests: https://www.santarosa.fl.gov/377/Road-Issues
- Florida Supreme Court corrected Westland opinion: https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf
- Florida Supreme Court case docket: https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/72492.html
- County repository GitHub snapshot: https://github.com/dthompsonfl/tom.street.drainage/tree/f929cc9d207e201cc554cda51edf9e097280d2da

**Audit deliverables:** This report, the separate **51-line finding/register**, and the **170-line complete file inventory**. Each issue register row is independently actionable and includes an acceptance check; it is not a presumption that 51 legal violations exist.
