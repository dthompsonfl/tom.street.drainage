# Tom Street | fixed edition and verified location map

**2026-10-16 technical implementation status: EDITION CANDIDATE ONLY.** No one has approved an exact resident statement, source/privacy review, or distribution package merely because this directory exists or a GitHub Actions job passed. Real neighbor testing and final human release authorization remain outstanding.

## What can be generated from this repository

- [Map generator](../tools/build_neighborhood_reference_map.py) produces a **source-verified PDF and accessible SVG** from preserved Santa Rosa County GIS parcel polygons (layer 8), the Tom Street County Maintained roadway centerline (layer 5, object 2036), and historical stormwater context (layer 79, object 2068).
- [Candidate edition generator](../tools/build_neighborhood_review_edition.py) packages only the **current five-page unsigned draft**, blank observation worksheets, plain-English source/uncertainty materials, and that map with **exact source commit SHA**, full inclusion list, content hashes and explicit pending approvals.
- [Automated candidate workflow](../.github/workflows/neighborhood-review-candidate.yml) runs read-only verification and retains the generated output as a clearly named **unapproved Actions artifact**, rather than pushing unsigned draft PDFs or automatically publishing a release.

The map **does not** show surveyed legal lot boundaries, parcel elevations, culvert inverts, current as-built grades, runoff direction or confirmed receiving outfall. Historic mapped problem-area information is not evidence of builder causation. The published original Crescent Shores plat remains a **separate historic official source**, not a 2026 engineering survey.

## Rebuild an exact checkout

From the intended fixed source commit with Python 3.12 and the release requirements installed:

    python -m pip install -r requirements-release.txt
    python tools/verify_reconciled_release.py
    python tools/build_neighborhood_reference_map.py
    python tools/build_neighborhood_review_edition.py
    python -m unittest discover -s tools -p 'test_neighborhood_review.py' -v

The generated GIS map is located under 19_NEIGHBOR_REVIEW/map/. The pinned, unapproved ZIP, checksums and status summary are under 19_NEIGHBOR_REVIEW/candidates/. The source commit and its timestamp are recorded inside the edition manifest; timestamp alone is not evidence of publication.

## Human publication path (not completed)

The proposed source and map must be visually checked and fact-checked; any official-source reuse restrictions must be reviewed; the resident author must approve each exact first-person version; two actual nontechnical people must complete the documented usability tasks and fixes must be retested; an authorized approver must sign off on **one specific edition manifest/ZIP checksum**. Only then may the coordinator record and distribute a fixed approved edition without changing its bytes. Until then do not represent an Actions artifact as released or personally approved.

No private household originals, authenticated portal captures, government source archive PDFs, or completed neighbor forms are included in the candidate. Older releases in releases/2026-10-15 are historical and superseded.
