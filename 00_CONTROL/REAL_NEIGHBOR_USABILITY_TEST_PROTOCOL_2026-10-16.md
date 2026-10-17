# Two real-neighbor usability tests | facilitator and participant packet

**PREPARED; ZERO PARTICIPANTS TESTED BY THIS DOCUMENT.** Run with two different adults who are not GIS or software specialists. Do not invent times, responses, consent, screenshots or sign-off. Their private answers and contact details stay outside the public repository. Use a different facilitator if the same organizer's guidance might influence test answers.

## Setup for each real participant

- Record anonymous participant reference `UT-01` or `UT-02`, date, device category (ordinary phone vs normal laptop/desktop), browser/PDF viewer, printing availability, accessibility accommodations, facilitator, and an actual informed testing agreement in the **private** facilitator notes. Do not record names, phone numbers or email in public logs.
- Give the participant only the GitHub repository home page or a **versioned candidate link with status label**. No instructions about where the correct answer is. Use screen-reader or enlarged type when appropriate, without treating accessibility accommodation as failure.
- Facilitator uses a stopwatch. Record per-task **start/end or elapsed seconds**, pass/assistance/fail, observed errors and exact page/file/version in a private observation record. Ask the participant to explain answers in their own words, not repeat a prompted phrase.

## Participant tasks (same eight for both, without coaching)

| ID | Task to complete | Objective pass criteria |
| --- | --- | --- |
| T1 | Find the current **neighborhood review** material starting from the homepage | Finds pinned edition/candidate and identifies draft versus approved status |
| T2 | Describe the concern and one significant open engineering question | Explains potential grading/drainage effect without stating a proven defect; mentions missing approved plans, field measurements or outfall |
| T3 | Find and open/print the **event-observation worksheet** | Opens page 3 standalone PDF, or locates same page in full blank packet; on computer can print on US Letter |
| T4 | Complete a **fictional practice observation** | Uses fictional date **2026-10-01**, imaginary rain period and location marked **PRACTICE ONLY**; records observed vs interpreted fields; never uploads completed sheet |
| T5 | Find a reliable primary source supporting a material fact | Locates source register or linked official record for parcel/permit or County road-maintenance classification; describes what it does not prove |
| T6 | Report wording error or broken link | Finds public correction issue route, or private coordinator contact procedure; knows not to upload private originals through GitHub |
| T7 | Identify sensitive evidence | Correctly identifies private photos, exact EXIF/GPS, contacts, completed forms, account/session captures and real approvals as restricted |
| T8 | Identify exact version | Finds edition ID/date, source commit and approval status (or correctly states no approved edition exists) |

Synthetic practice script: **"Imagine it rained for 20 minutes on Oct 1 at 3:00 PM and imaginary water stood near a pretend driveway. This is NOT a real Tom Street event. Record only those fictional details, keep the sample private or discard it."** Do not treat a hypothetical runoff direction as observed or proven.

## Accessibility/print checklist

Test at normal phone width (no horizontal layout scroll, legible text, touch targets), large text / zoom 200%, meaningful PDF page labels, links that describe destinations, usable keyboard focus and screen-reader reading order as applicable. Test computer printing in grayscale at US Letter 100%, check text not clipped, boxes aligned, sufficient writing room, clear privacy warning, page numbers, and no unexpectedly blank/missing worksheet pages. Record **NOT_TESTED** where assistive technology/printing was unavailable. A machine PDF parse is not a sighted usability test.

## Facilitator record, issues, corrections and retest

1. Create one real row per task in private `UT-01` / `UT-02` log. Summarize only non-identifying results and approved findings into [the public-safe register](USABILITY_TEST_RESULTS_PUBLIC_SAFE.csv). Blank rows are not completed tests.
2. Log each failure in [the defect tracker](USABILITY_DEFECT_AND_RETEST.csv): exact document/version, reproducible steps, actual behavior, severity, corrective action, new commit, repeat task and verified retest outcome. `OPEN` until reproduced and fixed; never mark `PASS` from the developer's prediction.
3. Address navigation, jargon, link, form and accessibility defects using their editable sources. Rebuild PDFs, run automated checks and have affected participant or a new eligible reviewer retest. Do not silently change a distributed approved edition; create a new candidate.
4. Independent review checks that **two actual distinct participants** completed all required tasks, both mobile and computer/print paths were exercised across tests, meaningful issues were resolved/retested, and human sign-off documents the **exact package SHA**. Keep signatures or identifying proof privately, with only opaque approval references in public status.

**Gate status: AWAITING_REAL_PARTICIPANTS.** Volunteer availability, date, actual timed results, corrections resulting from tests, retest outcomes and final sign-off are not established.
