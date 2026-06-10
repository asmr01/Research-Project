#!/usr/bin/env python3
"""Scrape Optum's NY find-care directory (authoritative provider roster).

Hits the public provider-search API that powers optum.com find-care:
  https://api.uhg.com/.../ups-provider-search-api/3.0.0/
scoped to Optum New York (cdo_ids 13599/13600/13601). No auth/cookies needed.

Each query returns up to ~100 results, so we sweep a broad set of SPECIALTY and
LOCATION query terms and de-duplicate every provider by NPI. Writes
optum_directory_ny.csv. Polite rate-limiting between requests.

Usage:  python scrape_optum_ny.py
"""
import csv, json, time, sys, urllib.parse, urllib.request

# api.uhg.com is behind bot protection that checks the TLS/HTTP-2 fingerprint, so a
# plain urllib request gets 401. curl_cffi impersonates Chrome (TLS+HTTP2) and works.
#   pip install curl_cffi
try:
    from curl_cffi import requests as creq
    _HAVE_CURL = True
except Exception:
    _HAVE_CURL = False

API = "https://api.uhg.com/api/cross-domain/producer/ups-provider-search-api/3.0.0/"
CDO_IDS = ["13599", "13600", "13601"]   # Optum New York
LIMIT = 500                              # try large; API may cap ~100 (union of terms covers the rest)
SLEEP = 0.5                              # seconds between requests (be a good citizen)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.optum.com",
    "referer": "https://www.optum.com/",
    "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
}

# Broad sweep of specialty-style query terms (fuzzy matched; noise is fine, we dedupe by NPI)
SPECIALTY_TERMS = [
 "primary care","family medicine","internal medicine","pediatrics","geriatric medicine",
 "nurse practitioner","physician assistant","hospitalist","urgent care",
 "cardiology","cardiovascular disease","interventional cardiology","electrophysiology",
 "nuclear cardiology","pediatric cardiology","heart failure",
 "oncology","hematology","hematology oncology","medical oncology","radiation oncology",
 "surgical oncology","gynecologic oncology",
 "gastroenterology","endocrinology","nephrology","rheumatology","pulmonary","pulmonology",
 "infectious disease","allergy immunology","sleep medicine","dermatology","neurology",
 "physical medicine rehabilitation","pain management","anesthesiology",
 "obstetrics gynecology","maternal fetal medicine","midwife","urology",
 "orthopaedic surgery","orthopedics","sports medicine","podiatry","neurosurgery",
 "general surgery","vascular surgery","plastic surgery","colorectal surgery",
 "otolaryphngology","otolaryngology","ent","ophthalmology","optometry","audiology",
 "radiology","interventional radiology","pathology","emergency medicine",
 "psychiatry","psychology","behavioral health","social work","counselor",
 "physical therapy","occupational therapy","speech language pathology",
 "dietitian","nutrition","pharmacy","pharmacist","chiropractic","acupuncture",
 "dentist","dental","oral surgery","orthodontics","periodontics","prosthodontics",
 "wound care","palliative","registered nurse","clinical nurse specialist",
]

# Optum NY geography (counties + boroughs + every Optum town we know of) - text matched
LOCATION_TERMS = [
 "Nassau","Suffolk","Westchester","Putnam","Dutchess","Orange","Rockland","Ulster",
 "Sullivan","Bronx","Brooklyn","Queens","Manhattan","Staten Island","New York",
 "Mount Kisco","Middletown","Monroe","Newburgh","Poughkeepsie","Fishkill","Rhinebeck",
 "New Windsor","Rock Hill","Warwick","Goshen","West Nyack","Pomona","Orangeburg","New City",
 "Airmont","Chestnut Ridge","Cortlandt Manor","Jefferson Valley","Katonah","Brewster",
 "Carmel","Yonkers","Rye","Dobbs Ferry","White Plains","Thornwood","Yorktown Heights",
 "Bethpage","Farmingdale","Garden City","Garden City Park","Jericho","New Hyde Park",
 "Lake Success","Rockville Centre","Syosset","Smithtown","Bay Shore","Riverhead","Levittown",
 "Lawrence","Lynbrook","Oceanside","East Rockaway","Wheatley Heights","Woodbury","Hicksville",
 "Huntington","Valley Stream","Astoria","Flushing","Long Island City","Maspeth","Rego Park",
 "Forest Hills","Howard Beach","New Paltz","Albany",
]


def fetch(term):
    params = [("query", term), ("sources", "mongodb_query")]
    params += [("cdo_ids", c) for c in CDO_IDS]
    params += [("radius", "100"), ("limit", str(LIMIT)), ("entity_type", "p"),
               ("partner", "cdo_hybrid"), ("distance", "100"),
               ("with_filters", "true"), ("edit_distance", "1")]
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            if _HAVE_CURL:
                r = creq.get(url, headers=HEADERS, impersonate="chrome", timeout=40)
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                return r.json()
            else:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=40) as resp:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if attempt == 3:
                print(f"   ! failed '{term}': {exc}", file=sys.stderr); return None
            time.sleep(2 * (attempt + 1))
    return None


def providers_from(body):
    try:
        return body["mongodb_query"]["data"][0]["hybrid_response"] or []
    except Exception:
        return []


def langs(v):
    if isinstance(v, list):
        out = []
        for x in v:
            out.append(x.get("name") if isinstance(x, dict) else str(x))
        return "; ".join(s for s in out if s)
    return ""


def row_of(p, found_via):
    locs = p.get("locations") or []
    loc0 = locs[0] if locs else {}
    return {
        "npi": str(p.get("npi") or p.get("generated_key") or ""),
        "display_name": p.get("display_name", ""),
        "first_name": p.get("first_name", ""),
        "middle_name": p.get("middle_name", "") or "",
        "last_name": p.get("last_name", ""),
        "gender": p.get("gender", "") or "",
        "specialty": p.get("specialty", "") or "",
        "accepting_new_patients": p.get("accepting_new_patients", "") or "",
        "employed_or_contract": p.get("primary_employed_or_contract_type", "") or "",
        "average_rating": round(p["average_rating"], 2) if isinstance(p.get("average_rating"), (int, float)) else "",
        "review_count": p.get("non_empty_review_count", "") or "",
        "languages": langs(p.get("languages")),
        "phone": p.get("display_phone", "") or "",
        "fax": p.get("display_fax", "") or "",
        "address": p.get("display_address", "") or loc0.get("display_address", ""),
        "zip": p.get("zip_code", "") or loc0.get("zip_code", ""),
        "cdo": p.get("cdo", "") or "",
        "num_locations": len(locs) if locs else 1,
        "primary_location_name": loc0.get("location_name", ""),
        "medicare_advantage": p.get("medicare_advantage_flag", "") or "",
        "website_url": p.get("website_url", "") or "",
        "schedule_url": p.get("schedule_appointment_url", "") or "",
        "found_via": found_via,
    }


def main():
    if _HAVE_CURL:
        print("Using curl_cffi (Chrome impersonation).")
    else:
        print("WARNING: curl_cffi not installed -> requests will likely 401.\n"
              "Install it first:  pip install curl_cffi\n")
    seen = {}
    capped = []
    terms = [("spec", t) for t in SPECIALTY_TERMS] + [("loc", t) for t in LOCATION_TERMS]
    for i, (kind, term) in enumerate(terms, 1):
        body = fetch(term)
        ps = providers_from(body) if body else []
        new = 0
        for p in ps:
            npi = str(p.get("npi") or p.get("generated_key") or "")
            if npi and npi not in seen:
                seen[npi] = row_of(p, f"{kind}:{term}")
                new += 1
        flag = "  <-- CAPPED (slice further)" if len(ps) >= LIMIT or len(ps) == 100 else ""
        print(f"[{i:>3}/{len(terms)}] {kind}:{term:<28} returned={len(ps):<4} new={new:<4} total={len(seen)}{flag}")
        if len(ps) >= LIMIT or len(ps) == 100:
            capped.append(term)
        time.sleep(SLEEP)

    cols = list(next(iter(seen.values())).keys()) if seen else []
    with open("optum_directory_ny.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in sorted(seen.values(), key=lambda x: (x["specialty"], x["last_name"], x["first_name"])):
            w.writerow(r)
    print(f"\nDONE -> optum_directory_ny.csv  ({len(seen)} unique providers)")
    if capped:
        print(f"NOTE: {len(capped)} queries hit the result cap (may be incomplete): {', '.join(capped)}")


if __name__ == "__main__":
    main()
