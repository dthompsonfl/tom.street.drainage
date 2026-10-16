# Remediation progress | as-of 2026-10-16 UTC

**Scope:** Direct main-branch corrective work based on the independent 51-item gap register. This progress report records local fixes subject to remote commit verification. It does not certify engineering, county, or homeowner evidence completeness.

## Verified local improvements

- Corrected unsupported narrative claims about 2266 historical address, 2268 mobile-home parcel attribution, Clerk deed-grid results, as-built/CO workflow, paid erosion-grading fees, roadside pipe installation/private boundaries, 2268 qualitative road grades, FEMA sampled-point boundaries and nearby ERP applicability.
- Reconciled claim CLM-011, 013, 014 and all 15 exhibit indexes to distinguish source references from a privacy-reviewed public exhibit.
- Built 23 individual claim-to-source links for 18 official claims; separately corroborated both target permit project/requirement/file captures and both neighboring historical driveway permits. No original agency JSON was rewritten.
- Replaced privacy classifier with generic checks and optional ignored local reviewer markers; removed old source-code embedded sensitive account/session literals and untracked two compiled `.pyc` artifacts in staged snapshot. Historic Git commits may still expose them.
- Changed validation to source-only manifest semantics, checks source SHA and file existence, and rejects false self-hash, missing ZIP parity, uncorroborated cross-site claims or false pass for release. Replaced unsafe automatic release with fail-closed draft check.
- Added original text links to FSU Florida Supreme Court Westland opinion and stronger LDC review requirements, plus draft County Public Works and FDEP CGP requests, **not submitted**.
- Prepared derived public source extracts without raw private contact data. The existing legacy PDF and ZIP are explicitly **withdrawn** and retained historically; a corrected print-ready release is not yet certified.

## Independent local verification

- 74 preserved source record files validated byte-exact against regenerated manifest, 0 failures.
- 23 claim-source joins checked against preserved SHA and mapped property scope, 0 errors.
- 38 repository tests passed, 0 failed; stricter evidence gate: 0 mechanical errors.
- `build_release.py` intentionally returned status 3, refusing final public publication absent sign-off. This is the **correct safety result**, not a release failure that should be suppressed.

## Outstanding material dependencies

- Five existing Chapter 119 draft requests and new FDEP/Public Works drafts remain unsubmitted; no new agency receipts.
- No stamped grading/approved revisions, historic/current survey, actual pipe invert/positive-outfall measurements, as-built/CO file confirmation, relevant title/easements, verified ERP/CGP coverage or PE assessment was obtained.
- Private archive now contains 15 hash-matched JPEG copies per concurrent agent, but device originals, EXIF origin, storm event timeline, and permissions remain unverified.
- No present or historical Git privacy purge performed; human privacy approval and session credential rotation require separate owner-controlled action.
- Concurrent agent published corrected draft PDF materials under `15_RECONCILED_DRAFTS/pdf/`; **external distribution approval has not been established**. The older `14_MEETING_PACKET` is withdrawn. The existing historical release is not for distribution.

**Next release condition:** County engineering documents + factual homeowner evidence + print/source-exhibit parity + privacy sign-off. A hash-valid file is not proof that its claims are correct.
