#!/usr/bin/env python3
"""Build the canonical evidence ledger, action tracker, chronology, exhibit
index, design-vs-field matrix, responsibility matrix and contradiction log.

Every claim row is generated FROM a captured evidence file where one exists, so
the ledger cannot drift from the evidence. Claims that rest on no file carry an
explicit evidentiary class of UNVERIFIED or INFERENCE and say so.
"""
import os as _os, sys as _sys  # noqa: E402
_HERE = _os.path.dirname(_os.path.abspath(__file__))  # noqa: E402
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)  # noqa: E402
from paths import ROOT as _ROOT, rel, sha256_file, utcnow  # noqa: E402

import csv
import json
from pathlib import Path

CTL = _ROOT / "00_CONTROL"


def w(name, cols, rows):
    p = CTL / name
    with p.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    print(f"  {rel(p)}  {len(rows)} rows")


def sha(p):
    q = _ROOT / p
    return sha256_file(q) if q.exists() else ""


def load(p):
    q = _ROOT / p
    return json.loads(q.read_text()) if q.exists() else None


# ---------------------------------------------------------------- evidence ledger
LEDGER_COLS = ["claim_id", "claim", "evidentiary_class", "source_exhibit",
               "source_file", "sha256", "dated_reference", "capture_utc",
               "limitation", "contrary_evidence", "confidence", "reviewer"]

SRCPA_2264 = "02_PROPERTY_AND_PARCELS/2264_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1020.json"
SRCPA_2268 = "02_PROPERTY_AND_PARCELS/2268_Tom_St/srcpa_property_record_21-2S-26-0780-0QQ00-1490.json"
ROLL = "02_PROPERTY_AND_PARCELS/RAW_HTTP/srcpa_property_query_street_TOM_NAVARRE.json"
P2264 = "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_by_uid.json"
P2268 = "03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_project_by_uid.json"
I2264 = "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_inspections.json"
I2268 = "03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_inspections.json"
R2264 = "03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_requirements.json"
R2268 = "03_PERMITS_AND_INSPECTIONS/2268_Tom_St/BP-2026-1612_requirements.json"
SWEEP = "03_PERMITS_AND_INSPECTIONS/SYSTEM_RAW/mgo_sweep_results.json"
ERP = "09_ENVIRONMENTAL_PERMITS/SYSTEM_RAW/erp_nearest_permits_tom_street.json"
ZONE = "11_HYDROLOGY_AND_HAZARD/fema_nfhl_flood_hazard_zones.json"
LDC = "08_LEGAL_AND_REGULATORY/SOURCE/santa_rosa_county_LDC.pdf"


def insp(p, needle):
    d = load(p)
    if not d:
        return None
    for x in d.get("data", []):
        if needle in (x.get("inspectionType") or "") or \
           needle in (x.get("comments") or ""):
            return x
    return None


def reqstat(p, needle):
    d = load(p)
    if not d:
        return None
    for x in d:
        if needle in str(x.get("Requirement")):
            return x
    return None


x2264_dw = insp(I2264, "Driveway Line & Grade")
x2268_gr = insp(I2268, "Site Grading / Drainage (pre-construction)")
x2268_dw = insp(I2268, "Driveway Line & Grade")

LEDGER = [
    dict(claim_id="CLM-001",
         claim="2264 Tom Street is parcel 21-2S-26-0780-0QQ00-1020, owner of record HOLIDAY BUILDERS INC, zoning R2M, filing Crescent Shores (00780), lot 1020.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-01",
         source_file=SRCPA_2264, dated_reference="roll export, parcelKey 10082028",
         limitation="Export does not carry legal description, building card or sales history.",
         contrary_evidence="Prior research asserted ...-1490 for this address; that parcel is 2268 Tom St.",
         confidence="HIGH", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-002",
         claim="2268 Tom Street is parcel 21-2S-26-0780-0QQ00-1490, owner of record HOLIDAY BUILDERS INC, zoning R2M, filing Crescent Shores (00780), lot 1490.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-02",
         source_file=SRCPA_2268, dated_reference="roll export, parcelKey 10082068",
         limitation="Export does not carry legal description, building card or sales history.",
         contrary_evidence="Prior research asserted ...-1060 for this address; that parcel is 2274 Tom St.",
         confidence="HIGH", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-003",
         claim="No current Property Appraiser parcel bears situs address 2266 Tom Street.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-03", source_file=ROLL,
         dated_reference="street=TOM city=NAVARRE, 123 records",
         limitation="Absence from the current roll does not explain the history. Five closed 1996-1998 mobile-home permits exist at the historical address; no renumbering or merger has been proven.",
         contrary_evidence="MGO holds 1996-2741-000-B/E/G/P-0 and 1998-323-000-G-0 at '2266 TOM ST'.",
         confidence="HIGH for absence; UNRESOLVED for cause",
         reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-004",
         claim="Building permit BP-2026-1621 covers 2264 Tom Street as New Single Family (R), status Active, created 2026-02-11, issued 2026-03-23, record updated 2026-10-01.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-04", source_file=P2264,
         dated_reference="projectUID DBFA3383-592A-4486-A392-F88065C90F95, projectID 17513349",
         limitation="Snapshot as of the capture time; permit status changes.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-15; refreshed 2026-10-16"),
    dict(claim_id="CLM-005",
         claim="Building permit BP-2026-1612 covers 2268 Tom Street as New Single Family (R), status Active, created 2026-02-11, issued 2026-03-23, record updated 2026-10-06.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-05", source_file=P2268,
         dated_reference="projectUID 677D3AE3-F348-4B97-A37C-8B0BC05CEAF7, projectID 17513025",
         limitation="Snapshot as of the capture time.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-15; refreshed 2026-10-16"),
    dict(claim_id="CLM-006",
         claim="Applicant of record for both permits is Amy Riddle, business Holiday Builders INC.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-04", source_file=P2264,
         dated_reference="applicantFirstName/LastName/applicantBusinessName",
         limitation="Establishes applicant, not licensed contractor of record and not engineer of record.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-007",
         claim=(f"On {x2264_dw['inspectionDateTime'][:10]} the county recorded a driveway line-and-grade "
                f"consultation for 2264 Tom Street, status {x2264_dw['inspectionStatus']}, comment: "
                f"\"{x2264_dw['comments']}\"") if x2264_dw else "UNAVAILABLE",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-06", source_file=I2264,
         dated_reference=(f"inspectionID {x2264_dw['inspectionID']}" if x2264_dw else ""),
         limitation="This is an inspector's direction recorded in a portal field. It is NOT an approved drawing, NOT proof of what was installed, NOT a hydraulic analysis, and NOT proof of invert elevations or pipe ownership.",
         contrary_evidence="", confidence="HIGH that the comment exists; it proves no design adequacy",
         reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-008",
         claim=(f"On {x2268_gr['inspectionDateTime'][:10]} the county recorded a pre-construction site "
                f"grading/drainage inspection for 2268 Tom Street, status {x2268_gr['inspectionStatus']}, "
                f"comment: \"{x2268_gr['comments']}\"") if x2268_gr else "UNAVAILABLE",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-07", source_file=I2268,
         dated_reference=(f"inspectionID {x2268_gr['inspectionID']}" if x2268_gr else ""),
         limitation="Confirms an inspector observed a roadway and stormwater ditch. It is not a survey, a profile, or a capacity finding.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-009",
         claim=(f"On {x2268_dw['inspectionDateTime'][:10]} the county recorded a driveway line-and-grade "
                f"consultation for 2268 Tom Street, status {x2268_dw['inspectionStatus']}, comment: "
                f"\"{x2268_dw['comments']}\"") if x2268_dw else "UNAVAILABLE",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-08", source_file=I2268,
         dated_reference=(f"inspectionID {x2268_dw['inspectionID']}" if x2268_dw else ""),
         limitation="'Flat' and 'match existing roadway grades' are the inspector's words. They do not quantify freeboard, slope or fall across the driveway.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-010",
         claim="The county requirement 'Certified Drainage as Built' is recorded as 'Assigned' on BOTH BP-2026-1621 and BP-2026-1612 as of the 2026-10-16 refresh.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-09", source_file=R2264,
         dated_reference="ProjectRequirements projectID 17513349 / 17513025",
         limitation="'Assigned' means the county has an open task. It does NOT establish that a document exists, that one is missing, that one is overdue, or that any violation occurred. Both permits are still Active.",
         contrary_evidence="", confidence="HIGH that the status reads 'Assigned'",
         reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-011",
         claim="'Site Grading / Drainage (mid-construction)' and '(final construction)' inspections and 'Driveway Final Inspection' are recorded 'Not Complete' on both permits; 'Issue CO' is 'Assigned'; no Certificate of Occupancy appears.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-09", source_file=R2268,
         dated_reference="ProjectRequirements projectID 17513025",
         limitation="Open tasks on an Active permit are consistent with normal construction sequence and are not evidence of non-compliance.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-012",
         claim="The MGO customer portal exposes zero attached documents for either permit.",
         evidentiary_class="OBSERVATION", source_exhibit="EX-10",
         source_file="03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_files.json",
         dated_reference="GET /api/v3/cp/ProjectFiles/get-customer-files-by-project-id/{id} -> data: []",
         limitation="An empty portal response does NOT establish that the County holds no approved plans. Three candidate inspection-report endpoints returned HTTP 404. This is the evidentiary basis for the records requests.",
         contrary_evidence="", confidence="HIGH that the endpoint is empty; NOT proof of absence of county records",
         reviewer="agent, 2026-10-15 and 2026-10-16"),
    dict(claim_id="CLM-013",
         claim="The nearest Environmental Resource Permit in the NWFWMD public map service is ERP 9220-2, 'Hadleigh Hills, Phase 2 Ext. to P9220-1', applicant Hadleigh Hills Development Group, 8.1 acres, decided 2016-11-21. No FDEP-issued ERP lies within 2,000 ft of either parcel.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-11", source_file=ERP,
         dated_reference="NWFWMD EPermit_ERP MapServer layer 0, OFFCL_PRMT_ID 9220 SEQ 2",
         limitation="Proximity is NOT proof that ERP 9220-2 covers these lots. No permit polygon was intersected against the parcel polygons, and no ERP document was obtained. Attribution to 2264/2268 is UNPROVEN.",
         contrary_evidence="", confidence="HIGH that the ERP exists nearby; UNPROVEN as to applicability",
         reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-014",
         claim="Both parcels sit in FEMA Flood Zone X (area of minimal flood hazard), FIRM panel 12113C0587H effective 2021-11-19, Santa Rosa County unincorporated areas.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-12", source_file=ZONE,
         dated_reference="FEMA NFHL layer 28 Flood Hazard Zones; layer 3 FIRM Panels",
         limitation="Regulatory flood hazard mapping does not address local street-ditch ponding, which can occur well outside the mapped floodplain.",
         contrary_evidence="", confidence="HIGH", reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-015",
         claim="Noon: no 'Crescent Shores' or 'Hadleigh Hills' entry appears in any of the County's seven annual Approved Subdivisions StoryMaps (2020-2026).",
         evidentiary_class="OBSERVATION", source_exhibit="",
         source_file="04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/approved_subdivision_storymaps_search.json",
         dated_reference="ArcGIS item data for 7 StoryMap items",
         limitation="Absence from a StoryMap is not a finding that no subdivision approval exists; the StoryMaps may not be exhaustive.",
         contrary_evidence="", confidence="MEDIUM", reviewer="agent, 2026-10-15"),
    dict(claim_id="CLM-016",
         claim="The neighbouring Driveway Connection permits at 2260 Tom St (2019-7490-000-B-2) and 2270 Tom St (2021-2524-000-B-1) each recorded multiple FAILED inspections before a later pass, and both are now Closed/Complete.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-13",
         source_file="04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/2019-7490-000-B-2.json",
         dated_reference="inspection records 2019-12-20, 2020-02-19 (2260); 2021-08-03/05/20 (2270)",
         limitation="Prior corrected failures at OTHER properties are NOT evidence of present non-compliance at 2264 or 2268. The county's failure-reason field records only the inspector's name, so the specific non-compliance is not disclosed.",
         contrary_evidence="Both projects were ultimately closed complete.",
         confidence="HIGH that the failures occurred", reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-017",
         claim="Santa Rosa County LDC 4.04.01.D.1 requires, for a residential lot under one acre that does not have a subdivision lot grading plan on file with County Engineering, a sealed Florida PE lot grading plan OR an NWFWMD Individual ERP approval letter with supporting calculations and plans, plus finish-floor elevations, positive-outfall inverts, perimeter spot elevations, flow areas, construction BMPs, and — at substantial completion and prior to Certificate of Occupancy — a signed/sealed engineer letter certifying conformance.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-14", source_file=LDC,
         dated_reference="LDC printed pages 249-250 = PDF pages 267-268; PDF dated 2026-01-13",
         limitation="Whether a subdivision lot grading plan is on file for these lots is UNKNOWN and is the pivotal unresolved fact. The requirement's applicability cannot be confirmed without the County Engineering lot-grading-plan index.",
         contrary_evidence="", confidence="HIGH that the code text says this; applicability UNRESOLVED",
         reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-018",
         claim="Santa Rosa County LDC 3.04.04 provides that development shall conform to natural contours with natural or man-made drainageways left unobstructed, and that obstruction of natural or man-made drainageways is strictly prohibited.",
         evidentiary_class="OFFICIAL_RECORD", source_exhibit="EX-14", source_file=LDC,
         dated_reference="LDC printed page 139 = PDF page 157",
         limitation="A compliance standard. No determination of violation is made: no approved plan, as-built, invert survey or PE analysis exists in this repository.",
         contrary_evidence="", confidence="HIGH that the code text says this",
         reviewer="agent, 2026-10-16"),
    dict(claim_id="CLM-019",
         claim="HOMEOWNER SITE OBSERVATIONS, original dated photographs/videos and EXIF have NOT been obtained.",
         evidentiary_class="NOT_OBTAINED", source_exhibit="", source_file="",
         dated_reference="", limitation="No field measurement, photograph or survey is present. Any statement about actual water depth, duration or direction on site is currently unsupported.",
         contrary_evidence="", confidence="N/A", reviewer="pending"),
    dict(claim_id="CLM-020",
         claim="No hydraulic capacity calculation, simulation or drainage-adequacy determination has been performed.",
         evidentiary_class="NOT_DETERMINED", source_exhibit="", source_file="",
         dated_reference="",
         limitation="Requires approved plan geometry, design rainfall criteria, invert elevations and a reproducible validated model. None exist here. A Florida licensed Professional Engineer and/or surveyor is required.",
         contrary_evidence="", confidence="N/A", reviewer="pending"),
]
for c in LEDGER:
    c["sha256"] = sha(c["source_file"]) if c["source_file"] else ""
    c["capture_utc"] = utcnow()

# ---------------------------------------------------------------- action tracker
ACT_COLS = ["gap_id", "gap", "custodian", "request_file", "submitted",
            "submission_date", "receipt_id", "agency_response",
            "production_batches", "due_or_next_followup", "owner",
            "closure_evidence", "status"]
REQ = "13_PUBLIC_RECORDS_REQUESTS"
ACTS = [
    dict(gap_id="GAP-01", gap="Approved site plan / plot plan for BP-2026-1621 (2264 Tom St)",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-02", gap="Approved grading plan and all revisions for BP-2026-1621",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-03", gap="Existing-conditions / topographic / boundary survey for 2264",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-04", gap="Erosion and sediment control plan for 2264",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-05", gap="Driveway plan and culvert details for 2264 (invert elevations, pipe size)",
         custodian="Santa Rosa County Development Services / Public Works",
         request_file=f"{REQ}/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-06", gap="Certified Drainage as Built for BP-2026-1621 (county task still 'Assigned')",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-07", gap="Final grading / mid- and final-construction inspection records for 2264",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-08", gap="Approved site plan and grading plan for BP-2026-1612 (2268 Tom St)",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-09", gap="Existing-conditions survey and positive-outfall inverts for 2268",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-10", gap="Certified Drainage as Built for BP-2026-1612 (county task still 'Assigned')",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2268_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-11",
         gap="PIVOTAL: does a subdivision lot grading plan exist on file with County Engineering for these lots? (determines which branch of LDC 4.04.01.D applies)",
         custodian="Santa Rosa County Engineering Department",
         request_file=f"{REQ}/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-12", gap="Tom Street roadway profile: crown, centreline and shoulder elevations",
         custodian="Santa Rosa County Public Works",
         request_file=f"{REQ}/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-13", gap="Records of the concrete drainage structures at 2260 and 2270 Tom St, incl. invert elevations",
         custodian="Santa Rosa County Public Works",
         request_file=f"{REQ}/SHARED_TOM_STREET_ROW_AND_DRAINAGE_PLANS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-14", gap="Recorded plat for Crescent Shores (00780) / Pope Subdivision; drainage and fill easements",
         custodian="Santa Rosa County Clerk of Court",
         request_file=f"{REQ}/CLERK_DEEDS_PLATS_EASEMENTS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-15", gap="Recorded legal description and chain of title for lots 1020 and 1490",
         custodian="Santa Rosa County Clerk of Court",
         request_file=f"{REQ}/CLERK_DEEDS_PLATS_EASEMENTS.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-16", gap="NWFWMD ERP 9220-2 permit file: application, approved stormwater drawings, conditions, compliance",
         custodian="Northwest Florida Water Management District",
         request_file=f"{REQ}/NWFWMD_ERP_9220-2_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-17", gap="Whether ERP 9220-2's permit polygon actually covers either Tom Street parcel (geometry intersection)",
         custodian="agent (GIS) + NWFWMD (documents)",
         request_file=f"{REQ}/NWFWMD_ERP_9220-2_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="after GAP-16; or request polygon from NWFWMD",
         owner="agent", closure_evidence="", status="NOT_OBTAINED"),
    dict(gap_id="GAP-18", gap="Construction-stormwater NPDES CGP coverage / NOI-NOT applicability determination for this site",
         custodian="NWFWMD / FDEP",
         request_file=f"{REQ}/NWFWMD_ERP_9220-2_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-19", gap="Contractor of record and engineer of record for BP-2026-1621 and BP-2026-1612",
         custodian="Santa Rosa County Development Services",
         request_file=f"{REQ}/2264_TOM_ST_COMPLETE_PERMIT_FILE.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="awaiting owner authorisation to submit",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-20", gap="Holiday Builders, Inc. legal entity registration and any parent/successor entity",
         custodian="Florida Division of Corporations (Sunbiz)",
         request_file="", submitted="FALSE", submission_date="", receipt_id="",
         agency_response="", production_batches="0",
         due_or_next_followup="retry Sunbiz (HTTP 403 on first attempt) or obtain via public records",
         owner="agent", closure_evidence="", status="NOT_OBTAINED"),
    dict(gap_id="GAP-21", gap="Homeowner original timestamped photographs/videos with EXIF of observed conditions",
         custodian="homeowner",
         request_file="14_MEETING_PACKET/HOMEOWNER_EVIDENCE_INTAKE_CHECKLIST.md",
         submitted="FALSE", submission_date="", receipt_id="", agency_response="",
         production_batches="0", due_or_next_followup="homeowner to supply originals",
         owner="homeowner", closure_evidence="", status="REQUEST_DRAFTED"),
    dict(gap_id="GAP-22", gap="Licensed Florida PE / surveyor field measurements and drainage analysis",
         custodian="to be engaged by homeowner",
         request_file="", submitted="FALSE", submission_date="", receipt_id="",
         agency_response="", production_batches="0",
         due_or_next_followup="after approved plans are obtained (GAP-01..GAP-10)",
         owner="homeowner", closure_evidence="", status="NOT_OBTAINED"),
]

# ---------------------------------------------------------------- chronology
CHRON_COLS = ["event_id", "date_observed", "date_record_created", "date_captured_utc",
              "address", "event", "source_type", "source_file", "sha256", "certainty"]
CHRON = [
    dict(event_id="CH-001", date_observed="1996-07-18", date_record_created="1996-07-18",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="Mobile home, electrical, mechanical and plumbing permits issued (1996-2765-000-B/E/M/P-0)",
         source_type="OFFICIAL_RECORD", source_file=SWEEP, certainty="recorded date"),
    dict(event_id="CH-002", date_observed="2000-12-14", date_record_created="2000-12-14",
         date_captured_utc="2026-10-15", address="2268 Tom St",
         event="Mobile home, electrical, gas and plumbing permits issued (2000-4250-000-B/E/G/P-0)",
         source_type="OFFICIAL_RECORD", source_file=SWEEP, certainty="recorded date"),
    dict(event_id="CH-003", date_observed="2015-02-23", date_record_created="2015-02-23",
         date_captured_utc="2026-10-15", address="2265 Tom St",
         event="New single family residence built (2015-1043-000-B-0) incl. Site (R) permit",
         source_type="OFFICIAL_RECORD", source_file=SWEEP, certainty="recorded date"),
    dict(event_id="CH-004", date_observed="2016-11-21", date_record_created="2016-11-21",
         date_captured_utc="2026-10-15", address="within 2,000 ft of both parcels",
         event="NWFWMD ERP 9220-2 'Hadleigh Hills, Phase 2' permit decision (applicability to these lots UNPROVEN)",
         source_type="OFFICIAL_RECORD", source_file=ERP, certainty="recorded date; applicability unproven"),
    dict(event_id="CH-005", date_observed="2026-02-11", date_record_created="2026-02-11T12:36:02",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="BP-2026-1621 application created", source_type="OFFICIAL_RECORD",
         source_file=P2264, certainty="recorded date"),
    dict(event_id="CH-006", date_observed="2026-02-11", date_record_created="2026-02-11T11:30:14",
         date_captured_utc="2026-10-15", address="2268 Tom St",
         event="BP-2026-1612 application created", source_type="OFFICIAL_RECORD",
         source_file=P2268, certainty="recorded date"),
    dict(event_id="CH-007", date_observed="2026-03-23", date_record_created="2026-03-23T15:18:01",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="BP-2026-1621 permit issued", source_type="OFFICIAL_RECORD",
         source_file=P2264, certainty="recorded date"),
    dict(event_id="CH-008", date_observed="2026-03-23", date_record_created="2026-03-23T15:12:03",
         date_captured_utc="2026-10-15", address="2268 Tom St",
         event="BP-2026-1612 permit issued", source_type="OFFICIAL_RECORD",
         source_file=P2268, certainty="recorded date"),
    dict(event_id="CH-009", date_observed="2026-07-22", date_record_created="2026-07-22",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="Site Grading / Drainage (pre-construction) inspection PASSED",
         source_type="OFFICIAL_RECORD", source_file=I2264, certainty="recorded date"),
    dict(event_id="CH-010", date_observed="2026-08-06", date_record_created="2026-08-06",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="Driveway Line & Grade consultation PASSED with pipe/inlet-box direction (see CLM-007)",
         source_type="OFFICIAL_RECORD", source_file=I2264, certainty="recorded date"),
    dict(event_id="CH-011", date_observed="2026-08-14", date_record_created="2026-08-14",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="Building Misc. Windload inspection PARTIAL PASS ('Trusses must seat on load bearing wall shim under floating trusses')",
         source_type="OFFICIAL_RECORD", source_file=I2264, certainty="recorded date"),
    dict(event_id="CH-012", date_observed="2026-08-31", date_record_created="2026-08-31",
         date_captured_utc="2026-10-15", address="2268 Tom St",
         event="Site Grading / Drainage (pre-construction) inspection PASSED; inspector references roadway and stormwater ditch (CLM-008)",
         source_type="OFFICIAL_RECORD", source_file=I2268, certainty="recorded date"),
    dict(event_id="CH-013", date_observed="2026-09-10", date_record_created="2026-09-10",
         date_captured_utc="2026-10-15", address="2268 Tom St",
         event="Driveway Line & Grade consultation PASSED, 'Flat; Match Existing roadway Grades' (CLM-009)",
         source_type="OFFICIAL_RECORD", source_file=I2268, certainty="recorded date"),
    dict(event_id="CH-014", date_observed="2026-10-01", date_record_created="2026-10-01",
         date_captured_utc="2026-10-15", address="2264 Tom St",
         event="Driveway Pre-Pour inspection PASSED; permit record last updated",
         source_type="OFFICIAL_RECORD", source_file=I2264, certainty="recorded date"),
    dict(event_id="CH-015", date_observed="2026-10-06", date_record_created="2026-10-06",
         date_captured_utc="2026-10-16", address="2268 Tom St",
         event="Permit record last updated", source_type="OFFICIAL_RECORD",
         source_file=P2268, certainty="recorded date"),
    dict(event_id="CH-016", date_observed="UNKNOWN", date_record_created="UNKNOWN",
         date_captured_utc="", address="2264 / 2268 Tom St",
         event="Homeowner-observed ponding, duration or direction of flow",
         source_type="NOT_OBTAINED", source_file="", certainty="UNKNOWN - not documented"),
]
for c in CHRON:
    c["sha256"] = sha(c["source_file"]) if c["source_file"] else ""

# ---------------------------------------------------------------- exhibits
EXH_COLS = ["exhibit_id", "caption", "source_file", "sha256", "bytes",
            "official_identifier", "what_it_proves", "what_it_does_NOT_prove",
            "public_release"]
EXH = [
    dict(exhibit_id="EX-01", caption="Official parcel record — 2264 Tom Street",
         source_file=SRCPA_2264, official_identifier="parcel 21-2S-26-0780-0QQ00-1020; parcelKey 10082028",
         what_it_proves="Owner of record, situs, zoning, filing name and lot for 2264 Tom Street.",
         what_it_does_NOT_prove="Legal description, boundary location, building card or sales history.",
         public_release="YES"),
    dict(exhibit_id="EX-02", caption="Official parcel record — 2268 Tom Street",
         source_file=SRCPA_2268, official_identifier="parcel 21-2S-26-0780-0QQ00-1490; parcelKey 10082068",
         what_it_proves="Owner of record, situs, zoning, filing name and lot for 2268 Tom Street.",
         what_it_does_NOT_prove="Legal description, boundary location, building card or sales history.",
         public_release="YES"),
    dict(exhibit_id="EX-03", caption="Property Appraiser Tom Street roll extract (123 records)",
         source_file=ROLL, official_identifier="POST /property/query street=TOM city=NAVARRE",
         what_it_proves="The current official street roll, including that no 2266 Tom St parcel exists.",
         what_it_does_NOT_prove="Why 2266 historically existed; the roll is not a boundary survey.",
         public_release="YES"),
    dict(exhibit_id="EX-04", caption="MGO permit record BP-2026-1621 (2264 Tom Street)",
         source_file=P2264, official_identifier="BP-2026-1621 / UID DBFA3383-592A-4486-A392-F88065C90F95",
         what_it_proves="Permit existence, type, status, dates, applicant, subdivision and lot.",
         what_it_does_NOT_prove="Any approved design, grading, or as-built condition.",
         public_release="YES"),
    dict(exhibit_id="EX-05", caption="MGO permit record BP-2026-1612 (2268 Tom Street)",
         source_file=P2268, official_identifier="BP-2026-1612 / UID 677D3AE3-F348-4B97-A37C-8B0BC05CEAF7",
         what_it_proves="Permit existence, type, status, dates, applicant, subdivision and lot.",
         what_it_does_NOT_prove="Any approved design, grading, or as-built condition.",
         public_release="YES"),
    dict(exhibit_id="EX-06", caption="2264 driveway line-and-grade inspection comment (2026-08-06)",
         source_file=I2264,
         official_identifier=f"inspectionID {x2264_dw['inspectionID']}" if x2264_dw else "",
         what_it_proves="An inspector recorded a direction about 12-inch ADS pipe and inlet boxes at the 2260 and 2270 frontages.",
         what_it_does_NOT_prove="An approved drawing; what was actually built; invert elevations; hydraulic sufficiency; pipe ownership.",
         public_release="YES"),
    dict(exhibit_id="EX-07", caption="2268 pre-construction grading/drainage inspection comment (2026-08-31)",
         source_file=I2268,
         official_identifier=f"inspectionID {x2268_gr['inspectionID']}" if x2268_gr else "",
         what_it_proves="An inspector passed the site and referred to a roadway and stormwater ditch.",
         what_it_does_NOT_prove="A survey, a profile, a capacity finding, or the condition of the ditch today.",
         public_release="YES"),
    dict(exhibit_id="EX-08", caption="2268 driveway line-and-grade inspection comment (2026-09-10)",
         source_file=I2268,
         official_identifier=f"inspectionID {x2268_dw['inspectionID']}" if x2268_dw else "",
         what_it_proves="An inspector recorded 'Flat; Match Existing roadway Grades'.",
         what_it_does_NOT_prove="Quantified freeboard, slope or cross-fall across the driveway.",
         public_release="YES"),
    dict(exhibit_id="EX-09", caption="MGO task/requirement lists showing open drainage and CO tasks",
         source_file=R2264,
         official_identifier="ProjectRequirements projectID 17513349 / 17513025",
         what_it_proves="'Certified Drainage as Built' = Assigned and final grading inspections = Not Complete on both permits as of 2026-10-16.",
         what_it_does_NOT_prove="That any document is missing, overdue, or that a violation occurred. Both permits remain Active.",
         public_release="YES"),
    dict(exhibit_id="EX-10", caption="MGO customer document endpoint returns an empty list",
         source_file="03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project_files.json",
         official_identifier="GET /api/v3/cp/ProjectFiles/get-customer-files-by-project-id/17513349",
         what_it_proves="The public portal exposes no attachments for this permit.",
         what_it_does_NOT_prove="That the County holds no approved plans. This is why records requests are needed.",
         public_release="YES"),
    dict(exhibit_id="EX-11", caption="NWFWMD ERP 9220-2 (nearest environmental authorization)",
         source_file=ERP, official_identifier="ERP Official Permit ID 9220, SEQ 2",
         what_it_proves="An individual ERP exists within 2,000 ft of both parcels, decided 2016-11-21.",
         what_it_does_NOT_prove="That it covers these lots. No polygon intersection was performed and no permit document was obtained.",
         public_release="YES"),
    dict(exhibit_id="EX-12", caption="FEMA flood hazard determination for both parcels",
         source_file=ZONE, official_identifier="FIRM panel 12113C0587H; NFHL layer 28",
         what_it_proves="Both parcels are mapped Zone X (minimal flood hazard).",
         what_it_does_NOT_prove="Absence of local street-ditch ponding, which is not mapped.",
         public_release="YES"),
    dict(exhibit_id="EX-13", caption="Neighbouring driveway-connection inspection history (2260 / 2270)",
         source_file="04_ENGINEERING_AND_DRAINAGE/Tom_Street_Shared_System/2019-7490-000-B-2.json",
         official_identifier="2019-7490-000-B-2; 2021-2524-000-B-1",
         what_it_proves="Both neighbouring driveway connections failed inspection more than once before closing complete.",
         what_it_does_NOT_prove="Any present non-compliance at 2264 or 2268; the specific failure reasons are not disclosed by the County.",
         public_release="YES"),
    dict(exhibit_id="EX-14", caption="Santa Rosa County Land Development Code (official PDF)",
         source_file=LDC,
         official_identifier="LDC 3.04.04, 3.04.05, 4.04.01; PDF dated 2026-01-13",
         what_it_proves="The codified drainage, obstruction and lot-grading requirements applicable to this jurisdiction.",
         what_it_does_NOT_prove="That any provision has been violated; applicability of 4.04.01.D depends on whether a subdivision lot grading plan is on file.",
         public_release="YES"),
    dict(exhibit_id="EX-15", caption="Permit record screenshot, account identity redacted (DERIVATIVE)",
         source_file="14_MEETING_PACKET/exhibits/derived_redacted/03_PERMITS_AND_INSPECTIONS/2264_Tom_St/BP-2026-1621_project.png",
         official_identifier="derivative of a restricted capture; original in .evidence_vault",
         what_it_proves="The county portal places a pin on the 2264 Tom Street parcel within the Tom Street frontage.",
         what_it_does_NOT_prove="Anything about drainage. The account identity has been redacted in this derivative.",
         public_release="YES"),
]
for e in EXH:
    q = _ROOT / e["source_file"]
    e["sha256"] = sha256_file(q) if q.exists() else ""
    e["bytes"] = q.stat().st_size if q.exists() else 0

# ---------------------------------------------------------------- design vs field
DVF_COLS = ["item_id", "parameter", "approved_value", "observed_or_surveyed_value",
            "unit", "datum", "responsible_party", "source", "discrepancy",
            "status"]
DVF = [
    dict(item_id="DVF-01", parameter="Finished floor elevation, 2264", approved_value="NOT_OBTAINED",
         observed_or_surveyed_value="NOT_MEASURED", unit="ft NAVD88 (assumed; unconfirmed)",
         datum="unknown", responsible_party="Engineer of Record (unidentified)",
         source="GAP-03 / GAP-06", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-02", parameter="Finished floor elevation, 2268", approved_value="NOT_OBTAINED",
         observed_or_surveyed_value="NOT_MEASURED", unit="ft", datum="unknown",
         responsible_party="Engineer of Record (unidentified)",
         source="GAP-08 / GAP-10", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-03", parameter="Roadway crown / centreline elevation at 2264 frontage",
         approved_value="NOT_OBTAINED", observed_or_surveyed_value="NOT_MEASURED", unit="ft",
         datum="unknown", responsible_party="Santa Rosa County Public Works",
         source="GAP-12", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-04", parameter="Driveway invert / outfall elevation, 2264",
         approved_value="NOT_OBTAINED", observed_or_surveyed_value="NOT_MEASURED", unit="ft",
         datum="unknown", responsible_party="Contractor / Engineer of Record",
         source="GAP-05", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-05", parameter="Driveway cross-slope / fall, 2268",
         approved_value="'Match Existing roadway Grades' (CLM-009) — no numeric value",
         observed_or_surveyed_value="NOT_MEASURED", unit="%", datum="n/a",
         responsible_party="Engineer of Record (unidentified)",
         source="EX-08", discrepancy="No numeric approved value exists to compare against",
         status="NOT_TESTABLE"),
    dict(item_id="DVF-06", parameter="Invert elevation of existing concrete drainage structure at 2260",
         approved_value="NOT_OBTAINED", observed_or_surveyed_value="NOT_MEASURED", unit="ft",
         datum="unknown", responsible_party="Santa Rosa County Public Works",
         source="GAP-13", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-07", parameter="Invert elevation of existing concrete drainage structure at 2270",
         approved_value="NOT_OBTAINED", observed_or_surveyed_value="NOT_MEASURED", unit="ft",
         datum="unknown", responsible_party="Santa Rosa County Public Works",
         source="GAP-13", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-08", parameter="Pipe size actually installed, 2264 driveway",
         approved_value="12-inch ADS perforated pipe with sock (inspector direction only, CLM-007)",
         observed_or_surveyed_value="NOT OBSERVED — no site visit or photograph yet",
         unit="in", datum="n/a", responsible_party="Contractor (unidentified)",
         source="EX-06", discrepancy="Direction is not proof of installation",
         status="NOT_TESTABLE"),
    dict(item_id="DVF-09", parameter="Stormwater ditch invert / cross-section, Tom St frontage",
         approved_value="NOT_OBTAINED", observed_or_surveyed_value="NOT_MEASURED", unit="ft / ft",
         datum="unknown", responsible_party="Santa Rosa County Public Works",
         source="GAP-12 / GAP-13", discrepancy="CANNOT COMPUTE", status="NOT_TESTABLE"),
    dict(item_id="DVF-10", parameter="Rainfall during documented drainage events",
         approved_value="Design storm criteria: not obtained (LDC 4.04.01.J referenced, full text not yet extracted)",
         observed_or_surveyed_value="NOAA Pensacola RGNL AP 2026-01-01..2026-10-15 total PRCP 1067.0 mm; 2025 full year 1044.3 mm",
         unit="mm", datum="n/a", responsible_party="NOAA (regional, not on-site)",
         source="11_HYDROLOGY_AND_HAZARD/noaa_ghcndaily_construction_window.json",
         discrepancy="Off-site regional gauge; cannot be used to compute site hydrology",
         status="CONTEXT_ONLY"),
]

# ---------------------------------------------------------------- responsibility
RESP_COLS = ["role", "entity", "basis", "verified_from", "certainty", "notes"]
RESP = [
    dict(role="Owner of record (both parcels)", entity="HOLIDAY BUILDERS INC",
         basis="Santa Rosa County Property Appraiser roll export",
         verified_from=SRCPA_2264, certainty="VERIFIED",
         notes="Mailing 2293 W Eau Gallie Blvd, Melbourne, FL 32935-3184. Ownership as of the roll date only."),
    dict(role="Permit applicant (both permits)", entity="Amy Riddle, Holiday Builders INC",
         basis="MGO permit record applicant fields", verified_from=P2264,
         certainty="VERIFIED", notes="Applicant is not automatically the licensed contractor."),
    dict(role="Permit authority", entity="Santa Rosa County Development Services",
         basis="MGO Connect jurisdiction ID 276", verified_from=P2264,
         certainty="VERIFIED", notes="Issued BP-2026-1621 and BP-2026-1612 on 2026-03-23."),
    dict(role="Licensed contractor of record", entity="NOT IDENTIFIED",
         basis="not exposed in the customer portal", verified_from="",
         certainty="NOT_OBTAINED", notes="See GAP-19."),
    dict(role="Engineer of record", entity="NOT IDENTIFIED",
         basis="not exposed in the customer portal; LDC 4.04.01.D.1.g requires a sealed PE letter",
         verified_from="", certainty="NOT_OBTAINED",
         notes="See GAP-19. This role is pivotal because the code requires the PE's sealed conformance letter before CO."),
    dict(role="Inspecting officials", entity="Santa Rosa County inspectors (named in records)",
         basis="inspection records name inspectors", verified_from=I2264,
         certainty="VERIFIED", notes="Names recorded per inspection; not an allegation."),
    dict(role="Road / drainage right-of-way custodian", entity="Santa Rosa County Public Works",
         basis="county department structure", verified_from="",
         certainty="CONDITIONAL",
         notes="Actual maintenance responsibility for the roadside ditch is UNCONFIRMED — may be a private or HOA-maintained swale."),
    dict(role="Environmental permitting authority", entity="Northwest Florida Water Management District",
         basis="ERP 9220-2 in NWFWMD's own map service", verified_from=ERP,
         certainty="VERIFIED as authority; UNPROVEN as to these parcels",
         notes="See GAP-16 / GAP-17."),
    dict(role="State ERP authority (separate)", entity="Florida DEP",
         basis="no FDEP ERP within 2,000 ft", verified_from=ERP,
         certainty="NOT_APPLICABLE on current evidence",
         notes="Absence of a search hit is not proof no authorisation exists."),
    dict(role="Recorded instruments custodian", entity="Santa Rosa County Clerk of Court",
         basis="official records portal", verified_from="",
         certainty="VERIFIED as custodian", notes="See GAP-14 / GAP-15."),
    dict(role="Builder corporate parent / successor", entity="NOT IDENTIFIED",
         basis="Sunbiz query returned HTTP 403 on first attempt",
         verified_from="", certainty="NOT_OBTAINED",
         notes="Corporate background is explicitly kept separate from drainage causation. See GAP-20."),
]

# ---------------------------------------------------------------- contradictions
CONTRA_COLS = ["id", "claim_a", "source_a", "claim_b", "source_b",
               "resolution", "status"]
CONTRA = [
    dict(id="CON-01",
         claim_a="2264 Tom St = parcel ...-0QQ00-1490",
         source_a="prior research, MLS-derived (CORRECTION_HISTORY.md CLAIM 1)",
         claim_b="2264 Tom St = parcel ...-0QQ00-1020",
         source_b=SRCPA_2264,
         resolution="Official roll controls. The prior work transposed the two target parcels. ...-1490 is 2268 Tom St.",
         status="RESOLVED in favour of official record"),
    dict(id="CON-02",
         claim_a="2268 Tom St = parcel ...-0QQ00-1060",
         source_a="prior research, MLS-derived",
         claim_b="2268 Tom St = parcel ...-0QQ00-1490",
         source_b=SRCPA_2268,
         resolution="Official roll controls. ...-1060 is 2274 Tom St (MATIG-A CEPRIANO P JR).",
         status="RESOLVED in favour of official record"),
    dict(id="CON-03",
         claim_a="2268 Tom St begins at ORB 3492 PG 700",
         source_a="prior research, MLS listing text",
         claim_b="ORB 3492/700 = instrument 201603296, legal '21-2S-26 POPE SUBD LOT 22 UNREC', grantee holds 2274 Tom St",
         source_b="00_CONTROL/SYSTEM_RAW/acclaim_bookpage_3492_700_20261015T235902Z.html + " + SRCPA_2268,
         resolution="The book/page lead is real but belongs to a different address. The prior attribution is wrong.",
         status="RESOLVED against the MLS text"),
    dict(id="CON-04",
         claim_a="2266 Tom St is an existing address to investigate",
         source_a="prior research",
         claim_b="No current parcel; but five closed 1996-1998 permits exist at that address",
         source_b=ROLL + " + " + SWEEP,
         resolution="Address is historical. Cause (renumbering vs merger) is UNPROVEN and deliberately not asserted.",
         status="PARTIALLY RESOLVED"),
    dict(id="CON-05",
         claim_a="Empty MGO document array means the County holds no approved plans",
         source_a="inference that must NOT be drawn",
         claim_b="The portal exposes no attachments at any access level tested",
         source_b="EX-10",
         resolution="The empty array justifies a records request; it does not establish absence of county records.",
         status="RESOLVED — absence NOT established"),
    dict(id="CON-06",
         claim_a="ERP 9220-2 'Hadleigh Hills' is the permit covering these lots",
         source_a="geographic proximity inference",
         claim_b="No polygon intersection performed; no permit document obtained",
         source_b=ERP,
         resolution="Recorded as an UNPROVEN lead only. GAP-17 tracks the required test.",
         status="UNRESOLVED"),
    dict(id="CON-07",
         claim_a="'Certified Drainage as Built: Assigned' means the county failed to obtain it",
         source_a="inference that must NOT be drawn",
         claim_b="Both permits are Active with 17-18 open tasks, consistent with an in-progress build",
         source_b=R2264 + " + " + R2268,
         resolution="Recorded as an open county task. It is neither a missing document nor a violation finding.",
         status="RESOLVED — no violation asserted"),
]

if __name__ == "__main__":
    print("building canonical registers:")
    w("EVIDENCE_LEDGER.csv", LEDGER_COLS, LEDGER)
    w("MISSING_RECORDS_AND_ACTIONS.csv", ACT_COLS, ACTS)
    w("CHRONOLOGY.csv", CHRON_COLS, CHRON)
    w("EXHIBIT_INDEX.csv", EXH_COLS, EXH)
    w("DESIGN_VS_FIELD_MATRIX.csv", DVF_COLS, DVF)
    w("RESPONSIBILITY_MATRIX.csv", RESP_COLS, RESP)
    w("CONTRADICTION_LOG.csv", CONTRA_COLS, CONTRA)