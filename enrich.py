import csv, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

SRC = "/root/.claude/uploads/87f376ba-3f62-5e40-825b-88b9f5b8ff90/ffaf3307-optum_ny_providers.csv"
LOC_SRC = "/root/.claude/uploads/87f376ba-3f62-5e40-825b-88b9f5b8ff90/1581b988-optum_ny_locations.csv"
OUT = "/home/user/Research-Project/optum_ny_providers_enriched.xlsx"

# --- NUCC taxonomy code -> readable specialty (verified) ---
SPEC = {
 "363LF0000X":"Nurse Practitioner, Family","207R00000X":"Internal Medicine",
 "225100000X":"Physical Therapist","207Q00000X":"Family Medicine",
 "207V00000X":"Obstetrics & Gynecology","363A00000X":"Physician Assistant",
 "363AM0700X":"Physician Assistant, Medical","208000000X":"Pediatrics",
 "208M00000X":"Hospitalist","207RC0000X":"Internal Medicine, Cardiovascular Disease",
 "207RG0100X":"Internal Medicine, Gastroenterology","363LA2200X":"Nurse Practitioner, Adult Health",
 "207L00000X":"Anesthesiology","2085R0202X":"Radiology, Diagnostic Radiology",
 "363AS0400X":"Physician Assistant, Surgical","207X00000X":"Orthopaedic Surgery",
 "207RE0101X":"Internal Medicine, Endocrinology, Diabetes & Metabolism",
 "2084N0400X":"Psychiatry & Neurology, Neurology","207RP1001X":"Internal Medicine, Pulmonary Disease",
 "183500000X":"Pharmacist","363L00000X":"Nurse Practitioner",
 "207RR0500X":"Internal Medicine, Rheumatology","208800000X":"Urology",
 "207N00000X":"Dermatology","208600000X":"Surgery","174400000X":"Specialist",
 "207RH0003X":"Internal Medicine, Hematology & Oncology","225X00000X":"Occupational Therapist",
 "207W00000X":"Ophthalmology","207P00000X":"Emergency Medicine",
 "207RN0300X":"Internal Medicine, Nephrology","367A00000X":"Advanced Practice Midwife",
 "208100000X":"Physical Medicine & Rehabilitation","213E00000X":"Podiatrist",
 "133V00000X":"Dietitian, Registered","207RG0300X":"Internal Medicine, Geriatric Medicine",
 "213ES0103X":"Podiatrist, Foot & Ankle Surgery","2084P0800X":"Psychiatry & Neurology, Psychiatry",
 "207QS0010X":"Family Medicine, Sports Medicine","207XS0106X":"Orthopaedic Surgery, Surgery of the Hand",
 "207RC0001X":"Internal Medicine, Clinical Cardiac Electrophysiology",
 "207RI0011X":"Internal Medicine, Interventional Cardiology","363LA2100X":"Nurse Practitioner, Acute Care",
 "207RI0200X":"Internal Medicine, Infectious Disease","207Y00000X":"Otolaryngology",
 "1041C0700X":"Social Worker, Clinical","1223G0001X":"Dentist, General Practice",
 "1223P0221X":"Dentist, Pediatric Dentistry","170300000X":"Genetic Counselor (M.S.)",
 "231H00000X":"Audiologist","207ZP0102X":"Pathology, Anatomic & Clinical Pathology",
 "207RS0010X":"Internal Medicine, Sports Medicine","152W00000X":"Optometrist",
 "103TC0700X":"Psychologist, Clinical","363LW0102X":"Nurse Practitioner, Women's Health",
 "2251X0800X":"Physical Therapist, Hand","208G00000X":"Thoracic Surgery (Cardiothoracic)",
 "2081P2900X":"Physical Medicine & Rehab, Pain Medicine","207K00000X":"Allergy & Immunology",
 "2086S0129X":"Surgery, Vascular Surgery","207YX0905X":"Otolaryngology, Otolaryngic Allergy",
 "207VM0101X":"Obstetrics & Gynecology, Maternal & Fetal Medicine",
 "2086S0105X":"Surgery, Surgery of the Hand","208VP0014X":"Pain Medicine, Interventional",
 "208VP0000X":"Pain Medicine","208200000X":"Plastic Surgery",
 "363LX0001X":"Nurse Practitioner, Obstetrics & Gynecology",
 "2080P0205X":"Pediatrics, Pediatric Emergency Medicine","176B00000X":"Midwife",
 "163WD0400X":"Registered Nurse, Diabetes Educator","367500000X":"Nurse Anesthetist (CRNA)",
 "2085R0204X":"Radiology, Vascular & Interventional","225200000X":"Physical Therapy Assistant",
 "225XH1200X":"Occupational Therapist, Hand","104100000X":"Social Worker",
 "1223X0400X":"Dentist, Orthodontics & Dentofacial Orthopedics",
 "207RA0201X":"Internal Medicine, Allergy & Immunology","207ND0101X":"Dermatology, MOHS Surgery",
 "207PH0002X":"Emergency Medicine, Hospice & Palliative","207VG0400X":"Obstetrics & Gynecology, Gynecology",
 "2080A0000X":"Pediatrics, Adolescent Medicine","207RC0200X":"Internal Medicine, Critical Care",
 "207XX0801X":"Orthopaedic Surgery, Orthopaedic Trauma","103TF0000X":"Psychologist, Family",
 "363LC1500X":"Nurse Practitioner, Community Health","207ZD0900X":"Pathology, Dermatopathology",
 "171100000X":"Acupuncturist","235Z00000X":"Speech-Language Pathologist",
 "363LP0808X":"Nurse Practitioner, Psychiatric/Mental Health",
 "207XX0004X":"Orthopaedic Surgery, Foot & Ankle Surgery","207QA0505X":"Family Medicine, Adult Medicine",
 "207ZP0101X":"Pathology, Anatomic Pathology","363LP0200X":"Nurse Practitioner, Pediatrics",
 "207RX0202X":"Internal Medicine, Medical Oncology","207QA0000X":"Family Medicine, Adolescent Medicine",
 "207XS0114X":"Orthopaedic Surgery, Adult Reconstructive","207T00000X":"Neurological Surgery",
 "2085D0003X":"Radiology, Diagnostic Neuroimaging","2080P0206X":"Pediatrics, Pediatric Endocrinology",
 "363LP2300X":"Nurse Practitioner, Primary Care","2085N0700X":"Radiology, Nuclear Radiology",
 "213EP1101X":"Podiatrist, Primary Podiatric Medicine","207NS0135X":"Dermatology, Pediatric Dermatology",
 "207XX0005X":"Orthopaedic Surgery, Sports Medicine","207QB0002X":"Family Medicine, Obesity Medicine",
 "390200000X":"Student in Training Program","363LC0200X":"Nurse Practitioner, Critical Care",
 "122300000X":"Dentist","207YS0123X":"Otolaryngology, Sleep Medicine",
 "261QR0400X":"Clinic/Center, Rehabilitation","103T00000X":"Psychologist",
 "225XP0019X":"Occupational Therapist, Pediatrics","207WX0107X":"Ophthalmology, Retina Specialist",
 "101YM0800X":"Counselor, Mental Health","2081S0010X":"Physical Medicine & Rehab, Sports Medicine",
 "171W00000X":"Contractor","207QH0002X":"Family Medicine, Hospice & Palliative",
 "207VH0002X":"Obstetrics & Gynecology, Hospice & Palliative","163W00000X":"Registered Nurse",
 "2251P0200X":"Physical Therapist, Pediatrics","364SA2200X":"Clinical Nurse Specialist, Adult Health",
}

# --- City -> NY county (NYC shown by borough). Authoritative for cities in this dataset. ---
CITY_COUNTY = {
 # NYC
 "new york":"Manhattan","manhattan":"Manhattan","bronx":"Bronx",
 "brooklyn":"Brooklyn","staten island":"Staten Island",
 "astoria":"Queens","flushing":"Queens","long island city":"Queens","maspeth":"Queens",
 "rego park":"Queens","jamaica":"Queens","forest hills":"Queens","fresh meadows":"Queens",
 "bayside":"Queens","elmhurst":"Queens","corona":"Queens","jackson heights":"Queens",
 "woodside":"Queens","whitestone":"Queens","ridgewood":"Queens","sunnyside":"Queens",
 "ozone park":"Queens","howard beach":"Queens","far rockaway":"Queens","middle village":"Queens",
 # Nassau
 "bethpage":"Nassau","farmingdale":"Nassau","garden city park":"Nassau","jericho":"Nassau",
 "new hyde park":"Nassau","rockville centre":"Nassau","syosset":"Nassau","garden city":"Nassau",
 "mineola":"Nassau","hempstead":"Nassau","great neck":"Nassau","hicksville":"Nassau",
 "levittown":"Nassau","massapequa":"Nassau","plainview":"Nassau","valley stream":"Nassau",
 "westbury":"Nassau","glen cove":"Nassau","long beach":"Nassau","oceanside":"Nassau",
 "wantagh":"Nassau","merrick":"Nassau","bellmore":"Nassau","freeport":"Nassau",
 "lynbrook":"Nassau","manhasset":"Nassau","port washington":"Nassau","roslyn":"Nassau",
 "franklin square":"Nassau","elmont":"Nassau","uniondale":"Nassau","east meadow":"Nassau",
 "floral park":"Nassau","baldwin":"Nassau","seaford":"Nassau","new hyde park":"Nassau",
 # Suffolk
 "bay shore":"Suffolk","riverhead":"Suffolk","smithtown":"Suffolk","huntington":"Suffolk",
 "babylon":"Suffolk","islip":"Suffolk","patchogue":"Suffolk","brentwood":"Suffolk",
 "commack":"Suffolk","hauppauge":"Suffolk","stony brook":"Suffolk","port jefferson":"Suffolk",
 "sayville":"Suffolk","bohemia":"Suffolk","ronkonkoma":"Suffolk","west islip":"Suffolk",
 "deer park":"Suffolk","central islip":"Suffolk","medford":"Suffolk","amityville":"Suffolk",
 "lindenhurst":"Suffolk","east setauket":"Suffolk","huntington station":"Suffolk",
 # Westchester
 "cortlandt manor":"Westchester","jefferson valley":"Westchester","katonah":"Westchester",
 "mount kisco":"Westchester","rye":"Westchester","yonkers":"Westchester","white plains":"Westchester",
 "new rochelle":"Westchester","mount vernon":"Westchester","scarsdale":"Westchester",
 "harrison":"Westchester","mamaroneck":"Westchester","port chester":"Westchester",
 "tarrytown":"Westchester","ossining":"Westchester","peekskill":"Westchester","bedford":"Westchester",
 "chappaqua":"Westchester","pleasantville":"Westchester","hartsdale":"Westchester",
 "hawthorne":"Westchester","valhalla":"Westchester","elmsford":"Westchester","dobbs ferry":"Westchester",
 "larchmont":"Westchester","bronxville":"Westchester","eastchester":"Westchester","tuckahoe":"Westchester",
 "yorktown heights":"Westchester","somers":"Westchester","briarcliff manor":"Westchester",
 "thornwood":"Westchester","mohegan lake":"Westchester","croton on hudson":"Westchester",
 # Putnam
 "brewster":"Putnam","carmel":"Putnam","mahopac":"Putnam","cold spring":"Putnam",
 "patterson":"Putnam","putnam valley":"Putnam",
 # Dutchess
 "fishkill":"Dutchess","poughkeepsie":"Dutchess","rhinebeck":"Dutchess","beacon":"Dutchess",
 "wappingers falls":"Dutchess","hyde park":"Dutchess","hopewell junction":"Dutchess",
 "pleasant valley":"Dutchess","red hook":"Dutchess","millbrook":"Dutchess","pawling":"Dutchess",
 # Orange
 "goshen":"Orange","middletown":"Orange","monroe":"Orange","new windsor":"Orange",
 "newburgh":"Orange","warwick":"Orange","cornwall":"Orange","chester":"Orange",
 "washingtonville":"Orange","montgomery":"Orange","walden":"Orange","highland falls":"Orange",
 "port jervis":"Orange","florida":"Orange","pine bush":"Orange","central valley":"Orange",
 # Rockland
 "new city":"Rockland","orangeburg":"Rockland","pomona":"Rockland","west nyack":"Rockland",
 "nyack":"Rockland","nanuet":"Rockland","suffern":"Rockland","spring valley":"Rockland",
 "pearl river":"Rockland","monsey":"Rockland","haverstraw":"Rockland","stony point":"Rockland",
 "congers":"Rockland","valley cottage":"Rockland","tappan":"Rockland",
 # Ulster
 "new paltz":"Ulster","kingston":"Ulster","saugerties":"Ulster","highland":"Ulster",
 "ellenville":"Ulster","woodstock":"Ulster","wallkill":"Ulster",
 # Sullivan
 "rock hill":"Sullivan","monticello":"Sullivan","liberty":"Sullivan","wurtsboro":"Sullivan",
 # additional cities present in the full locations file
 "albany":"Albany","airmont":"Rockland","chestnut ridge":"Rockland",
 "lawrence":"Nassau","east rockaway":"Nassau","wheatley heights":"Suffolk",
 "woodbury":"Nassau","lake success":"Nassau",
}

# zip5-specific overrides for ZIPs whose zip3 spans multiple counties (Hudson Valley/LI edges)
ZIP_COUNTY = {
 "10509":"Putnam","10512":"Putnam","10516":"Putnam","10524":"Putnam","10541":"Putnam","10579":"Putnam",
 "10567":"Westchester","10535":"Westchester","10536":"Westchester","10549":"Westchester","10580":"Westchester","10701":"Westchester",
 "10924":"Orange","10941":"Orange","10950":"Orange","10990":"Orange","12550":"Orange","12553":"Orange",
 "10956":"Rockland","10962":"Rockland","10970":"Rockland","10994":"Rockland",
 "12524":"Dutchess","12572":"Dutchess","12601":"Dutchess",
 "12561":"Ulster","12775":"Sullivan",
 "11040":"Nassau","11042":"Nassau","11714":"Nassau","11735":"Nassau","11753":"Nassau","11570":"Nassau","11791":"Nassau",
 "11706":"Suffolk","11787":"Suffolk","11901":"Suffolk","11798":"Suffolk",
 "10952":"Rockland","10977":"Rockland","11797":"Nassau","11518":"Nassau","11559":"Nassau",
}

ZIP3 = {"100":"Manhattan","101":"Manhattan","102":"Manhattan","103":"Staten Island","104":"Bronx",
        "106":"Westchester","107":"Westchester","108":"Westchester","112":"Brooklyn"}

def county(city, zip5):
    if zip5 in ZIP_COUNTY: return ZIP_COUNTY[zip5]
    c = CITY_COUNTY.get(city.strip().lower())
    if c: return c
    return ZIP3.get(zip5[:3], "")

# --- County -> region (territory planning) ---
REGION_ORDER = ["New York City","Long Island","Lower Hudson Valley","Mid-Hudson Valley","Capital Region"]
COUNTY_REGION = {
 "Manhattan":"New York City","Brooklyn":"New York City","Queens":"New York City",
 "Bronx":"New York City","Staten Island":"New York City",
 "Nassau":"Long Island","Suffolk":"Long Island",
 "Westchester":"Lower Hudson Valley","Rockland":"Lower Hudson Valley","Putnam":"Lower Hudson Valley",
 "Orange":"Mid-Hudson Valley","Dutchess":"Mid-Hudson Valley","Ulster":"Mid-Hudson Valley","Sullivan":"Mid-Hudson Valley",
 "Albany":"Capital Region",
}

# --- Provider type (recruitment buckets) by taxonomy code ---
def provider_type(code):
    if code.startswith("363L"): return "Nurse Practitioner"
    if code.startswith("363A"): return "Physician Assistant"
    if code.startswith("213E"): return "Podiatrist (DPM)"
    if code.startswith("1223") or code == "122300000X": return "Dentist"
    if code.startswith("103T") or code.startswith("1041") or code == "104100000X" or code.startswith("101Y"):
        return "Behavioral Health (non-MD)"
    if (code.startswith("2251") or code.startswith("2252") or code.startswith("225X")
            or code in ("225100000X","225200000X") or code.startswith("235Z") or code.startswith("231H")):
        return "Therapy & Rehab"
    if (code.startswith("163W") or code.startswith("364S") or code == "367500000X" or code.startswith("367A")
            or code.startswith("176B") or code == "183500000X" or code.startswith("133V") or code.startswith("152W")
            or code == "171100000X" or code == "170300000X"):
        return "Other Clinical"
    if code == "174400000X" or code.startswith("171W") or code == "390200000X" or code.startswith("261Q"):
        return "Other / Non-clinical"
    if code[:3] in ("207","208","204"): return "Physician (MD/DO)"
    return "Other / Non-clinical"

# --- Specialty group (clinical area) by taxonomy code ---
GROUP_ORDER = ["Primary Care","Cardiology","Oncology","Medical Specialties","Surgical Specialties",
               "Women's Health","Behavioral Health","Emergency & Hospital Med","Anesthesia/Pain/PM&R",
               "Diagnostics (Rad/Path)","Allied Health","Other"]
_PC="Primary Care";_MS="Medical Specialties";_SS="Surgical Specialties";_WH="Women's Health"
_BH="Behavioral Health";_EH="Emergency & Hospital Med";_AP="Anesthesia/Pain/PM&R"
_DX="Diagnostics (Rad/Path)";_AH="Allied Health";_OT="Other"
_CARD="Cardiology";_ONC="Oncology"
SPEC_GROUP = {
 "363LF0000X":_PC,"207R00000X":_PC,"225100000X":_AH,"207Q00000X":_PC,"207V00000X":_WH,
 "363A00000X":_PC,"363AM0700X":_PC,"208000000X":_PC,"208M00000X":_EH,"207RC0000X":_CARD,
 "207RG0100X":_MS,"363LA2200X":_PC,"207L00000X":_AP,"2085R0202X":_DX,"363AS0400X":_SS,
 "207X00000X":_SS,"207RE0101X":_MS,"2084N0400X":_MS,"207RP1001X":_MS,"183500000X":_AH,
 "363L00000X":_PC,"207RR0500X":_MS,"208800000X":_SS,"207N00000X":_MS,"208600000X":_SS,
 "174400000X":_OT,"207RH0003X":_ONC,"225X00000X":_AH,"207W00000X":_SS,"207P00000X":_EH,
 "207RN0300X":_MS,"367A00000X":_WH,"208100000X":_AP,"213E00000X":_AH,"133V00000X":_AH,
 "207RG0300X":_PC,"213ES0103X":_AH,"2084P0800X":_BH,"207QS0010X":_PC,"207XS0106X":_SS,
 "207RC0001X":_CARD,"207RI0011X":_CARD,"363LA2100X":_PC,"207RI0200X":_MS,"207Y00000X":_SS,
 "1041C0700X":_BH,"1223G0001X":_AH,"1223P0221X":_AH,"170300000X":_OT,"231H00000X":_AH,
 "207ZP0102X":_DX,"207RS0010X":_MS,"152W00000X":_AH,"103TC0700X":_BH,"363LW0102X":_WH,
 "2251X0800X":_AH,"208G00000X":_SS,"2081P2900X":_AP,"207K00000X":_MS,"2086S0129X":_SS,
 "207YX0905X":_SS,"207VM0101X":_WH,"2086S0105X":_SS,"208VP0014X":_AP,"208VP0000X":_AP,
 "208200000X":_SS,"363LX0001X":_WH,"2080P0205X":_MS,"176B00000X":_WH,"163WD0400X":_AH,
 "367500000X":_AP,"2085R0204X":_DX,"225200000X":_AH,"225XH1200X":_AH,"104100000X":_BH,
 "1223X0400X":_AH,"207RA0201X":_MS,"207ND0101X":_MS,"207PH0002X":_EH,"207VG0400X":_WH,
 "2080A0000X":_PC,"207RC0200X":_EH,"207XX0801X":_SS,"103TF0000X":_BH,"363LC1500X":_PC,
 "207ZD0900X":_DX,"171100000X":_AH,"235Z00000X":_AH,"363LP0808X":_BH,"207XX0004X":_SS,
 "207QA0505X":_PC,"207ZP0101X":_DX,"363LP0200X":_PC,"207RX0202X":_ONC,"207QA0000X":_PC,
 "207XS0114X":_SS,"207T00000X":_SS,"2085D0003X":_DX,"2080P0206X":_MS,"363LP2300X":_PC,
 "2085N0700X":_DX,"213EP1101X":_AH,"207NS0135X":_MS,"207XX0005X":_SS,"207QB0002X":_PC,
 "390200000X":_OT,"363LC0200X":_EH,"122300000X":_AH,"207YS0123X":_SS,"261QR0400X":_OT,
 "103T00000X":_BH,"225XP0019X":_AH,"207WX0107X":_SS,"101YM0800X":_BH,"2081S0010X":_AP,
 "171W00000X":_OT,"207QH0002X":_PC,"207VH0002X":_WH,"163W00000X":_AH,"2251P0200X":_AH,
 "364SA2200X":_PC,
}

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))

# --- Build workbook ---
wb = Workbook()
wsP = wb.active; wsP.title = "Providers"
pcols = ["provider_npi","first_name","last_name","credential","provider_type","specialty",
         "specialty_group","specialty_code","match_confidence","brand","location_name","region",
         "county","city","zip","street","phone","location_npi"]
wsP.append(pcols)
unmapped_spec, unmapped_cty = set(), set()
cnt_cty_grp = collections.Counter()   # (county, specialty_group)
cnt_cty_pt  = collections.Counter()   # (county, provider_type)
cnt_reg_grp = collections.Counter()   # (region, specialty_group)
for r in rows:
    code = r["specialty"]
    name = SPEC.get(code, code)
    if code not in SPEC: unmapped_spec.add(code)
    cty = county(r["city"], r["zip"])
    if not cty: unmapped_cty.add((r["city"], r["zip"]))
    reg = COUNTY_REGION.get(cty, "")
    grp = SPEC_GROUP.get(code, _OT)
    pt  = provider_type(code)
    wsP.append([r["provider_npi"], r["first_name"], r["last_name"], r["credential"], pt, name,
                grp, code, r.get("match_confidence",""), r["brand"], r["location_name"], reg, cty,
                r["city"], r["zip"], r["street"], r["phone"], r["location_npi"]])
    cnt_cty_grp[(cty, grp)] += 1
    cnt_cty_pt[(cty, pt)] += 1
    cnt_reg_grp[(reg, grp)] += 1

wsL = wb.create_sheet("Locations")
lcols = ["location_npi","name","brand","county","city","zip","street","phone","provider_count"]
wsL.append(lcols)
loc_rows = list(csv.DictReader(open(LOC_SRC, encoding="utf-8-sig")))
for lr in loc_rows:
    cty = county(lr["city"], lr["zip"])
    if not cty: unmapped_cty.add((lr["city"], lr["zip"]))
    wsL.append([lr["location_npi"], lr["name"], lr["brand"], cty, lr["city"], lr["zip"],
                lr["street"], lr["phone"], int(lr["provider_count"])])

# --- Pivot tabs (static cross-tabs with totals) ---
PT_ORDER = ["Physician (MD/DO)","Nurse Practitioner","Physician Assistant","Podiatrist (DPM)",
            "Dentist","Behavioral Health (non-MD)","Therapy & Rehab","Other Clinical","Other / Non-clinical"]
# counties ordered by region then name
counties_present = sorted({county(r["city"], r["zip"]) for r in rows},
                          key=lambda c: (REGION_ORDER.index(COUNTY_REGION.get(c,"Capital Region")), c))

def add_pivot(title, row_label, row_keys, col_keys, counter, row_region=False):
    ws = wb.create_sheet(title)
    header = ([ "Region", row_label] if row_region else [row_label]) + list(col_keys) + ["Total"]
    ws.append(header)
    col_tot = collections.Counter(); grand = 0
    for rk in row_keys:
        vals = [counter.get((rk, ck), 0) for ck in col_keys]
        rt = sum(vals)
        line = ([COUNTY_REGION.get(rk,""), rk] if row_region else [rk]) + vals + [rt]
        ws.append(line)
        for ck, v in zip(col_keys, vals): col_tot[ck] += v
        grand += rt
    totline = (["",""] if row_region else [""])
    totline[-1] = "TOTAL"
    ws.append(totline + [col_tot[ck] for ck in col_keys] + [grand])
    return ws

p1 = add_pivot("Pivot-County x SpecGroup", "County", counties_present, GROUP_ORDER, cnt_cty_grp, row_region=True)
p2 = add_pivot("Pivot-County x ProviderType", "County", counties_present, PT_ORDER, cnt_cty_pt, row_region=True)
p3 = add_pivot("Pivot-Region x SpecGroup", "Region",
               [r for r in REGION_ORDER if any(k[0]==r for k in cnt_reg_grp)], GROUP_ORDER, cnt_reg_grp)

# formatting: data sheets get filters+freeze; pivots get bold header + bold total row
for ws in (wsP, wsL):
    for cell in ws[1]:
        cell.font = Font(bold=True); cell.alignment = Alignment(vertical="center")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for i in range(1, ws.max_column+1):
        w = max((len(str(ws.cell(row=r, column=i).value or "")) for r in range(1, min(ws.max_row,400)+1)), default=10)
        ws.column_dimensions[get_column_letter(i)].width = min(max(w+2, 11), 48)

for ws in (p1, p2, p3):
    for cell in ws[1]: cell.font = Font(bold=True)
    for cell in ws[ws.max_row]: cell.font = Font(bold=True)
    ws.freeze_panes = "B2"
    for i in range(1, ws.max_column+1):
        w = max((len(str(ws.cell(row=r, column=i).value or "")) for r in range(1, ws.max_row+1)), default=10)
        ws.column_dimensions[get_column_letter(i)].width = min(max(w+2, 9), 26)

wb.save(OUT)
print("Saved", OUT)
print("Providers:", len(rows), "| Locations:", len(loc_rows),
      "| sum provider_count:", sum(int(l["provider_count"]) for l in loc_rows))
print("Provider county breakdown:", dict(collections.Counter(county(r["city"], r["zip"]) for r in rows)))
print("Location county breakdown:", dict(collections.Counter(county(l["city"], l["zip"]) for l in loc_rows)))
print("Unmapped specialty codes:", unmapped_spec or "none")
print("Unmapped city/zip -> county:", unmapped_cty or "none")