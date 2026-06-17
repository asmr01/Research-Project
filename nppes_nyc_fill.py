# nppes_nyc_fill.py - find providers at specific Optum NYC addresses (urgent care /
# radiology / offices the directory scrape missed) in the FULL NPPES file.
# Put next to your npidata_pfile_*.csv and run:  python nppes_nyc_fill.py
import csv, glob, sys, re
csv.field_size_limit(10_000_000)

# Optum NYC sites Prism shows but our directory missed (street -> county, expected specialties)
TARGETS = {
 "1049 MORRIS PARK AVE":      ("Bronx",     "Urgent Care"),
 "3802 14 AVE":               ("Kings",     "Radiology"),
 "7601 4 AVE":                ("Kings",     "Radiology"),
 "1601 3 AVE":                ("New York",  "Urgent Care / PM&R"),
 "345 E 37 ST":               ("New York",  "Cardiology / GI"),
 "16450 CROSS BAY BLVD":      ("Queens",    "Urgent Care / IMFM"),
 "133 E 58 ST":               ("New York",  "Ophthalmology (partial)"),
 "317 E 34 ST":               ("New York",  "PM&R / Podiatry (partial)"),
}

def norm(s):
    if not s: return ""
    s=s.upper().split(",")[0].replace("."," ").replace("-","")
    s=re.sub(r'\b(STE|SUITE|FL|FLR|FLOOR|RM|ROOM|APT|UNIT|#|BLDG|DEPT|LL)\b.*','',s)
    s=re.sub(r'(\d+)(ST|ND|RD|TH)\b',r'\1',s)
    for a,b in [(" STREET"," ST"),(" AVENUE"," AVE"),(" ROAD"," RD"),(" BOULEVARD"," BLVD"),
                (" DRIVE"," DR"),(" PLACE"," PL"),(" TURNPIKE"," TPKE"),(" PARKWAY"," PKWY"),(" HIGHWAY"," HWY")]:
        s=s.replace(a,b)
    return " ".join(s.split())

def main():
    files=[f for f in (sys.argv[1:] or glob.glob("npidata_pfile_*.csv")) if "fileheader" not in f]
    if not files: print("ERROR: no npidata_pfile_*.csv found next to this script."); return
    path=files[0]; print(f"Reading {path} ...")
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rd=csv.reader(fh); header=next(rd); idx={n:i for i,n in enumerate(header)}
        NPI=idx["NPI"]; ENT=idx["Entity Type Code"]; LAST=idx["Provider Last Name (Legal Name)"]
        FIRST=idx["Provider First Name"]; CRED=idx["Provider Credential Text"]
        A1=idx["Provider First Line Business Practice Location Address"]
        A2=idx["Provider Second Line Business Practice Location Address"]
        CITY=idx["Provider Business Practice Location Address City Name"]
        ST=idx["Provider Business Practice Location Address State Name"]
        ZIP=idx["Provider Business Practice Location Address Postal Code"]
        ENUM=idx["Provider Enumeration Date"]; SEX=idx["Provider Sex Code"]
        tax=[idx[f"Healthcare Provider Taxonomy Code_{k}"] for k in range(1,16)]
        sw =[idx[f"Healthcare Provider Primary Taxonomy Switch_{k}"] for k in range(1,16)]
        out=[]; n=0
        for r in rd:
            n+=1
            if n%1000000==0: print(f"  ...{n:,} rows")
            if r[ST].strip()!="NY": continue
            key=norm((r[A1]+" "+r[A2]))
            tgt=None
            for t in TARGETS:
                if key==t or t in key or key in t: tgt=t; break
            if not tgt: continue
            prim=""
            for ci,si in zip(tax,sw):
                if r[ci].strip():
                    if r[si].strip().upper()=="Y": prim=r[ci].strip(); break
                    prim=prim or r[ci].strip()
            out.append([r[NPI],r[FIRST].title(),r[LAST].title(),r[CRED].strip(),
                        ("Org" if r[ENT].strip()=="2" else "Indiv"),prim,r[ENUM],r[SEX].strip(),
                        f"{r[A1]} {r[A2]}".strip(),r[CITY].title(),r[ZIP][:5],
                        tgt,TARGETS[tgt][0],TARGETS[tgt][1]])
        print(f"Scanned {n:,} rows; found {len(out)} providers at the {len(TARGETS)} target addresses.")
    with open("optum_nyc_fill.csv","w",newline="",encoding="utf-8-sig") as fh:
        w=csv.writer(fh)
        w.writerow(["npi","first_name","last_name","credential","entity","primary_taxonomy",
                    "enumeration_date","sex","address","city","zip","matched_address","county","expected_specialty"])
        w.writerows(out)
    print("DONE -> optum_nyc_fill.csv  (upload this)")

main()
