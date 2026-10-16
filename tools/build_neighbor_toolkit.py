#!/usr/bin/env python3
"""Builds the public-safe Tom Street neighbor blank paper-first PDF forms.

Blank paper-first worksheets, without resident information. Reproducible PDF output,
US Letter, embedded Lato fonts, single geometry system, quiet grayscale-safe styling.

Usage:
    python tools/build_neighbor_toolkit.py
    python tools/build_neighbor_toolkit.py /optional/output/directory

A blank master should be shared publicly; completed pages and original evidence stay
in private resident-controlled storage.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import sys
import re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit

FONTS = Path('/usr/share/fonts/truetype/lato')
FORCE_FALLBACK = os.environ.get('TOM_STREET_FORCE_HELVETICA') == '1'
FONT_FILES = [('Lato','Lato-Regular.ttf'),('LatoSemi','Lato-Semibold.ttf'),('LatoBold','Lato-Bold.ttf'),('LatoHeavy','Lato-Heavy.ttf'),('LatoItalic','Lato-Italic.ttf')]
# The distributed PDFs contain embedded fonts. The generator uses widely available
# built-in Helvetica as a fallback on systems that do not have Lato installed.
FALLBACK_FONTS = {'Lato':'Helvetica','LatoSemi':'Helvetica-Bold','LatoBold':'Helvetica-Bold','LatoHeavy':'Helvetica-Bold','LatoItalic':'Helvetica-Oblique'}
FONT_MAP = {}
for name, filename in FONT_FILES:
    path = FONTS / filename
    if path.exists() and not FORCE_FALLBACK:
        pdfmetrics.registerFont(TTFont(name,str(path)))
        FONT_MAP[name] = name
    else:
        FONT_MAP[name] = FALLBACK_FONTS[name]


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "18_NEIGHBOR_TOOLKIT" / "print"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = OUT_DIR / "Tom_Street_Neighbor_Documentation_Forms.pdf"
W,H=letter
L,R=48,48
PW=W-L-R
NAVY=HexColor('#142E3B')
TEAL=HexColor('#286473')
BODY=HexColor('#22353E')
MUTED=HexColor('#54656E')
RULE=HexColor('#B8C5CB')
PALE=HexColor('#E7ECEE')
WASH=HexColor('#F3F6F7')
WHITE=HexColor('#FFFFFF')
TOTAL=18
c=canvas.Canvas(str(OUT),pagesize=letter,pageCompression=1)
c.setTitle('Tom Street - Neighbor Documentation | Blank Forms')
c.setAuthor('Tom Street community documentation project')
c.setSubject('Blank printable worksheets for observations, official records and follow-up')
c.setKeywords('Tom Street, community, drainage, observations, records, print-ready, forms')

# Coordinates below are all TOP-ORIGIN points, which avoids mismatched rectangles.
def txt(x,top,s,font='Lato',size=9.5,color=BODY):
    c.setFillColor(color)
    c.setFont(FONT_MAP.get(font,font),size)
    c.drawString(x,H-top-size,s)

def right_txt(right,top,s,font='Lato',size=9.5,color=BODY):
    c.setFillColor(color);c.setFont(FONT_MAP.get(font,font),size)
    c.drawRightString(right,H-top-size,s)

def center_txt(x,top,s,font='Lato',size=9.5,color=BODY):
    c.setFillColor(color);c.setFont(FONT_MAP.get(font,font),size)
    c.drawCentredString(x,H-top-size,s)

def line(x1,y1,x2,y2,color=RULE,width=.7):
    c.setStrokeColor(color);c.setLineWidth(width)
    c.line(x1,H-y1,x2,H-y2)

def rect(x,top,w,h,fill=None,stroke=None,radius=0,sw=.7):
    c.setLineWidth(sw)
    if fill is not None: c.setFillColor(fill)
    if stroke is not None: c.setStrokeColor(stroke)
    if radius:
        c.roundRect(x,H-top-h,w,h,radius,fill=int(fill is not None),stroke=int(stroke is not None))
    else:
        c.rect(x,H-top-h,w,h,fill=int(fill is not None),stroke=int(stroke is not None))

def wrap(s,maxwidth,font='Lato',size=9.4):
    result=[]
    for segment in s.split('\n'):
        if not segment: result.append('');continue
        result.extend(simpleSplit(segment,FONT_MAP.get(font,font),size,maxwidth))
    return result

def paragraph(s,top,x=L,maxwidth=PW,font='Lato',size=9.6,leading=13.8,color=BODY,max_lines=10):
    lines=wrap(s,maxwidth,font,size)
    if len(lines)>max_lines:
        raise ValueError(f'Too many lines in paragraph: {s[:65]} ({len(lines)} > {max_lines})')
    for i,t in enumerate(lines): txt(x,top+leading*i,t,font,size,color)
    return top+leading*len(lines)

class Page:
    def __init__(self,index,code,title,subtitle,tag='BLANK WORKSHEET'):
        self.index=index
        self.code=code
        self.title=title
        self.rectangles=[]
        c.bookmarkPage(f'page-{index:02d}')
        c.addOutlineEntry(f'{index:02d} - {title}',f'page-{index:02d}',level=0,closed=False)
        # Restraint: short two-tone masthead with ample whitespace.
        rect(L,34,4,18,TEAL)
        txt(L+14,35,'TOM STREET  /  NEIGHBOR DOCUMENTATION',font='LatoBold',size=8.2,color=NAVY)
        right_txt(W-R,35,tag,font='LatoSemi',size=8,color=MUTED)
        line(L,58,W-R,58,PALE,1.0)
        txt(L,67,title,font='LatoHeavy',size=21,color=NAVY)
        self.y=paragraph(subtitle,100,size=9.65,leading=13.1,color=MUTED,max_lines=2)
        self.y=max(133,self.y+19)

    def section(self,number,name,top=None):
        if top is None: top=self.y
        txt(L,top,str(number).zfill(2),font='LatoBold',size=9.2,color=TEAL)
        txt(L+28,top-2,name,font='LatoBold',size=11.1,color=NAVY)
        line(L,top+19,W-R,top+19,PALE,.85)
        self.y=top+30
        return self.y

    def fields(self,items,top=None,height=49,gap=15):
        """items: list of (label,weight), shared baseline and tidy proportional widths."""
        if top is None: top=self.y
        assert height>=42
        space=PW-gap*(len(items)-1)
        weights=sum(w for _,w in items)
        x=L
        for label,wt in items:
            width=space*wt/weights
            label_lines=wrap(label,width-4,'LatoSemi',9.05)
            if len(label_lines)>2: raise ValueError(f'Field label too long for width: {label}')
            for k,lab in enumerate(label_lines):
                txt(x,top+k*11,lab,'LatoSemi',9.05,MUTED)
            line(x,top+height-7,x+width,top+height-7,RULE,.88)
            x+=width+gap
        if abs((x-gap)-(W-R))>.1: raise RuntimeError('Field row grid did not align')
        self.y=top+height+5
        return self.y

    def write(self,label,rows=3,top=None,helptext=None,leading=23.5):
        if top is None: top=self.y
        lines=wrap(label,PW,'LatoSemi',9.4)
        if len(lines)>2: raise ValueError('Overlong area label: '+label)
        for i,lab in enumerate(lines):txt(L,top+i*12.5,lab,'LatoSemi',9.4,NAVY)
        offset=35+12*(len(lines)-1)
        if helptext:
            hlines=wrap(helptext,PW,'LatoItalic',8.45)
            if len(hlines)>2: raise ValueError('Overlong helptext')
            for i,t in enumerate(hlines):txt(L,top+19+i*11,t,'LatoItalic',8.45,MUTED)
            offset+=11*len(hlines)
        for i in range(rows):
            line(L,top+offset+i*leading,W-R,top+offset+i*leading,RULE,.77)
        self.y=top+offset+(rows-1)*leading+22
        return self.y

    def checks(self,options,cols=2,top=None,row_height=28.5,size=9.5):
        if top is None: top=self.y
        rows=(len(options)+cols-1)//cols
        cw=PW/cols
        for i,s in enumerate(options):
            rr=i//cols;cc=i%cols
            x=L+cc*cw
            t=top+rr*row_height
            rect(x,t+1,12,12,fill=None,stroke=TEAL,sw=.85)
            lines=wrap(s,cw-25,'Lato',size)
            if len(lines)>2:raise ValueError('Too many check lines '+s)
            for k,lab in enumerate(lines):txt(x+20,t-2+k*11,lab,'Lato',size,BODY)
        self.y=top+rows*row_height+8
        return self.y

    def note(self,text,top=None,shade=True):
        if top is None: top=self.y
        wrapped=wrap(text,PW-31,'Lato',9.1)
        if len(wrapped)>3:raise ValueError('Note is too long '+text[:60])
        hh=19+len(wrapped)*12.6
        rect(L,top,PW,hh,fill=WASH if shade else WHITE,radius=3)
        rect(L,top,3,hh,fill=TEAL)
        for i,s in enumerate(wrapped): txt(L+17,top+9+i*12.6,s,'Lato',9.1,BODY)
        self.y=top+hh+13
        return self.y

    def table(self,headers,widths,rowcount,rowh=49,headerh=33,top=None,preprints=None):
        if top is None:top=self.y
        if abs(sum(widths)-PW)>0.01: raise ValueError('Table width not equal page width')
        total=headerh+rowcount*rowh
        rect(L,top,PW,headerh,fill=WASH)
        line(L,top,W-R,top,PALE,.7)
        line(L,top+headerh,W-R,top+headerh,RULE,.85)
        x=L
        for i,(label,w) in enumerate(zip(headers,widths)):
            label_lines=wrap(label,w-15,'LatoBold',8.85)
            if len(label_lines)>2:raise ValueError('Header overflow '+label)
            for j,ln in enumerate(label_lines):txt(x+9,top+7+j*10,ln,'LatoBold',8.85,NAVY)
            x+=w
            if i<len(headers)-1:
                line(x,top,x,top+total,PALE,.65)
        for i in range(rowcount):
            rowtop=top+headerh+i*rowh
            if preprints and i<len(preprints):
                lines=wrap(preprints[i],widths[0]-15,'Lato',9.4)
                if len(lines)>3:raise ValueError('Preprinted role name overflow')
                for j,lab in enumerate(lines):txt(L+9,rowtop+13+j*12,lab,'Lato',9.4,BODY)
            line(L,rowtop+rowh,W-R,rowtop+rowh,RULE,.73)
        self.y=top+total+17
        return self.y

    def ruled_sketch(self,top,height):
        rect(L,top,PW,height,fill=WHITE,stroke=RULE,sw=.9)
        # Very faint 1/4 inch cross grid, does not obscure pencil marks.
        gap=18
        for n in range(1,int(PW/gap)):
            line(L+n*gap,top,L+n*gap,top+height,PALE,.32)
        for n in range(1,int(height/gap)):
            line(L,top+n*gap,W-R,top+n*gap,PALE,.32)
        txt(L+10,top+10,'NORTH (IF KNOWN): ______',font='LatoSemi',size=8.9,color=MUTED)
        right_txt(W-R-10,top+10,'ROUGH SKETCH / NOT TO SCALE',font='LatoSemi',size=8,color=MUTED)
        self.y=top+height+14
        return self.y

    def finish(self):
        if self.y>738: raise RuntimeError(f'Page {self.index} overflows content area, bottom={self.y:.1f}')
        line(L,745,W-R,745,PALE,.9)
        txt(L,756,'BLANK MASTER  |  Keep completed pages and original files in private storage',font='Lato',size=7.65,color=MUTED)
        right_txt(W-R,756,f'{self.code}   /   {self.index:02d} OF {TOTAL:02d}',font='LatoBold',size=7.65,color=MUTED)
        c.showPage()

# 01 - quick, useful front page
p=Page(1,'START','A better record starts here','A practical set of blank forms for documenting drainage, water conditions, construction activity and agency responses.','PRINT GUIDE')
p.note('Start with the Event observation sheet on page 3. You do not need to use every form or understand engineering to contribute a useful record.')
p.section(1,'Five habits that keep the record reliable')
items=[
 ('WRITE IT DOWN','Record the date, time, safe viewing location and what you actually saw.'),
 ('SAVE THE ORIGINAL','Keep unchanged photos, video, messages and documents in protected storage.'),
 ('BE SPECIFIC','Connect notes to a photo ID, a document number or a person who provided the information.'),
 ('RECORD NORMAL DAYS','Dry conditions, earlier drainage problems and completed repairs matter too.'),
 ('KEEP QUESTIONS OPEN','If a cause, elevation, ownership or completed repair is not verified, mark it unknown.'),
]
y=p.y
for i,(head,body) in enumerate(items):
    rect(L,y+1,22,22,fill=WASH,radius=5)
    center_txt(L+11,y+4,str(i+1),'LatoBold',10,TEAL)
    txt(L+34,y-1,head,'LatoBold',9.3,NAVY)
    yend=paragraph(body,y+13,x=L+34,maxwidth=PW-34,size=9.1,leading=12.5,color=MUTED,max_lines=2)
    y=yend+12
p.y=y+4
p.section(2,'Which pages should I print?')
# two-column use cases, each single-line with short description
pages=[
 ('03','Event observations'),('04','Photo and video index'),
 ('06','Draw the water path'),('07','Drainage feature notes'),
 ('09','Official record worksheet'),('10','Request and response'),
 ('11','Meeting or inspection'),('13','Documented roles'),
]
colw=(PW-20)/2
start=p.y
for i,(no,lab) in enumerate(pages):
    col=i%2;row=i//2
    x=L+col*(colw+20)
    yt=start+row*30
    txt(x,yt,no,'LatoBold',9.2,TEAL)
    txt(x+28,yt,lab,'Lato',9.6,BODY)
p.y=start+4*30+15
p.note('SAFETY & PRIVACY  Stay out of moving water, traffic, work zones and other property. Completed pages may contain private information; share only with permission.')
p.note('SIMPLE REFERENCE IDS  E-001 = event, P-001 = photograph, F-001 = feature, R-001 = record, C-001 = contact. Use one ID consistently across the pages.')
p.finish()

# 02 - baseline
p=Page(2,'BASELINE','Property and earlier conditions','Complete once per household, then update only when you learn something new. A memory is useful, but it is not a survey.')
p.section(1,'Reference details')
p.fields([('Resident code (not full name)',1.4),('Date completed / time zone',1.15),('Area or property (private)',2)],height=51)
p.section(2,'What you personally remember from before nearby work')
p.write('Describe typical runoff, ponding, drains, storms, and how long water remained.',rows=4)
p.fields([('Approximate dates / years you directly observed',2),('Earliest related photo or record ID',1.3)],height=48)
p.checks(['Earlier ponding or runoff problems','Earlier drainage worked normally','I was not here before the work','I cannot recall enough to compare'],cols=2)
p.section(3,'Other sources and present-day comparison')
p.write('Earlier conditions reported by someone else or shown in a record (give source + date).',rows=2)
p.write('What looks different today? Add event or photo IDs. Record uncertainty.',rows=3)
p.finish()

# 03 - EVENT - primary one page field form
p=Page(3,'EVENT','Event observation record','Use one copy for each rain, dry-day or construction event. Only describe what you personally witnessed.')
p.section(1,'When and where')
p.fields([('Event ID',.7),('Date + local time / time zone',1.75),('Observer code',.9)],height=47)
p.fields([('Location / safe viewpoint',2),('Start / end time',.9),('Form completed date',1.2)],height=48)
p.section(2,'Conditions')
p.checks(['Raining','Rain recently ended','Dry weather','Standing water','Water visibly flowing','No unusual water seen'],cols=3,row_height=24)
p.fields([('Rain timing, amount and source (if known)',2),('Direction water moved / not clear',1.5)],height=48)
p.section(3,'Direct observation')
p.write('What did you see? Include water location, extent, timing, and any measurement + method.',rows=4)
p.section(4,'Sources and uncertainty')
p.write('Earlier conditions, other possible factors and what remains unknown.',rows=2)
p.fields([('Photo / video / record IDs',1.7),('Same viewpoint as older photo?  Yes / No / Unknown',2)],height=45)
p.finish()

# 04 - PHOTO INDEX
p=Page(4,'PHOTO','Photo, video and file index','Give each file one stable ID. Do not edit the original. This is an index, not a place to attach private files.')
p.note('An annotated or cropped version needs a separate ID. Record the original filename exactly. A file hash is optional and does not prove when or where an image was captured.')
for i in (1,2):
    p.section(i,f'File {i} - complete all fields you know')
    p.fields([('File ID',.75),('Original filename exactly as saved',2.5),('Photo / video / other',1)],height=48)
    p.fields([('Capture date/time + time zone (or unknown)',1.9),('Who made or supplied it? Private code',1.7)],height=48)
    p.fields([('Location / camera direction (private)',2),('Related event ID',.8),('Original stored at (private ref)',1.5)],height=48)
    p.fields([('SHA-256 or hash record ID (optional)',2),('Edited / share copy ID (if any)',1.4)],height=47)
p.finish()

# 05 - REPEATED RAINFALL
p=Page(5,'WEATHER','Rain and repeat observations','Compare rainfall and drainage conditions over time, including normal dry days.')
p.fields([('Observer code',1),('Viewpoint or area (private)',2),('Time zone',.7)],height=51)
p.note('Label each rain number as measured or reported. Include the source and period. A forecast is not an observed rainfall total.')
p.section(1,'Daily or storm-by-storm record')
p.table(['Date + local time','Rain + period + source','Water / drainage observed','Event or photo ID'],[106,140,185,85],rowcount=5,rowh=52,headerh=38)
p.section(2,'Comparison notes')
p.write('What changed across events? Note differences in storm duration, earlier problems or work completed.',rows=3)
p.finish()

# 06 - SKETCH
p=Page(6,'MAP','Sketch the area and water path','Draw from a safe location. Mark roads, houses, swales, pipes, inlets, outlet points and camera positions. Not a survey.')
p.fields([('Sketch / event ID',1),('Date / time',1),('Location / safe viewpoint',2)],height=51)
p.note('Use solid arrows for water movement you actually observed; use a question mark for a suspected or unknown connection. Do not estimate boundaries, slopes or pipe sizes by eye.')
p.ruled_sketch(top=p.y+3,height=386)
p.write('Legend, source photo IDs, uncertain locations or other notes',rows=2)
p.finish()

# 07 - FEATURE
p=Page(7,'FEATURE','Drainage feature and work notes','Use one sheet per pipe, ditch, inlet, outlet or related feature. Separate firsthand conditions from records.')
p.fields([('Feature ID',.9),('Location / nearest landmark (private)',2.2),('Date + local time',1.3)],height=49)
p.checks(['Ditch / swale','Pipe / culvert','Inlet / catch basin','Outlet / outfall','Road / driveway','Other / uncertain'],cols=3,row_height=25)
p.section(1,'Directly observed condition')
p.write('Describe water, sediment, debris, damage, movement or visible work, with dates.',rows=4)
p.fields([('Event / photo IDs',1.25),('Work date (if observed)',1),('Measurement / method (or not measured)',1.9)],height=48)
p.section(2,'What an official document states')
p.write('Plan, inspection or work record: reference ID + wording and date. Proposed is not completed.',rows=3)
p.fields([('Documented owner or maintainer / source ID',2.25),('Still needs verification',1.4)],height=46)
p.finish()

# 08 - THREE TIMES
p=Page(8,'COMPARE','Before, during and after','Compare the same location and conditions over time. If a period has no firsthand evidence, mark it unknown.')
p.fields([('Comparison ID',1),('Viewpoint / location (private)',2),('Prepared date',1)],height=50)
for no,name,label in [(1,'Before nearby work','Dates, what was present and which photos or records support it.'),(2,'During nearby work','Dates, observations and supporting photos or records.'),(3,'After the observed work','Dates, what changed or stayed the same and supporting references.')]:
    p.section(no,name)
    p.write(label,rows=3)
p.checks(['Same viewpoint confirmed','Comparable rainfall confirmed','Earlier conditions not known','Different conditions may explain change'],cols=2,row_height=28)
p.finish()

# 09 - SOURCE RECORD
p=Page(9,'RECORD','Official document worksheet','Use for an obtained permit, plan, survey, inspection, correspondence or recorded instrument. Keep its original unchanged.')
p.section(1,'Document identity')
p.fields([('Record ID',.8),('Exact title / document number',2.2),('Document date',1)],height=47)
p.fields([('Agency / issuing source',1.5),('Obtained on + from where',2),('Version / page reference',1.25)],height=47)
p.section(2,'What it actually says')
p.write('Quote or summarize accurately. Include page, drawing, condition or note number.',rows=4)
p.checks(['Proposed / recommended','Approved / issued','Inspection comment','Recorded / certified','Completion documented','Status is unclear'],cols=3,row_height=25)
p.section(3,'What this record does NOT establish')
p.write('Which detail remains unconfirmed? Include competing information or limitations.',rows=3)
p.fields([('Original document retained at (private reference)',2),('Related feature / permit / event IDs',1.5)],height=46)
p.finish()

# 10 - CORRESPONDENCE
p=Page(10,'CONTACT','Request and response record','Use one sheet per request, inspection report or other contact. A prepared draft does not mean it was sent.')
p.section(1,'Who was contacted and when')
p.fields([('Contact ID',.9),('Office / agency / role',2.2),('Sent date + time zone',1.3)],height=50)
p.fields([('Method / destination (private)',2),('Receipt, case or request number',1.45)],height=49)
p.section(2,'Exact information requested')
p.write('What existing records or actions did you ask for? Keep an unchanged copy of the outgoing message.',rows=3)
p.fields([('Status: Draft / Sent / Acknowledged / Partial / Answered',2.4),('Reply date',.9)],height=48)
p.section(3,'What was received and what is outstanding')
p.write('Write the exact response, missing items and filename or record IDs. Do not fill gaps by guessing.',rows=4)
p.fields([('Original reply + attachments saved?  Yes / No / Pending',2.2),('Next follow-up date / who',1.45)],height=45)
p.finish()

# 11 - MEETING
p=Page(11,'MEETING','Meeting and inspection notes','Record direct quotations separately from paraphrases. A promise to do work is different from confirmation it was done.')
p.fields([('Meeting / visit ID',1.05),('Date, start / end + time zone',1.65),('Location / format',1.25)],height=49)
p.fields([('Agency, department and roles of attendees',2.6),('Note taker private code',1.15)],height=49)
p.section(1,'Questions and answers')
p.write('Question(s) asked, including the person or office who answered.',rows=3)
p.write('Response given. Label exact quote versus your own description.',rows=3)
p.section(2,'Actions and follow-up')
p.table(['Promised record, visit or action','Contact / office','Agreed date','Proof or status ID'],[211,129,75,101],rowcount=2,rowh=46,headerh=35)
p.fields([('Case / inspection reference',1.4),('Written findings or documents received? IDs',2)],height=45)
p.finish()

# 12 - WORK PROGRESS
p=Page(12,'UPDATE','Work, repairs and condition changes','Track actual activity or changes after reported work. Record what you observed and who a source identified.')
p.fields([('Change / work ID',1),('Feature / area (private)',1.9),('Observed date(s)',1.25)],height=49)
p.checks(['I saw activity directly','Another person reported it','Agency record describes it','Work only proposed','Completion unconfirmed','Follow-up observed'],cols=2,row_height=25)
p.section(1,'Condition sequence')
p.write('BEFORE - date, condition and photo ID',rows=2)
p.write('DURING - what was actually seen, when and photo ID',rows=2)
p.write('AFTER - condition, date and photo ID (or not yet observed)',rows=2)
p.section(2,'Records and remaining questions')
p.fields([('Who performed or recorded the work? Include source ID',2.3),('Acceptance / work order ID if known',1.3)],height=48)
p.write('What remains unknown about installation, function, inspection or ongoing upkeep?',rows=2)
p.finish()

# 13 - ROLES
p=Page(13,'ROLES','Who is documented for each role?','Use names only when a dated source identifies them. Several organizations may have different roles for the same location.')
p.note('Do not infer who maintains a structure from road classification alone. Keep each pipe, ditch or outlet distinct, with its source ID and date.')
p.section(1,'Evidence-based role tracker')
roles=[
 'Recorded property interest',
 'Permit applicant / holder',
 'Builder / performing contractor',
 'Approved plan designer',
 'Approving / reviewing office',
 'Inspector / finding',
 'Roadway or right-of-way office',
 'Pipe / inlet / swale / outlet maintainer',
]
p.table(['Role to verify','Organization / name on record','Source ID, date and exact basis'],[166,158,192],rowcount=8,rowh=48,headerh=38,preprints=roles)
p.fields([('Unverified role or source needed next',2),('Related feature IDs',1.1)],height=48)
p.finish()

# 14 - EVIDENCE ORIGINALS
p=Page(14,'ORIGINALS','Original files and handoff log','Use a stable evidence ID. Preserve unchanged originals, and record every copy or transfer separately.')
p.section(1,'Identify and locate the original')
p.fields([('Evidence ID',.9),('Exact filename or paper document title',2.9)],height=49)
p.fields([('Source / acquired from (private)',1.75),('Received date + time zone',1.55)],height=49)
p.fields([('Original stored where? (private protected reference)',2.35),('SHA-256 hash or hash record ID',1.7)],height=49)
p.section(2,'Copies and transfers')
p.table(['Date + time','From / to (private codes)','File or copy ID + how sent / purpose'],[108,177,231],rowcount=3,rowh=51,headerh=35)
p.section(3,'Original preservation and sharing status')
p.checks(['Original remains unmodified','Access is restricted','Metadata treated as private','Edited copy has a new ID','Permission checked before sharing','Original source is still available'],cols=2,row_height=27)
p.fields([('Related event, record or photo IDs',2),('Who keeps the original? Private code',1.6)],height=47)
p.finish()

# 15 - PROPERTY EFFECTS
p=Page(15,'PROPERTY','Property conditions and expenses','PRIVATE. Record actual effects, earlier conditions and receipts separately from theories about the cause.')
p.fields([('Property-effect ID',1),('Area affected (private)',1.9),('First observed date',1.3)],height=50)
p.section(1,'Describe the condition you observed')
p.write('Location, dimensions if measured, time, what was wet or damaged, and when it changed.',rows=3)
p.fields([('Related photo / event IDs',1.8),('Earlier known condition? Source ID or unknown',2)],height=48)
p.section(2,'Maintenance, cleanup and repairs')
p.write('What action was taken? By whom, when, and what written records or photos exist?',rows=2)
p.section(3,'Expense record')
p.table(['Date / item or effect','Estimate vs. paid + amount','Receipt, invoice or source ID'],[188,165,163],rowcount=2,rowh=47,headerh=36)
p.write('Other factors or unresolved questions (prior wear, other weather, missing inspection).',rows=1)
p.finish()

# 16 - OPEN GAPS
p=Page(16,'GAPS','Missing records and next steps','Check only what has actually been received. A missing document is an open question until the source responds.')
p.section(1,'Records or findings physically or digitally in hand')
records=[
 'Approved grading/site plans and dated revisions',
 'Relevant original and current surveys with datum',
 'Drainage design details and calculations (if applicable)',
 'Pipe sizes, inlet / invert / outlet measurements',
 'Verified downstream water path and outlet',
 'Recorded drainage easements and maintenance agreements',
 'Permit conditions, inspection logs and revisions',
 'Written asset ownership and maintenance information',
 'Environmental authorization / applicability response',
 'Documented field visit and written findings',
]
p.checks(records,cols=1,row_height=26,size=9.7)
p.fields([('Permit, parcel or feature IDs concerned',2),('Updated date',1)],height=45)
p.section(2,'Most important information still needed')
p.write('1. What is missing, who may have it, and which request / case ID applies?',rows=2)
p.write('2. What is missing, who may have it, and which request / case ID applies?',rows=2)
p.fields([('Next action, owner (private code) and follow-up date',1)],height=45)
p.finish()

# 17 - PRIVACY BEFORE SHARING
p=Page(17,'SHARING','Sharing review and permission','This page stays private. Share only a separately prepared, approved summary when appropriate.','PRIVATE REVIEW')
p.fields([('Proposed summary ID',1),('Date',.8),('Supporting event / record IDs',2)],height=47)
p.section(1,'What is supported by firsthand records?')
p.write('Short, accurate summary, with dates and general locations approved for sharing.',rows=3)
p.section(2,'What do the obtained documents establish?')
p.write('Name the issuing source, document date and precise page or record references.',rows=3)
p.section(3,'What is still unverified?')
p.write('Outstanding grades, installed drainage, outfall, upkeep or competing explanations.',rows=2)
p.section(4,'Privacy and accuracy checks')
p.checks(['No original images or hidden GPS data','No unnecessary private contact details','No identifiable uninvolved people','Every source ID and date checked','Uncertainty and alternative factors included','Resident approved their own words'],cols=2,row_height=26,size=9.2)
p.fields([('Approved to share this specific summary?  Yes / No',2),('Reviewer and date (private reference)',1.4)],height=46)
p.finish()

# 18 - CONTINUATION
p=Page(18,'NOTES','Continuation and additional notes','Attach this page to any other form when you need more space. Repeat the related form or event ID.')
p.fields([('Related form / event / record ID',1.6),('Page ___ of ___',.8),('Date + time zone',1.15)],height=50)
p.section(1,'Additional firsthand notes or source quotations')
p.write('Continue without overwriting the original entry. Label direct observations, quotes and inferences.',rows=15,leading=24)
p.fields([('Additional evidence IDs or original document references',2.2),('Recorder (private code)',1)],height=48)
p.note('Corrections: add the new date, what changed and why. Keep the earlier entry rather than silently replacing it.')
p.finish()

c.save()

# Standalone prints are extracted from the same master pages. Never duplicate
# descriptions by maintaining independent templates that can become stale.
from pypdf import PdfReader, PdfWriter

EXPORTS = {
    '03_Event_Observation.pdf': 3,
    '04_Photo_and_Video_Index.pdf': 4,
    '10_Request_and_Response.pdf': 10,
    '11_Meeting_and_Inspection_Notes.pdf': 11,
    '13_Documented_Roles.pdf': 13,
    '14_Original_Files_and_Handoff.pdf': 14,
    '16_Missing_Records_Checklist.pdf': 16,
    '18_Continuation_Page.pdf': 18,
}
reader = PdfReader(str(OUT))
if len(reader.pages) != TOTAL:
    raise RuntimeError(f'Expected {TOTAL} pages, found {len(reader.pages)}')
for filename, number in EXPORTS.items():
    output = OUT_DIR / filename
    writer = PdfWriter()
    writer.add_page(reader.pages[number - 1])
    writer.add_metadata({'/Title': 'Tom Street - ' + filename.replace('_', ' ').removesuffix('.pdf'),
                         '/Subject': 'Blank neighborhood documentation worksheet'})
    with output.open('wb') as fp:
        writer.write(fp)
    extracted = (PdfReader(str(output)).pages[0].extract_text() or '')
    if len(extracted) < 150:
        raise RuntimeError('Missing extractable text in ' + filename)

# Text-only sidecar supports review without including private input files.
checksums = sorted((p.name, hashlib.sha256(p.read_bytes()).hexdigest())
                   for p in OUT_DIR.glob('*.pdf'))
print(json.dumps({'master': OUT.name, 'pages': TOTAL, 'standalone': len(EXPORTS),
                  'pdf_sha256': dict(checksums)}, indent=2))
