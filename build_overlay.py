import collections
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

SRC="/home/user/Research-Project/Optum_NY_All_Providers.xlsx"
OUT="/home/user/Research-Project/Optum_NY_Comparison.xlsx"

P=load_workbook(SRC)["Providers"]; h=[c.value for c in P[1]]
ci=h.index("county"); pti=h.index("provider_type"); ti=h.index("target_specialty")
rows=list(P.iter_rows(min_row=2,values_only=True))
OUR=collections.Counter((r[pti],r[ci]) for r in rows)
our_cty=collections.Counter(r[ci] for r in rows)
OUR_SPEC=collections.Counter((r[ti],r[ci]) for r in rows)

# Prism (from screenshot; validated to 158 physician + 101 APC = 259)
PRISM={("Bronx","Physician (MD/DO)"):1,("Bronx","Nurse Practitioner"):1,("Bronx","Physician Assistant"):1,
 ("Kings","Physician (MD/DO)"):6,
 ("Nassau","Physician (MD/DO)"):70,("Nassau","Nurse Practitioner"):3,("Nassau","Physician Assistant"):10,("Nassau","Therapy & Rehab"):8,("Nassau","Other Clinical"):1,("Nassau","APC (unspecified)"):10,
 ("New York","Physician (MD/DO)"):28,("New York","Nurse Practitioner"):3,("New York","Physician Assistant"):4,("New York","Therapy & Rehab"):24,
 ("Queens","Physician (MD/DO)"):10,("Queens","Nurse Practitioner"):1,("Queens","Physician Assistant"):3,("Queens","Therapy & Rehab"):4,
 ("Rockland","Physician (MD/DO)"):3,
 ("Suffolk","Physician (MD/DO)"):13,("Suffolk","Nurse Practitioner"):6,("Suffolk","Physician Assistant"):10,("Suffolk","APC (unspecified)"):1,
 ("Westchester","Physician (MD/DO)"):27,("Westchester","Nurse Practitioner"):3,("Westchester","Physician Assistant"):3,("Westchester","Therapy & Rehab"):1,("Westchester","APC (unspecified)"):4}
prism_counties=sorted({c for (c,p) in PRISM})

PT=["Physician (MD/DO)","Nurse Practitioner","Physician Assistant","Therapy & Rehab","Other Clinical",
    "Podiatrist (DPM)","Behavioral Health (non-MD)","Other / Non-clinical","Dentist","APC (unspecified)"]
COUNTIES=[c for c,_ in our_cty.most_common()]
for c in prism_counties:
    if c not in COUNTIES: COUNTIES.append(c)

GREY=PatternFill("solid",fgColor="D9D9D9"); PINK=PatternFill("solid",fgColor="FCE4EC")
RED=PatternFill("solid",fgColor="F4B6C2"); HDR=PatternFill("solid",fgColor="DDEBF7"); TOT=PatternFill("solid",fgColor="F2F2F2")
NOPRISM=PatternFill("solid",fgColor="FFF2CC")
thin=Side(style="thin",color="BFBFBF"); BORD=Border(thin,thin,thin,thin)
bold=Font(bold=True); ctr=Alignment(horizontal="center",vertical="center")

wb=Workbook(); ws=wb.active; ws.title="County x ProviderType"
ws["A1"]="Optum NY — Provider Type × County:  Prism  /  our roster"; ws["A1"].font=Font(bold=True,size=13,color="1F4E78")
ws["A2"]="Cell = Prism count / our-roster count.  PINK = we have providers (overlap shown).  "\
         "RED = Prism > our roster (resolve).  GREY = neither has any.  YELLOW header = county not in Prism."
ws["A2"].font=Font(italic=True,color="C0006C")
r0=4
ws.cell(r0,1,"Provider Type \\ County").font=bold
for j,c in enumerate(COUNTIES,2):
    cc=ws.cell(r0,j,c); cc.font=bold; cc.alignment=ctr; cc.border=BORD
    cc.fill=HDR if c in prism_counties else NOPRISM
ws.cell(r0,len(COUNTIES)+2,"Total (P / ours)").font=bold; ws.cell(r0,len(COUNTIES)+2).fill=HDR; ws.cell(r0,len(COUNTIES)+2).alignment=ctr; ws.cell(r0,len(COUNTIES)+2).border=BORD
for i,pt in enumerate(PT,r0+1):
    ws.cell(i,1,pt).font=bold; ws.cell(i,1).border=BORD
    op_tot=pp_tot=0
    for j,c in enumerate(COUNTIES,2):
        o=OUR.get((pt,c),0); pr=PRISM.get((c,pt),0); op_tot+=o; pp_tot+=pr
        cell=ws.cell(i,j); cell.alignment=ctr; cell.border=BORD
        if o==0 and pr==0: cell.value=""; cell.fill=GREY
        else:
            cell.value=f"{pr} / {o}"
            cell.fill=RED if pr>o else PINK
    e=ws.cell(i,len(COUNTIES)+2,f"{pp_tot} / {op_tot}"); e.font=bold; e.fill=TOT; e.alignment=ctr; e.border=BORD
ti_=r0+len(PT)+1
ws.cell(ti_,1,"Total").font=bold; ws.cell(ti_,1).fill=TOT; ws.cell(ti_,1).border=BORD
for j,c in enumerate(COUNTIES,2):
    o=sum(OUR.get((pt,c),0) for pt in PT); pr=sum(PRISM.get((c,pt),0) for pt in PT)
    e=ws.cell(ti_,j,f"{pr} / {o}"); e.font=bold; e.fill=TOT; e.alignment=ctr; e.border=BORD
g=ws.cell(ti_,len(COUNTIES)+2,f"{sum(PRISM.values())} / {len(rows)}"); g.font=bold; g.fill=TOT; g.alignment=ctr; g.border=BORD
ws.column_dimensions["A"].width=26
for j in range(2,len(COUNTIES)+3): ws.column_dimensions[get_column_letter(j)].width=11
ws.freeze_panes="B5"

# Sheet 2: discrepancies to resolve
ws2=wb.create_sheet("Resolve (Prism > ours)")
ws2.append(["Provider Type","County","Prism","Our roster","Gap"]);
for c in ws2[1]: c.font=bold; c.fill=HDR; c.border=BORD
for pt in PT:
    for c in COUNTIES:
        o=OUR.get((pt,c),0); pr=PRISM.get((c,pt),0)
        if pr>o:
            ws2.append([pt,c,pr,o,pr-o])
for col,w in zip("ABCDE",[26,14,8,12,8]): ws2.column_dimensions[col].width=w
for row in ws2.iter_rows(min_row=2):
    for cell in row: cell.border=BORD
    row[-1].fill=RED; row[-1].font=bold

# Sheet 3: our specialty x county (full) for reference
ws3=wb.create_sheet("Specialty x County (ours)")
TARGET=["Allergy","Behavioral","Cardiology","Endocrinology","ENT","Gastroenterology","Hospitalist","IMFM",
        "Infectious Disease","OBGYN","Oncology/Radiation Oncology","Ophthalmology","Orthopedics","Pain Management",
        "Pediatrics","Physical Medicine and Rehab","Podiatry","Radiology","Rheumatology","Surgery","Urgent Care",
        "Urology","Other / no target"]
ws3.append(["Specialty (your taxonomy) \\ County"]+COUNTIES+["Total"])
for c in ws3[1]: c.font=bold; c.fill=HDR; c.border=BORD; c.alignment=ctr
for sp in TARGET:
    rowv=[sp]; tot=0
    for c in COUNTIES:
        v=OUR_SPEC.get((sp,c),0); rowv.append(v); tot+=v
    rowv.append(tot); ws3.append(rowv)
ws3.column_dimensions["A"].width=28
for j in range(2,len(COUNTIES)+3): ws3.column_dimensions[get_column_letter(j)].width=10
for row in ws3.iter_rows(min_row=2):
    for cell in row[1:]:
        cell.alignment=ctr; cell.border=BORD
        if cell.value==0: cell.fill=GREY
    row[0].font=bold; row[0].border=BORD
ws3.freeze_panes="B2"

wb.save(OUT)
print("Saved",OUT)
print("Prism counties:",prism_counties)
print("Counties not in Prism (ours only):",[c for c in COUNTIES if c not in prism_counties])
