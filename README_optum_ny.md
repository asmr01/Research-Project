# Optum-owned Providers in New York — data builder

Builds an Excel table of **Optum-owned medical practices in New York** and the
**individual providers joined to each location**, from the public
[NPPES NPI Registry API](https://npiregistry.cms.hhs.gov/api/) (CMS).

## Prerequisites

```bash
pip install openpyxl
```

### Network allowlist (Claude Code on the web)

The NPPES host must be reachable. By default this environment blocks it
(`Host not in allowlist`). To enable:

1. Open the environment settings for this repo's web session.
2. **Network access → custom allowlist**, add: `npiregistry.cms.hhs.gov`
3. Save and start a **fresh session** (containers are ephemeral; the new policy
   applies to a new container).

Docs: https://code.claude.com/docs/en/claude-code-on-the-web

## Run

```bash
python3 optum_ny_providers.py --out optum_ny_providers.xlsx
# locations only (faster):
python3 optum_ny_providers.py --skip-providers
```

## Output

An `.xlsx` workbook with two sheets:

| Sheet      | Contents |
|------------|----------|
| `Locations` | Each Optum-owned org location in NY: NPI, name, brand, address, phone, provider count |
| `Providers` | Each individual provider joined to their Optum location: name, NPI, specialty, credential, location |

## Optum-owned brands covered

`Optum Medical Care` (= former **CareMount Medical**, **ProHEALTH NY**,
**Riverside Medical Group**) and **Crystal Run Healthcare**. Edit
`OPTUM_NY_BRANDS` in the script to add/remove brands.

## Method & caveats

- **Locations** come from NPPES "Type 2" (organizational) records matched by
  organization name + `state=NY`. This is reliable and authoritative.
- **Provider↔location join** is **address-based**: NPPES "Type 1" (individual)
  records do not store an employer, so providers are matched to a location by
  their registered practice street + ZIP. This captures clinicians who listed an
  Optum clinic as their practice address — good coverage, but **not guaranteed
  exhaustive**. The fully authoritative provider↔location mapping lives in
  Optum's own directory (optum.com), which blocks automated access.
- NPPES caps pagination at 1,200 records per query string; the script pages per
  brand and per ZIP to stay within that limit.
