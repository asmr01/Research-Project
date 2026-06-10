#!/usr/bin/env python3
"""Build a table of Optum-owned practices and their providers in New York.

Data source: NPPES NPI Registry public API (https://npiregistry.cms.hhs.gov/api/).
This is the free, authoritative CMS registry of US health care providers.

REQUIREMENT: The host `npiregistry.cms.hhs.gov` must be reachable. In Claude Code
on the web, add it to the environment's network allowlist (see README).

What it does
------------
1. Pulls every Optum-OWNED organization location in NY (NPPES "Type 2" records)
   whose legal/other name matches one of the known Optum NY brands.
2. Pulls individual providers (NPPES "Type 1") and JOINS them to those locations
   by matching their NPPES practice address (street + ZIP) to a location.
   NOTE: NPPES individual records do not store an employer, so this join is an
   address-based inference. It captures clinicians who registered an Optum clinic
   as their practice address. It is good coverage but not guaranteed exhaustive.
3. Writes an Excel workbook with three sheets: Locations, Providers, Joined.

Usage
-----
    python3 optum_ny_providers.py --out optum_ny_providers.xlsx
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

import urllib.parse
import urllib.request

# Allow very large CSV fields (NPPES rows are wide).
csv.field_size_limit(10_000_000)

API = "https://npiregistry.cms.hhs.gov/api/"
API_VERSION = "2.1"
PAGE = 200            # NPPES max results per request
MAX_SKIP = 1000       # NPPES caps skip at 1000 (=> 1200 records max per query string)

# Known Optum-owned medical groups operating in New York. NPPES search is a
# prefix/wildcard match on the organization name field, so we query each brand.
OPTUM_NY_BRANDS = [
    "Optum Medical Care",
    "Optum",                 # broad catch (filtered later by NY + brand heuristics)
    "CareMount",             # former CareMount Medical
    "ProHEALTH",             # former ProHEALTH New York
    "Riverside Medical",     # former Riverside Medical Group
    "Crystal Run",           # Crystal Run Healthcare
]

# Names that confirm Optum ownership when filtering the broad "Optum" sweep.
OPTUM_NAME_HINTS = (
    "optum", "caremount", "prohealth", "riverside medical", "crystal run",
)


# --- NPPES full-file (npidata_pfile) column indices (0-based) ---
COL_NPI = 0
COL_ENTITY = 1          # "1" individual, "2" organization
COL_ORG_NAME = 4
COL_LAST = 5
COL_FIRST = 6
COL_CRED = 10
COL_ADDR1 = 28
COL_ADDR2 = 29
COL_CITY = 30
COL_STATE = 31
COL_ZIP = 32
COL_PHONE = 34
# Taxonomy: 15 groups of 4 cols starting at 47; primary switch 3 cols after code.
TAX_FIRST = 47
TAX_GROUPS = 15


def _primary_taxonomy(row: list[str]) -> str:
    """Return the primary taxonomy code from an npidata row (fallback: first code)."""
    first = ""
    for k in range(TAX_GROUPS):
        code_i = TAX_FIRST + 4 * k
        sw_i = code_i + 3
        if code_i >= len(row):
            break
        code = row[code_i].strip()
        if not code:
            continue
        if not first:
            first = code
        if sw_i < len(row) and row[sw_i].strip().upper() == "Y":
            return code
    return first


def load_taxonomy_map(path: str | None) -> dict[str, str]:
    """Optional NUCC taxonomy crosswalk (Code -> 'Classification - Specialization')."""
    if not path or not os.path.exists(path):
        return {}
    out: dict[str, str] = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            code = (r.get("Code") or "").strip()
            if not code:
                continue
            cls = (r.get("Classification") or "").strip()
            spec = (r.get("Specialization") or "").strip()
            out[code] = f"{cls} - {spec}" if spec else cls
    return out


def load_from_file(npidata_path: str, taxonomy_path: str | None = None
                   ) -> tuple[dict[str, "Location"], list[dict[str, Any]]]:
    """Parse a full NPPES npidata_pfile CSV offline.

    Streams the file once: collects NY Optum-owned org locations (entity type 2)
    and NY individuals (entity type 1), then joins individuals to locations by
    practice street + ZIP.
    """
    taxmap = load_taxonomy_map(taxonomy_path)
    locs: dict[str, Location] = {}
    individuals: list[dict[str, Any]] = []

    with open(npidata_path, newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.reader(fh)
        next(reader, None)  # header
        for row in reader:
            if len(row) <= COL_STATE or row[COL_STATE].strip() != "NY":
                continue
            entity = row[COL_ENTITY].strip()
            addr = {
                "address_1": row[COL_ADDR1], "address_2": row[COL_ADDR2],
                "postal_code": row[COL_ZIP],
            }
            street, zip5 = _norm_street(addr), _zip5(addr)
            if entity == "2":
                name = row[COL_ORG_NAME].strip()
                if not any(h in name.lower() for h in OPTUM_NAME_HINTS):
                    continue
                npi = row[COL_NPI].strip()
                locs[npi] = Location(
                    npi=npi, name=name, brand=_brand_of(name), street=street,
                    city=row[COL_CITY].title(), state="NY", zip5=zip5,
                    phone=row[COL_PHONE].strip(),
                )
            elif entity == "1":
                code = _primary_taxonomy(row)
                individuals.append({
                    "provider_npi": row[COL_NPI].strip(),
                    "first_name": row[COL_FIRST].title(),
                    "last_name": row[COL_LAST].title(),
                    "credential": row[COL_CRED].strip(),
                    "specialty": taxmap.get(code, code),
                    "_key": (street, zip5),
                })

    by_key = {loc.key: loc for loc in locs.values()}
    joined: list[dict[str, Any]] = []
    for ind in individuals:
        loc = by_key.get(ind.pop("_key"))
        if not loc:
            continue
        ind.update({
            "location_name": loc.name, "brand": loc.brand, "location_npi": loc.npi,
            "street": loc.street, "city": loc.city, "state": loc.state,
            "zip": loc.zip5, "phone": loc.phone,
        })
        joined.append(ind)
        loc.providers.append(ind)
    print(f"  -> {len(locs)} Optum NY locations, {len(joined)} providers matched")
    return locs, joined


def _brand_of(name: str) -> str:
    n = name.lower()
    if "caremount" in n:
        return "CareMount (Optum)"
    if "prohealth" in n:
        return "ProHEALTH (Optum)"
    if "crystal run" in n:
        return "Crystal Run Healthcare (Optum)"
    if "riverside medical" in n:
        return "Riverside Medical Group (Optum)"
    return "Optum Medical Care"


def _get(params: dict[str, Any], retries: int = 4) -> dict[str, Any]:
    """GET the NPPES API with simple exponential-backoff retry."""
    url = API + "?" + urllib.parse.urlencode(params)
    delay = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                import json
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - network errors of many kinds
            if attempt == retries - 1:
                raise
            print(f"  retry {attempt+1} after error: {exc}", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
    return {}


def fetch_all(enumeration_type: str, **filters: Any) -> list[dict[str, Any]]:
    """Page through every result for a given query (capped at MAX_SKIP by NPPES)."""
    out: list[dict[str, Any]] = []
    skip = 0
    while skip <= MAX_SKIP:
        params = {
            "version": API_VERSION,
            "enumeration_type": enumeration_type,
            "limit": PAGE,
            "skip": skip,
            **filters,
        }
        data = _get(params)
        results = data.get("results") or []
        out.extend(results)
        if len(results) < PAGE:
            break
        skip += PAGE
    return out


def _practice_address(rec: dict[str, Any]) -> dict[str, Any]:
    """Return the LOCATION practice address dict for an NPPES record."""
    for addr in rec.get("addresses", []):
        if addr.get("address_purpose") == "LOCATION":
            return addr
    return rec.get("addresses", [{}])[0] if rec.get("addresses") else {}


def _norm_street(addr: dict[str, Any]) -> str:
    s = " ".join(
        str(addr.get(k, "")).strip()
        for k in ("address_1", "address_2")
    ).upper()
    return " ".join(s.split())


def _zip5(addr: dict[str, Any]) -> str:
    return str(addr.get("postal_code", ""))[:5]


@dataclass
class Location:
    npi: str
    name: str
    brand: str
    street: str
    city: str
    state: str
    zip5: str
    phone: str
    providers: list[dict[str, Any]] = field(default_factory=list)

    @property
    def key(self) -> tuple[str, str]:
        return (self.street, self.zip5)


def collect_locations() -> dict[str, Location]:
    """Fetch all Optum-owned org (Type 2) locations in NY, de-duplicated by NPI."""
    locs: dict[str, Location] = {}
    for brand in OPTUM_NY_BRANDS:
        print(f"Fetching org locations for brand: {brand!r}")
        recs = fetch_all(
            "NPI-2",
            state="NY",
            organization_name=brand + "*",
        )
        for rec in recs:
            basic = rec.get("basic", {})
            name = (basic.get("organization_name") or "").strip()
            if not any(h in name.lower() for h in OPTUM_NAME_HINTS):
                continue
            addr = _practice_address(rec)
            if addr.get("state") != "NY":
                continue
            npi = str(rec.get("number"))
            locs[npi] = Location(
                npi=npi,
                name=name,
                brand=brand,
                street=_norm_street(addr),
                city=(addr.get("city") or "").title(),
                state=addr.get("state", ""),
                zip5=_zip5(addr),
                phone=addr.get("telephone_number", ""),
            )
    print(f"  -> {len(locs)} unique Optum-owned NY locations")
    return locs


def collect_providers(locs: dict[str, Location]) -> list[dict[str, Any]]:
    """Fetch individual providers (Type 1) by the ZIP codes of Optum locations and
    join them to a location by street+ZIP match."""
    by_key = {loc.key: loc for loc in locs.values()}
    zips = sorted({loc.zip5 for loc in locs.values() if loc.zip5})
    joined: list[dict[str, Any]] = []
    seen: set[str] = set()
    for z in zips:
        recs = fetch_all("NPI-1", state="NY", postal_code=z + "*")
        for rec in recs:
            addr = _practice_address(rec)
            key = (_norm_street(addr), _zip5(addr))
            loc = by_key.get(key)
            if not loc:
                continue
            npi = str(rec.get("number"))
            if npi in seen:
                continue
            seen.add(npi)
            basic = rec.get("basic", {})
            taxonomies = rec.get("taxonomies", [])
            primary_tax = next(
                (t for t in taxonomies if t.get("primary")), taxonomies[0] if taxonomies else {}
            )
            row = {
                "provider_npi": npi,
                "first_name": basic.get("first_name", ""),
                "last_name": basic.get("last_name", ""),
                "credential": basic.get("credential", ""),
                "specialty": primary_tax.get("desc", ""),
                "location_name": loc.name,
                "brand": loc.brand,
                "location_npi": loc.npi,
                "street": loc.street,
                "city": loc.city,
                "state": loc.state,
                "zip": loc.zip5,
                "phone": loc.phone,
            }
            joined.append(row)
            loc.providers.append(row)
    print(f"  -> {len(joined)} providers matched to Optum locations")
    return joined


def write_excel(out_path: str, locs: dict[str, Location], providers: list[dict]) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from openpyxl.utils import get_column_letter

    wb = Workbook()

    # Sheet 1: Locations
    ws = wb.active
    ws.title = "Locations"
    loc_cols = ["location_npi", "name", "brand", "street", "city", "state", "zip",
                "phone", "provider_count"]
    ws.append(loc_cols)
    for loc in sorted(locs.values(), key=lambda l: (l.brand, l.city, l.name)):
        ws.append([loc.npi, loc.name, loc.brand, loc.street, loc.city, loc.state,
                   loc.zip5, loc.phone, len(loc.providers)])

    # Sheet 2: Providers (joined)
    ws2 = wb.create_sheet("Providers")
    prov_cols = ["provider_npi", "first_name", "last_name", "credential", "specialty",
                 "location_name", "brand", "location_npi", "street", "city", "state",
                 "zip", "phone"]
    ws2.append(prov_cols)
    for row in sorted(providers, key=lambda r: (r["brand"], r["last_name"], r["first_name"])):
        ws2.append([row[c] for c in prov_cols])

    # Formatting: bold header + autosize-ish
    for sheet in (ws, ws2):
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        sheet.freeze_panes = "A2"
        for i, _ in enumerate(sheet[1], start=1):
            width = max(
                (len(str(sheet.cell(row=r, column=i).value or "")) for r in range(1, min(sheet.max_row, 200) + 1)),
                default=10,
            )
            sheet.column_dimensions[get_column_letter(i)].width = min(max(width + 2, 12), 50)

    wb.save(out_path)
    print(f"Wrote {out_path}: {len(locs)} locations, {len(providers)} providers")


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="optum_ny_providers.xlsx", help="output .xlsx path")
    ap.add_argument("--skip-providers", action="store_true",
                    help="only build the locations sheet (faster; API mode)")
    ap.add_argument("--from-file", metavar="NPIDATA_CSV",
                    help="parse a full NPPES npidata_pfile CSV offline (no network)")
    ap.add_argument("--taxonomy-file", metavar="NUCC_CSV",
                    help="optional NUCC taxonomy crosswalk to map specialty codes to names")
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.from_file:
        locs, providers = load_from_file(args.from_file, args.taxonomy_file)
    else:
        locs = collect_locations()
        providers = [] if args.skip_providers else collect_providers(locs)

    if not locs:
        hint = ("Is this the FULL monthly npidata file (not the weekly)?"
                if args.from_file else "Is the NPPES host allowlisted?")
        print(f"No Optum locations found. {hint}", file=sys.stderr)
        return 1
    write_excel(args.out, locs, providers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
