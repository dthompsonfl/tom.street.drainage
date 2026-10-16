# CURRENT STATE RECONCILIATION

Prepared: 2026-10-16 · Repo: `/home/dylan/Tom-Street-Drainage-Investigation`
Baseline captured **before** any edit in this session.

---

## 1. Repository identity

| Item | Value |
|---|---|
| Root | `/home/dylan/Tom-Street-Drainage-Investigation` |
| Remote | `https://github.com/dthompsonfl/tom.street.drainage` |
| Remote visibility | **PUBLIC** (verified via `gh repo view --json visibility`) |
| Default branch | `main` |
| Starting HEAD (this session) | `5ddbac9ba37f824b298ee715cb413cc309fe7c52` |
| Remote `main` HEAD at start | `5ddbac9ba37f824b298ee715cb413cc309fe7c52` (in sync) |
| Working tree at start | **clean** (`git status --porcelain` = 0 lines) |
| Tracked files at start | 119 |
| Prior commits | `5ddbac9 updates`, `a5a3eee init commit` |

**Important:** the previous session's evidence work was already committed and
pushed before this directive began. This session therefore starts from a
published state, not a draft state.

## 2. Source-material availability — a material correction

The directive directs that certain prior artifacts be read before editing, and
gives specific baselines. **Those artifacts were searched for across the whole
filesystem and are not present.** This is recorded rather than worked around.

| Referenced artifact | Present? | How checked |
|---|---|---|
| `tom.street.drainage-main.zip` | **YES** | `/home/dylan/Downloads/tom.street.drainage-main.zip` |
| `Tom_Street_Corrected_Workspace_2026-10-15.zip` | **NO** | `find / -name …` |
| `Tom_Street_Independent_Audit_2026-10-15.md` (18 findings) | **NO** | `find / -name …` |
| `Tom_Street_Line_By_Line_File_Audit_2026-10-15.csv` (119-file register) | **NO** | `find / -name …` |
| `Tom_Street_Evidence_Ledger_2026-10-15.csv` (15 claims) | **NO** | `find / -name …` |
| `Tom_Street_Missing_Records_Tracker_2026-10-15.csv` (14 gaps) | **NO** | `find / -name …` |
| `Tom_Street_Meeting_Packet_2026-10-15.zip` (+ 2 PDF briefs) | **NO** | `find / -name …` |

Consequences, stated plainly:

- **The "18 principal audit findings" could not be read.** No corrective action
  is claimed against them.
- **The 119-file coverage register could not be reconciled against the original
  agent archive.** The number 119 does coincide with `git ls-files | wc -l`
  in the current repository, but that is the *current* tracked-file count and
  is **not** evidence of the audit's original baseline. These are treated as
  different quantities.
- **"60,069 textual lines"** could not be verified. The second commit alone
  shows 56,103 insertions, so the figure cannot be assumed to correspond to any
  single prior state.
- The three archived claim/gap CSVs could not be read, so no claim in this
  repository is traced to them.

### 2.1 What `tom.street.drainage-main.zip` actually is

| Property | Value |
|---|---|
| Path | `/home/dylan/Downloads/tom.street.drainage-main.zip` |
| SHA-256 | `8a827e22da2535f0bf77deb18c5d331e09243f413deee8cf05fb7ee02308a26b` |
| Size | 1,030,568 bytes |
| Members | 138 (119 files + 19 directories) |
| `unzip -t` | **No errors detected** |
| File mtime | 2026-10-15 20:47 — *after* the `5ddbac9` commit |

It is **a GitHub source snapshot of this repository as it stood at the start of
this session**, not a pre-existing independent agent archive. It contains
`00_CONTROL/ACQUISITION_RESULTS.md`, `CORRECTION_HISTORY.md` and all
`00_CONTROL/tools/*.py` created in the prior session, and it even contains
compiled `__pycache__/*.pyc` artifacts that should never have been tracked.

It is therefore treated as a redundant copy of the live checkout, **not** as
independent corroboration of any factual claim.

## 3. Baseline defects found in the starting repository

| # | Defect | Severity | Disposition |
|---|---|---|---|
| D1 | 10 authenticated-portal captures (HTML + PNG) containing the requester's **name and e-mail address** were tracked and pushed to a **PUBLIC** repository | **Critical / privacy** | Remediated this session — see §4 |
| D2 | 2 compiled `.pyc` files tracked under `00_CONTROL/tools/__pycache__/` | Medium | Untracked and deleted from working tree |
| D3 | 22 of 27 tools hardcoded `/home/dylan/Tom-Street-Drainage-Investigation` | Medium | Replaced with `paths.py` root discovery |
| D4 | Register writers overwrite canonical CSVs with no guard, dry-run or backup | Medium | Added `GUARDED` set + `safe_write()` refusal |
| D5 | `classify_for_release.py` (added this session) initially classified text-only, silently skipping non-UTF-8 portal HTML | Medium | Fixed to scan raw bytes; self-test added |
| D6 | No `CURRENT_STATE_RECONCILIATION.md`, `EVIDENCE_LEDGER.csv`, `MISSING_RECORDS_AND_ACTIONS.csv`, `REGULATORY_AND_CASELAW_MATRIX.md`, `EXHIBIT_INDEX.csv`, `CHRONOLOGY.csv`, `DESIGN_VS_FIELD_MATRIX.csv`, `RESPONSIBILITY_MATRIX.csv`, `CONTRADICTION_LOG.md`, root `README.md` | High | Created this session |
| D7 | No `14_MEETING_PACKET/` and no release packaging | High | Created this session |
| D8 | No test suite or single build/validate entry point | High | Created this session |
| D9 | `00_CONTROL/RELEASE_PRIVACY_CLASSIFICATION.csv` embedded the literal e-mail it was detecting | Low | Sanitised; detector now uses split literals |

## 4. Privacy remediation performed (D1)

The leak was real and is now closed going forward:

1. `00_CONTROL/tools/classify_for_release.py` classifies every file
   `PUBLIC` / `RESTRICTED` / `BUILD_ARTIFACT` by **byte-level** scan.
2. `00_CONTROL/tools/vault_restricted.py` copied the 10 restricted files to
   `.evidence_vault/restricted/…`, verified each copy by SHA-256, then removed
   them from the working tree and from the Git index.
   **No bytes were deleted.**
3. `00_CONTROL/RESTRICTED_EVIDENCE_INDEX.csv` records original path → vault
   path → bytes → SHA-256 for all 10.
4. `00_CONTROL/tools/redact_captures.py` produced redacted **derivatives** of
   the two permit screenshots for any public use; the unredacted originals stay
   in the vault.
5. `.gitignore` now excludes `.evidence_vault/`.

Verified after remediation: `grep` across the working tree (excluding the vault)
finds **no** occurrence of the requester's name or e-mail, and the detector's
self-test still flags a synthetic leak.

**Residual risk, disclosed plainly:** the files remain in the *published Git
history* at commit `5ddbac9`. Removing them from `main` going forward does not
erase them from prior commits. Rewriting history is expressly out of scope for
this directive, so the prior exposure is reported rather than silently remediated.
If the owner wants it purged, that requires a history rewrite and separate authorisation.

## 5. Static safety review of `00_CONTROL/tools/*.py` (before execution)

Performed before any tool was run, as directed.

- **27 scripts** AST-parsed. **0 syntax errors.**
- Searched for destructive primitives: `os.system`, `subprocess.call/Popen`,
  `shutil.rmtree`, `os.remove`, `os.unlink`, `eval`, `exec` → **none present**.
- Network primitives are limited to `requests` and Playwright, used only to read
  public portals.
- No script performs deletion of evidence. Two scripts call `git rm --cached`,
  which affects the index only; both were reviewed and used only under `--apply`.
- Scripts that write canonical registers (`build_registers.py`,
  `build_registers2.py`) are now guarded by `paths.safe_write`.

**Caveat recorded per the directive:** AST-clean is not the same as correct.
A syntactically valid tool can still be misconfigured. Several tools require an
authenticated MGO session (`/tmp/opencode/mgo_auth.json`); they are *not*
self-configuring and were not treated as runnable without it.

## 6. Proposed surgical edits (all applied this session)

| Path | Change | Rationale |
|---|---|---|
| `00_CONTROL/tools/paths.py` | **new** | Root discovery, guarded writes, hashing helpers |
| `00_CONTROL/tools/*.py` (22 files) | hardcoded root → `from paths import ROOT` | D3 |
| `00_CONTROL/tools/classify_for_release.py` | **new** | D1, D5 |
| `00_CONTROL/tools/vault_restricted.py` | **new** | D1 |
| `00_CONTROL/tools/redact_captures.py` | **new** | D1 derivative handling |
| `00_CONTROL/tools/acquire_hydrology.py` | **new** | FEMA + NOAA primary acquisition |
| `00_CONTROL/tools/mgo_refresh_status.py` | **new** | Status refresh with fresh timestamp |
| `08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf` | **new** | Actual county code, 509 pp |
| `00_CONTROL/*` canonical registers | **new/refreshed** | D6 |
| `11_HYDROLOGY_AND_HAZARD/*` | **new** | Flood zone + rainfall |
| `14_MEETING_PACKET/*` | **new** | D7 |

## 7. Verdict

The starting repository contained **zero verified primary engineering evidence
for drainage design** but did contain verified official permit metadata and
inspection records. Its principal defect was a **privacy exposure on a public
remote**, now closed going forward. The missing audit artifacts are recorded
above as unavailable rather than assumed.