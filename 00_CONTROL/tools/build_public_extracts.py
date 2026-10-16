#!/usr/bin/env python3
"""HISTORICAL PUBLIC-EXTRACT GENERATOR DISABLED.

Build public, minimal extracts from preserved PA/MGO records.

This intentionally excludes applicants' private contact information, resident
photos, authenticated portal shells, session data, and unrelated raw records.
Outputs are *research extracts*, not county-certified engineering drawings.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json
from paths import ROOT

def source(path):
    p=ROOT/path
    b=p.read_bytes()
    return json.loads(b), hashlib.sha256(b).hexdigest()

def main():
    lines=['# Tom Street | Public-source extracts (derived, not official certified copies)',
           '', '**DRAFT RESEARCH SUPPORT, NOT A VERIFIED DRAINAGE DESIGN.** Source snapshots were captured during October 15–16, 2026 UTC. These excerpts are selected from preserved agency API records; the official agencies retain authority over the full current file. All current status claims require refreshing with the agency.', '',
           'This document deliberately omits contact details, account identifiers, original homeowner photographs, portal authentication state, and system-record fields unrelated to the listed claims.', '']
    for address,number,parcel in [('2264','1621','21-2S-26-0780-0QQ00-1020'),('2268','1612','21-2S-26-0780-0QQ00-1490')]:
        base=f'03_PERMITS_AND_INSPECTIONS/{address}_Tom_St'
        pa=f'02_PROPERTY_AND_PARCELS/{address}_Tom_St/srcpa_property_record_{parcel}.json'
        project=f'{base}/BP-2026-{number}_project_by_uid.json'
        inspections=f'{base}/BP-2026-{number}_inspections.json'
        requirements=f'{base}/BP-2026-{number}_requirements.json'
        attachments=f'{base}/BP-2026-{number}_project_files.json'
        pdata,psha=source(pa); assert pdata[0]['parcelNumber']==parcel
        info,isha=source(project);d=info['data'];assert d['projectNumber']==f'BP-2026-{number}'
        arr,ash=source(inspections)
        tasks,tsha=source(requirements)
        files,fsha=source(attachments)
        assert files.get('data')==[]
        row=pdata[0]
        lines += [f'## {address} Tom Street | BP-2026-{number}', '',
            f'- Archived County PA export: parcel `{row["parcelNumber"]}`; situs `{row["situsAddress1"]}`; owner organization `{row["ownerName"]}`; recorded zoning field `{row["zoning"]}`.',
            f'- Archived MGO project: `{d["projectNumber"]}`; status `{d["status"]}` **when captured**; issued `{d["dateIssued"]}`; last record update `{d.get("dateUpdated")}`; applicant business `{d.get("applicantBusinessName")}`.',
            f'- Permit tasks: `Certified Drainage as Built` = `{next(x["Status"] for x in tasks if x.get("Requirement")=="Certified Drainage as Built")}`. This is a workflow state, **not** proof of document absence, filing, lateness, acceptance or CO issuance.',
            f'- Portal-accessible project documents: `{len(files["data"])}` in the saved customer-file endpoint response. This is **not** a no-record statement from County staff.', '', '### Dated relevant inspection remarks', '']
        terms=('pipe','inlet','stormwater ditch','roadway grade','roadway grades','drainage')
        matches=[x for x in arr['data'] if x.get('comments') and any(k in x['comments'].lower() for k in terms)]
        for x in matches:
            comments=' '.join(x['comments'].split())
            lines+= [f'- {x["inspectionDateTime"]} (inspection ID `{x.get("inspectionID")}`): recorded remark: {comments}', '']
        if not matches:lines.append('- No drainage-related comment was selected by the public extract filter.\n')
        lines+=['### Source integrity / exact preserved record paths','',
                 '| Captured record | SHA-256 |', '|---|---|']
        for name,path,sha in [('County PA',pa,psha),('MGO project',project,isha),('Inspection comments',inspections,ash),('Requirement statuses',requirements,tsha),('Customer project-file endpoint',attachments,fsha)]:
            lines.append(f'| `{path}` | `{sha}` |')
        lines+=['', '**Limitation:** These hashes verify the saved source bytes, not completeness of the underlying county permit file, design adequacy, current permit status or the legality of drainage work.', '']
    lines+=['## Related authority and unresolved matters','',
       '- Santa Rosa County Land Development Code, cover dated November 10, 2025: official county URL https://www.santarosa.fl.gov/DocumentCenter/View/5820 ; potentially relevant provisions §§ 3.04.04, 3.04.05 and 4.04.01. Confirm controlling version and any lot-specific exemptions with the County.',
       '- Florida Supreme Court reasonable-use doctrine: *Westland Skating Center, Inc. v. Gus Machado Buick, Inc.*, corrected opinion (March 30, 1989), https://library.law.fsu.edu/Digital-Collections/flsupct/dockets/72492/op-72492.pdf. Not proof of Tom Street harm or a violation.',
       '- The inspector instruction for 2264 does not prove that any pipe is actually installed, the pipe direction, positive outfall, location relative to ROW/easements, ownership, maintenance or hydraulic capacity.',
       '- The road-grade instruction for 2268 provides no actual surveyed grade or lot freeboard.',
       '- Neither the ERP proximity search nor FEMA flood-zone geocoded-point results establish environmental permit applicability or whole-parcel flood behavior.',
       '- The original homeowner flooding photos/EXIF, surveys, approved plans, signed certifications, measured inverts and Public Works work-order results remain outstanding.',
       '- Five earlier Chapter 119 requests, the FDEP construction-stormwater draft and the County Public Works work-request draft are **NOT SUBMITTED** in the preserved workspace. No receipt is known.', '']
    out=ROOT/'15_RECONCILED_DRAFTS/05_PRIMARY_SOURCE_EXTRACTS.md'
    out.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('created',out.relative_to(ROOT),len(lines),'lines')
if __name__=='__main__':
    raise SystemExit("RETIRED HISTORICAL EXTRACT BUILDER: do not overwrite current curated research extracts with a fixed older selection.")
    main()
