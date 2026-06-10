# build_optum.py - extract Optum-owned NY practices + providers from NPPES full file
# v2: building-level address matching (ignores suite/floor) + match_confidence flag
import csv, glob, sys
csv.field_size_limit(10_000_000)

# NPPES npidata_pfile column positions (0-based)
NPI,ENTITY,ORG,LAST,FIRST,CRED = 0,1,4,5,6,10
A1,A2,CITY,STATE,ZIP,PHONE = 28,29,30,31,32,34
TAX_FIRST,TAX_GROUPS = 47,15
HINTS = ("optum","caremount","prohealth","crystal run","riverside medical")

# tokens that begin a secondary unit designator (suite/floor/etc.) - everything from
# the first one onward is dropped to get the "building" address used for matching.
STOP = {"STE","SUITE","UNIT","FL","FLR","FLOOR","RM","ROOM","APT","BLDG","BUILDING",
        "DEPT","DEPARTMENT","LEVEL","LL","SPC","SPACE","#"}

def brand(n):
    n=n.lower()
    if "caremount" in n: return "CareMount (Optum)"
    if "prohealth" in n: return "ProHEALTH (Optum)"
    if "crystal run" in n: return "Crystal Run Healthcare (Optum)"
    if "riverside medical" in n: return "Riverside Medical Group (Optum)"
    return "Optum Medical Care"

def full_street(r): return " ".join((r[A1]+" "+r[A2]).upper().split())
def zip5(r): return r[ZIP][:5]

def base_street(s):
    out=[]
    for t in s.split():
        if t in STOP or t.startswith("#"): break
        out.append(t)
    return " ".join(out)

def primary_tax(r):
    first=""
    for k in range(TAX_GROUPS):
        c=TAX_FIRST+4*k
        if c>=len(r): break
        if r[c].strip():
            if not first: first=r[c].strip()
            if c+3<len(r) and r[c+3].strip().upper()=="Y": return r[c].strip()
    return first

def main():
    files=[f for f in (sys.argv[1:] or glob.glob("npidata_pfile_*.csv")) if "fileheader" not in f]
    if not files:
        print("ERROR: no npidata_pfile_*.csv found next to this script."); return
    path=files[0]; print(f"Reading {path} ...")
    locs={}; inds=[]; n=0
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        rd=csv.reader(fh); next(rd,None)
        for r in rd:
            n+=1
            if n % 1000000 == 0: print(f"  ...{n:,} rows scanned")
            if len(r)<=STATE or r[STATE].strip()!="NY": continue
            fs=full_street(r); z=zip5(r)
            if r[ENTITY].strip()=="2":
                nm=r[ORG].strip()
                if any(h in nm.lower() for h in HINTS):
                    locs[r[NPI]]={"npi":r[NPI],"name":nm,"brand":brand(nm),"street":fs,
                        "city":r[CITY].title(),"zip":z,"phone":r[PHONE].strip(),
                        "full":(fs,z),"base":(base_street(fs),z)}
            elif r[ENTITY].strip()=="1":
                code=primary_tax(r)
                inds.append({"npi":r[NPI],"first":r[FIRST].title(),"last":r[LAST].title(),
                    "cred":r[CRED].strip(),"spec":code,"full":(fs,z),"base":(base_street(fs),z)})
    print(f"Scanned {n:,} rows. Optum NY locations: {len(locs)}")

    by_full={}; by_base={}
    for l in locs.values():
        by_full.setdefault(l["full"], l)
        # prefer a 'care' org over a facility/ASC when several share a building key
        cur=by_base.get(l["base"])
        if cur is None or l["base"]==l["full"]:  # exact-street org wins as the base representative
            by_base[l["base"]]=l

    rows=[]; counts={}; exact=build=0
    for i in inds:
        loc=by_full.get(i["full"]); conf="exact"
        if not loc:
            loc=by_base.get(i["base"]); conf="building"
        if not loc: continue
        if conf=="exact": exact+=1
        else: build+=1
        counts[loc["npi"]]=counts.get(loc["npi"],0)+1
        rows.append([i["npi"],i["first"],i["last"],i["cred"],i["spec"],conf,
            loc["name"],loc["brand"],loc["npi"],loc["street"],loc["city"],loc["zip"],loc["phone"]])
    print(f"Providers matched: {len(rows)}  (exact={exact}, building-level={build})")

    with open("optum_ny_locations.csv","w",newline="",encoding="utf-8-sig") as fh:
        w=csv.writer(fh); w.writerow(["location_npi","name","brand","street","city","zip","phone","provider_count"])
        for l in sorted(locs.values(),key=lambda x:(x["brand"],x["city"],x["name"])):
            w.writerow([l["npi"],l["name"],l["brand"],l["street"],l["city"],l["zip"],l["phone"],counts.get(l["npi"],0)])
    with open("optum_ny_providers.csv","w",newline="",encoding="utf-8-sig") as fh:
        w=csv.writer(fh); w.writerow(["provider_npi","first_name","last_name","credential","specialty",
            "match_confidence","location_name","brand","location_npi","street","city","zip","phone"])
        for row in sorted(rows,key=lambda x:(x[7],x[2],x[1])): w.writerow(row)
    print("DONE -> optum_ny_locations.csv and optum_ny_providers.csv")

main()
