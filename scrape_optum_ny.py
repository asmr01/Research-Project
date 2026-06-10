#!/usr/bin/env python3
"""Scrape Optum's NY find-care directory (authoritative provider roster).

Hits the public provider-search API behind optum.com find-care, scoped to Optum NY
(cdo_ids 13599/13600/13601). The API needs a short-lived Bearer token that the site
uses. Paste that token into a file named token.txt next to this script, then run.

GET A FRESH TOKEN (valid ~1 hour):
  1. Open an Optum find-care results page, F12 -> Network, filter: provider-search
  2. Search something so a request to api.uhg.com appears (status 200).
  3. Right-click it -> Copy -> Copy as cURL. Find the part:  authorization: Bearer eyJ....
  4. Put just the eyJ.... value (or the whole 'Bearer eyJ...') into token.txt and save.

RUN:  python scrape_optum_ny.py
Output: optum_directory_ny.csv   (upload it back)
"""
import csv, json, os, sys, time, urllib.parse, urllib.request

try:
    from curl_cffi import requests as creq
    _HAVE_CURL = True
except Exception:
    _HAVE_CURL = False

API = "https://api.uhg.com/api/cross-domain/producer/ups-provider-search-api/3.0.0/"
CDO_IDS = ["13599", "13600", "13601"]   # Optum New York
SLEEP = 0.6


def load_token():
    for name in ("token.txt", "token"):
        if os.path.exists(name):
            t = open(name, encoding="utf-8").read().strip()
            for pre in ("Bearer ", "bearer ", "authorization: ", "Authorization: "):
                t = t.replace(pre, "")
            return t.strip().strip('"').strip("'")
    return ""

TOKEN = load_token()
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer " + TOKEN,
    "origin": "https://www.optum.com",
    "referer": "https://www.optum.com/",
}
URLLIB_HEADERS = dict(HEADERS, **{
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
})

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
 "otolaryngology","ent","ophthalmology","optometry","audiology",
 "radiology","interventional radiology","pathology","emergency medicine",
 "psychiatry","psychology","behavioral health","social work","counselor",
 "physical therapy","occupational therapy","speech language pathology",
 "dietitian","nutrition","pharmacy","pharmacist","chiropractic","acupuncture",
 "dentist","dental","oral surgery","orthodontics","periodontics","prosthodontics",
 "wound care","palliative","registered nurse","clinical nurse specialist",
]
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

_session = creq.Session(impersonate="chrome") if _HAVE_CURL else None


def _url(term):
    p = [("query", term), ("sources", "mongodb_query")] + [("cdo_ids", c) for c in CDO_IDS]
    p += [("radius", "25"), ("limit", "100"), ("partner", "cdo_hybrid"), ("distance", "25"),
          ("re_new_patient", "true"), ("with_filters", "true"), ("edit_distance", "1")]
    return API + "?" + urllib.parse.urlencode(p)


def fetch(term):
    url = _url(term)
    last = None
    for attempt in range(4):
        try:
            if _HAVE_CURL:
                r = _session.get(url, headers=HEADERS, timeout=40)
                if r.status_code == 401:
                    return 401
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                return r.json()
            else:
                req = urllib.request.Request(url, headers=URLLIB_HEADERS)
                with urllib.request.urlopen(req, timeout=40) as resp:
                    return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return 401
            last = e
        except Exception as e:
            last = e
        time.sleep(2 * (attempt + 1))
    print(f"   ! failed '{term}': {last}", file=sys.stderr)
    return None


def providers_from(body):
    try:
        return body["mongodb_query"]["data"][0]["hybrid_response"] or []
    except Exception:
        return []


def langs(v):
    if isinstance(v, list):
        return "; ".join(s for s in ((x.get("name") if isinstance(x, dict) else str(x)) for x in v) if s)
    return ""


def row_of(p, found_via):
    locs = p.get("locations") or []
    loc0 = locs[0] if locs else {}
    return {
        "npi": str(p.get("npi") or p.get("generated_key") or ""),
        "display_name": p.get("display_name", ""), "first_name": p.get("first_name", ""),
        "middle_name": p.get("middle_name", "") or "", "last_name": p.get("last_name", ""),
        "gender": p.get("gender", "") or "", "specialty": p.get("specialty", "") or "",
        "accepting_new_patients": p.get("accepting_new_patients", "") or "",
        "employed_or_contract": p.get("primary_employed_or_contract_type", "") or "",
        "average_rating": round(p["average_rating"], 2) if isinstance(p.get("average_rating"), (int, float)) else "",
        "review_count": p.get("non_empty_review_count", "") or "", "languages": langs(p.get("languages")),
        "phone": p.get("display_phone", "") or "", "fax": p.get("display_fax", "") or "",
        "address": p.get("display_address", "") or loc0.get("display_address", ""),
        "zip": p.get("zip_code", "") or loc0.get("zip_code", ""), "cdo": p.get("cdo", "") or "",
        "num_locations": len(locs) if locs else 1, "primary_location_name": loc0.get("location_name", ""),
        "medicare_advantage": p.get("medicare_advantage_flag", "") or "",
        "website_url": p.get("website_url", "") or "", "schedule_url": p.get("schedule_appointment_url", "") or "",
        "found_via": found_via,
    }


def main():
    if not TOKEN:
        print("ERROR: no token. Create token.txt next to this script and paste the Bearer token\n"
              "       (the eyJ.... value from Copy as cURL). See the notes at the top of this file.")
        return 1
    print("curl_cffi:", _HAVE_CURL, "| token loaded:", TOKEN[:12] + "...")
    # probe
    probe = fetch("cardiology")
    if probe == 401:
        print("\n401 Unauthorized -> the token is missing/expired.\n"
              "Re-capture a fresh one (Copy as cURL), update token.txt, and rerun within ~1 hour.")
        return 1

    seen, capped = {}, []
    terms = [("spec", t) for t in SPECIALTY_TERMS] + [("loc", t) for t in LOCATION_TERMS]
    for i, (kind, term) in enumerate(terms, 1):
        body = fetch(term)
        if body == 401:
            print("\n401 mid-run -> token expired. Re-capture token.txt and rerun.")
            break
        ps = providers_from(body) if body else []
        new = 0
        for p in ps:
            npi = str(p.get("npi") or p.get("generated_key") or "")
            if npi and npi not in seen:
                seen[npi] = row_of(p, f"{kind}:{term}"); new += 1
        if len(ps) >= 100:
            capped.append(term)
        print(f"[{i:>3}/{len(terms)}] {kind}:{term:<28} returned={len(ps):<4} new={new:<4} total={len(seen)}"
              + ("  CAPPED" if len(ps) >= 100 else ""))
        time.sleep(SLEEP)

    if not seen:
        print("No providers collected."); return 1
    cols = list(next(iter(seen.values())).keys())
    with open("optum_directory_ny.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for r in sorted(seen.values(), key=lambda x: (x["specialty"], x["last_name"], x["first_name"])):
            w.writerow(r)
    print(f"\nDONE -> optum_directory_ny.csv  ({len(seen)} unique providers)")
    if capped:
        print(f"NOTE: {len(capped)} queries hit the 100 cap (location sweep usually backfills): {', '.join(capped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
