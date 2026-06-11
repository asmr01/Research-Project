import csv, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

SRC = "/root/.claude/uploads/87f376ba-3f62-5e40-825b-88b9f5b8ff90/130db19f-optum_directory_ny.csv"
OUT = "/home/user/Research-Project/optum_ny_directory_enriched.xlsx"

# ---- geography (city/zip -> county -> region) ----
CITY_COUNTY = {
 "new york":"Manhattan","manhattan":"Manhattan","bronx":"Bronx","brooklyn":"Brooklyn",
 "staten island":"Staten Island","astoria":"Queens","flushing":"Queens","long island city":"Queens",
 "maspeth":"Queens","rego park":"Queens","forest hills":"Queens","fresh meadows":"Queens",
 "bayside":"Queens","howard beach":"Queens","jamaica":"Queens","middle village":"Queens",
 "bethpage":"Nassau","farmingdale":"Nassau","garden city park":"Nassau","garden city":"Nassau",
 "jericho":"Nassau","new hyde park":"Nassau","rockville centre":"Nassau","syosset":"Nassau",
 "mineola":"Nassau","hicksville":"Nassau","plainview":"Nassau","levittown":"Nassau",
 "valley stream":"Nassau","westbury":"Nassau","great neck":"Nassau","manhasset":"Nassau",
 "lynbrook":"Nassau","oceanside":"Nassau","lawrence":"Nassau","east rockaway":"Nassau",
 "woodbury":"Nassau","lake success":"Nassau","massapequa":"Nassau","wantagh":"Nassau",
 "merrick":"Nassau","bellmore":"Nassau","freeport":"Nassau","franklin square":"Nassau",
 "bay shore":"Suffolk","riverhead":"Suffolk","smithtown":"Suffolk","huntington":"Suffolk",
 "commack":"Suffolk","hauppauge":"Suffolk","wheatley heights":"Suffolk","west islip":"Suffolk",
 "babylon":"Suffolk","islip":"Suffolk","patchogue":"Suffolk","stony brook":"Suffolk",
 "mount kisco":"Westchester","cortlandt manor":"Westchester","jefferson valley":"Westchester",
 "katonah":"Westchester","rye":"Westchester","yonkers":"Westchester","white plains":"Westchester",
 "dobbs ferry":"Westchester","thornwood":"Westchester","yorktown heights":"Westchester",
 "new rochelle":"Westchester","scarsdale":"Westchester","harrison":"Westchester","mamaroneck":"Westchester",
 "ossining":"Westchester","peekskill":"Westchester","mohegan lake":"Westchester","hawthorne":"Westchester",
 "brewster":"Putnam","carmel":"Putnam","mahopac":"Putnam","cold spring":"Putnam",
 "fishkill":"Dutchess","poughkeepsie":"Dutchess","rhinebeck":"Dutchess","beacon":"Dutchess",
 "wappingers falls":"Dutchess","hopewell junction":"Dutchess","hyde park":"Dutchess",
 "goshen":"Orange","middletown":"Orange","monroe":"Orange","new windsor":"Orange",
 "newburgh":"Orange","warwick":"Orange","chester":"Orange","cornwall":"Orange",
 "new city":"Rockland","orangeburg":"Rockland","pomona":"Rockland","west nyack":"Rockland",
 "airmont":"Rockland","chestnut ridge":"Rockland","nyack":"Rockland","nanuet":"Rockland",
 "suffern":"Rockland","pearl river":"Rockland","new paltz":"Ulster","kingston":"Ulster",
 "rock hill":"Sullivan","monticello":"Sullivan","albany":"Albany",
 "croton on hudson":"Westchester","briarcliff manor":"Westchester","seaford":"Nassau",
 "port jefferson":"Suffolk","port jefferson station":"Suffolk","wading river":"Suffolk",
 "miller place":"Suffolk","centereach":"Suffolk","lake katrine":"Ulster",
}
ZIP_COUNTY = {
 "10509":"Putnam","10512":"Putnam","10516":"Putnam","10524":"Putnam","10541":"Putnam","10579":"Putnam",
 "10567":"Westchester","10535":"Westchester","10536":"Westchester","10549":"Westchester","10580":"Westchester","10701":"Westchester",
 "10924":"Orange","10941":"Orange","10950":"Orange","10990":"Orange","12550":"Orange","12553":"Orange",
 "10956":"Rockland","10962":"Rockland","10970":"Rockland","10994":"Rockland","10952":"Rockland","10977":"Rockland",
 "12524":"Dutchess","12572":"Dutchess","12601":"Dutchess","12603":"Dutchess","12561":"Ulster","12775":"Sullivan",
 "11040":"Nassau","11042":"Nassau","11714":"Nassau","11753":"Nassau","11570":"Nassau","11791":"Nassau",
 "11797":"Nassau","11518":"Nassau","11559":"Nassau","11801":"Nassau","11530":"Nassau","11563":"Nassau","11572":"Nassau",
 "11706":"Suffolk","11787":"Suffolk","11901":"Suffolk","11798":"Suffolk","11743":"Suffolk",
}
ZIP3 = {"100":"Manhattan","101":"Manhattan","102":"Manhattan","103":"Staten Island","104":"Bronx",
        "106":"Westchester","107":"Westchester","108":"Westchester","112":"Brooklyn",
        "110":"Queens","111":"Queens","113":"Queens","114":"Queens","116":"Queens","115":"Nassau"}
REGION_ORDER = ["New York City","Long Island","Lower Hudson Valley","Mid-Hudson Valley","Capital Region"]
COUNTY_REGION = {"Manhattan":"New York City","Brooklyn":"New York City","Queens":"New York City",
 "Bronx":"New York City","Staten Island":"New York City","Nassau":"Long Island","Suffolk":"Long Island",
 "Westchester":"Lower Hudson Valley","Rockland":"Lower Hudson Valley","Putnam":"Lower Hudson Valley",
 "Orange":"Mid-Hudson Valley","Dutchess":"Mid-Hudson Valley","Ulster":"Mid-Hudson Valley",
 "Sullivan":"Mid-Hudson Valley","Albany":"Capital Region"}

def parse_city(addr):
    parts = [p.strip() for p in addr.split(",")]
    return parts[-2] if len(parts) >= 2 else ""

def county(addr, zip5):
    if zip5 in ZIP_COUNTY: return ZIP_COUNTY[zip5]
    c = CITY_COUNTY.get(parse_city(addr).lower())
    if c: return c
    return ZIP3.get(zip5[:3], "")

# ---- specialty grouping (name-based) ----
PC,MS,SS,WH,BH,AP,DX,AH,OT="Primary Care","Medical Specialties","Surgical Specialties","Women's Health","Behavioral Health","Anesthesia/Pain/PM&R","Diagnostics (Rad/Path)","Allied Health","Other"
CARD,ONC="Cardiology","Oncology"
GROUP_ORDER=[PC,CARD,ONC,MS,SS,WH,BH,AP,AH,OT]
def spec_group(s):
    n=s.lower()
    if "cardio" in n or "cardiac" in n: return CARD
    if "oncology" in n: return ONC
    if any(k in n for k in ["orthopaedic","orthopedic","surgery","surgical","ophthalmology","otolaryngology","urology","retina"]): return SS
    if any(k in n for k in ["obstetric","gynecolog","midwife","maternal","pelvic"]): return WH
    if any(k in n for k in ["psycholog","behavioral health","counsel","psychiatr"]): return BH
    if any(k in n for k in ["pain medicine","physical medicine","rehabilitation","anesthe"]): return AP
    if any(k in n for k in ["physical therapist","podiatr","audiolog","optometr","nutrition","dietitian","therapist"]): return AH
    if any(k in n for k in ["family medicine","internal medicine","pediatrics","primary care","geriatric","obesity","developmental"]): return PC
    if any(k in n for k in ["dermatology","gastro","endocrin","nephro","rheumat","neurolog","infectious","pulmonary","allergy","sleep","hematology"]): return MS
    return MS

def provider_type(name, specialty):
    cred = name.split(",",1)[1].upper() if "," in name else ""
    toks = set(t.strip() for t in cred.replace("-"," ").split())
    if {"MD","DO"} & toks: return "Physician (MD/DO)"
    if {"NP","FNP","DNP","APRN","ANP","PNP","AGNP","WHNP"} & toks: return "Nurse Practitioner"
    if {"PA","PAC","RPA"} & toks: return "Physician Assistant"
    if "DPM" in toks: return "Podiatrist (DPM)"
    if {"DDS","DMD"} & toks: return "Dentist"
    if {"DPT","PT"} & toks: return "Therapy & Rehab"
    if {"OD","AUD","CNM","CM","RD","RDN"} & toks: return "Other Clinical"
    if {"PHD","PSYD"} & toks or "psycholog" in specialty.lower(): return "Behavioral Health (non-MD)"
    # fallbacks by specialty
    sl=specialty.lower()
    if "midwife" in sl: return "Other Clinical"
    if "physical therapist" in sl: return "Therapy & Rehab"
    if any(k in sl for k in ["audiolog","optometr","nutrition"]): return "Other Clinical"
    return "Physician (MD/DO)"

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
PT_ORDER=["Physician (MD/DO)","Nurse Practitioner","Physician Assistant","Podiatrist (DPM)",
          "Dentist","Behavioral Health (non-MD)","Therapy & Rehab","Other Clinical"]

wb=Workbook(); ws=wb.active; ws.title="Providers"
cols=["npi","display_name","first_name","last_name","gender","provider_type","specialty",
      "specialty_group","accepting_new_patients","employed_or_contract","average_rating",
      "review_count","languages","cdo","region","county","city","zip","address","phone",
      "primary_location_name","num_locations","website_url","schedule_url"]
ws.append(cols)
cnt_cg=collections.Counter(); cnt_cp=collections.Counter(); cnt_rg=collections.Counter()
for r in rows:
    cty=county(r["address"], r["zip"]); reg=COUNTY_REGION.get(cty,"")
    grp=spec_group(r["specialty"]); pt=provider_type(r["display_name"], r["specialty"])
    city=parse_city(r["address"])
    ws.append([r["npi"],r["display_name"],r["first_name"],r["last_name"],r["gender"],pt,r["specialty"],
        grp,r["accepting_new_patients"],r["employed_or_contract"],r["average_rating"],r["review_count"],
        r["languages"],r["cdo"],reg,cty,city,r["zip"],r["address"],r["phone"],
        r["primary_location_name"],r["num_locations"],r["website_url"],r["schedule_url"]])
    cnt_cg[(cty,grp)]+=1; cnt_cp[(cty,pt)]+=1; cnt_rg[(reg,grp)]+=1

counties=sorted({county(r["address"],r["zip"]) for r in rows},
                key=lambda c:(REGION_ORDER.index(COUNTY_REGION.get(c,"Capital Region")),c))
def pivot(title,rowkeys,colkeys,counter,region_col=True):
    s=wb.create_sheet(title)
    s.append((["Region","County"] if region_col else ["Region"])+list(colkeys)+["Total"])
    ctot=collections.Counter(); grand=0
    for rk in rowkeys:
        vals=[counter.get((rk,ck),0) for ck in colkeys]; rt=sum(vals)
        s.append(([COUNTY_REGION.get(rk,""),rk] if region_col else [rk])+vals+[rt])
        for ck,v in zip(colkeys,vals): ctot[ck]+=v
        grand+=rt
    s.append((["","TOTAL"] if region_col else ["TOTAL"])+[ctot[ck] for ck in colkeys]+[grand])
    return s
p1=pivot("Pivot-County x SpecGroup",counties,GROUP_ORDER,cnt_cg)
p2=pivot("Pivot-County x ProviderType",counties,PT_ORDER,cnt_cp)
p3=pivot("Pivot-Region x SpecGroup",[r for r in REGION_ORDER if any(k[0]==r for k in cnt_rg)],GROUP_ORDER,cnt_rg,region_col=False)

for s in (ws,):
    for c in s[1]: c.font=Font(bold=True); c.alignment=Alignment(vertical="center")
    s.freeze_panes="A2"; s.auto_filter.ref=s.dimensions
    for i in range(1,s.max_column+1):
        w=max((len(str(s.cell(row=r,column=i).value or "")) for r in range(1,min(s.max_row,300)+1)),default=10)
        s.column_dimensions[get_column_letter(i)].width=min(max(w+2,11),46)
for s in (p1,p2,p3):
    for c in s[1]: c.font=Font(bold=True)
    for c in s[s.max_row]: c.font=Font(bold=True)
    s.freeze_panes="B2"
    for i in range(1,s.max_column+1):
        w=max((len(str(s.cell(row=r,column=i).value or "")) for r in range(1,s.max_row+1)),default=10)
        s.column_dimensions[get_column_letter(i)].width=min(max(w+2,9),26)

wb.save(OUT)
print("Saved",OUT,"| providers:",len(rows))
print("specialty_group:",dict(collections.Counter(spec_group(r["specialty"]) for r in rows)))
print("provider_type:",dict(collections.Counter(provider_type(r["display_name"],r["specialty"]) for r in rows)))
print("county:",dict(collections.Counter(county(r["address"],r["zip"]) for r in rows)))
print("unmapped county:",{(parse_city(r["address"]),r["zip"]) for r in rows if not county(r["address"],r["zip"])})
