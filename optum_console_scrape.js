/* Optum NY directory scraper — RUN IN THE BROWSER CONSOLE (token embedded).
   1) Open: https://www.optum.com/en/care/locations/optum-new-york/find-care.html  (do any search)
   2) F12 -> Console. If paste is blocked, type:  allow pasting  then Enter.
   3) Paste ALL of this, press Enter. Wait ~2-3 min. optum_directory_ny.csv downloads.
   NOTE: token below expires ~1 hour after it was minted; if you see 401s, grab a fresh
   Bearer token (Network -> provider-search -> Copy as cURL) and replace TOKEN's value.
*/
(async () => {
  const TOKEN = "eyJraWQiOiJSdjd2VG9aeE1zNWRTMXBZbUJnRmlLak5oMGxRM3hEclY0QVd6RW9MdENIIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJhdWQiOlsiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL29wdHVtLXNyY2giLCJodHRwczovL2FwaS51aGcuY29tL2FwaS9jcm9zcy1kb21haW4vcHJvZHVjZXIvb3B0dW1yeG1vbmdvIiwiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL3Vwcy1wcm92aWRlci1yZXZpZXctYXBpIiwiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL29wdHVtLWdlbmFpIiwiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL3Vwcy1wcm92aWRlci1zZWFyY2gtYXBpIiwiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL3Vwcy1hdXRvLWNvbXBsZXRlIiwiaHR0cHM6Ly9hcGkudWhnLmNvbS9hcGkvY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL3NlYXJjaGxpdGUiLCJodHRwczovL2FwaS51aGcuY29tL2FwaS9jcm9zcy1kb21haW4vcHJvZHVjZXIvYXV0b2NvbXBsZXRldjEiXSwic3ViIjoiZGM4YTU1NjktMTU3OS00YmZhLWIzNWUtOWIwNWNlOGExMzc4IiwiYXpwIjoiZGM4YTU1NjktMTU3OS00YmZhLWIzNWUtOWIwNWNlOGExMzc4Iiwic2NvcGUiOiJjcm9zcy1kb21haW4vcHJvZHVjZXIvb3B0dW1yeG1vbmdvOmFsbCBjcm9zcy1kb21haW4vcHJvZHVjZXIvdXBzLWF1dG8tY29tcGxldGU6YWxsIGNyb3NzLWRvbWFpbi9wcm9kdWNlci9hdXRvY29tcGxldGV2MTphbGwgY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL3Vwcy1wcm92aWRlci1yZXZpZXctYXBpOmFsbCBjcm9zcy1kb21haW4vcHJvZHVjZXIvdXBzLXByb3ZpZGVyLXNlYXJjaC1hcGk6YWxsIGNyb3NzLWRvbWFpbi9wcm9kdWNlci9zZWFyY2hsaXRlOmFsbCBjcm9zcy1kb21haW4vcHJvZHVjZXIvb3B0dW0tc3JjaDphbGwgY3Jvc3MtZG9tYWluL3Byb2R1Y2VyL29wdHVtLWdlbmFpOmFsbCIsImlzcyI6Imh0dHBzOi8vaWRlbnRpdHkudWhnLmNvbSIsInR5cCI6IkJlYXJlciIsIm9pZCI6ImRjOGE1NTY5LTE1NzktNGJmYS1iMzVlLTliMDVjZThhMTM3OCIsImV4cCI6MTc4MTEzMzM2NSwiaWF0IjoxNzgxMTI5NzY1LCJqdGkiOiJjNmU5NDE1Yy1jMDlhLTRlNDYtOTQ0Yy03MGE3NGQ1Y2Q1MjEifQ.SgEP_xxhSHqVNnhwJuXlYgGDOkvQowlPvDtAPjltzgmZCdAxTK9-ZusA-r2XGOffx2r_hAhySSbVmV9tjEn9wbS7mRoOZGwOQYysCsvUtQILVuYpkzNcU0WaB2reCHmFdSTcVGRJhppi9hie_V6WNHNH2UFjDjxYwN8WrfUgeK6esGSjL8mg0bWEvi08xIsgJEzUM8iTgd2jWD1q-Z6CsGQfXAP2ngaAl_W6iBoopO5rJbCX90UCNVkCAia8ezTI01iWGREgwrjXs97Fdyaqlg5WyS6cZakd74OHWeYfBR91dN0ZkCgE9HMTl4yoL4izmNgcK4_f-aIrTuJiGxIlAA";
  const API = "https://api.uhg.com/api/cross-domain/producer/ups-provider-search-api/3.0.0/";
  const CDO = ["13599", "13600", "13601"];
  const SPEC = ["primary care","family medicine","internal medicine","pediatrics","geriatric medicine","nurse practitioner","physician assistant","hospitalist","urgent care","cardiology","cardiovascular disease","interventional cardiology","electrophysiology","nuclear cardiology","pediatric cardiology","heart failure","oncology","hematology","hematology oncology","medical oncology","radiation oncology","surgical oncology","gynecologic oncology","gastroenterology","endocrinology","nephrology","rheumatology","pulmonary","pulmonology","infectious disease","allergy immunology","sleep medicine","dermatology","neurology","physical medicine rehabilitation","pain management","anesthesiology","obstetrics gynecology","maternal fetal medicine","midwife","urology","orthopaedic surgery","orthopedics","sports medicine","podiatry","neurosurgery","general surgery","vascular surgery","plastic surgery","colorectal surgery","otolaryngology","ent","ophthalmology","optometry","audiology","radiology","interventional radiology","pathology","emergency medicine","psychiatry","psychology","behavioral health","social work","counselor","physical therapy","occupational therapy","speech language pathology","dietitian","nutrition","pharmacy","pharmacist","chiropractic","acupuncture","dentist","dental","oral surgery","orthodontics","periodontics","prosthodontics","wound care","palliative","registered nurse","clinical nurse specialist"];
  const LOC = ["Nassau","Suffolk","Westchester","Putnam","Dutchess","Orange","Rockland","Ulster","Sullivan","Bronx","Brooklyn","Queens","Manhattan","Staten Island","New York","Mount Kisco","Middletown","Monroe","Newburgh","Poughkeepsie","Fishkill","Rhinebeck","New Windsor","Rock Hill","Warwick","Goshen","West Nyack","Pomona","Orangeburg","New City","Airmont","Chestnut Ridge","Cortlandt Manor","Jefferson Valley","Katonah","Brewster","Carmel","Yonkers","Rye","Dobbs Ferry","White Plains","Thornwood","Yorktown Heights","Bethpage","Farmingdale","Garden City","Garden City Park","Jericho","New Hyde Park","Lake Success","Rockville Centre","Syosset","Smithtown","Bay Shore","Riverhead","Levittown","Lawrence","Lynbrook","Oceanside","East Rockaway","Wheatley Heights","Woodbury","Hicksville","Huntington","Valley Stream","Astoria","Flushing","Long Island City","Maspeth","Rego Park","Forest Hills","Howard Beach","New Paltz","Albany"];
  const terms = SPEC.map(t => ["spec", t]).concat(LOC.map(t => ["loc", t]));
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const seen = new Map();
  const url = term => {
    const p = new URLSearchParams();
    p.append("query", term); p.append("sources", "mongodb_query");
    CDO.forEach(c => p.append("cdo_ids", c));
    p.append("radius", "25"); p.append("limit", "100"); p.append("partner", "cdo_hybrid");
    p.append("distance", "25"); p.append("re_new_patient", "true");
    p.append("with_filters", "true"); p.append("edit_distance", "1");
    return API + "?" + p.toString();
  };
  const langs = v => Array.isArray(v) ? v.map(x => (x && x.name) ? x.name : x).filter(Boolean).join("; ") : "";
  const rowOf = (p, via) => { const L = p.locations || [], l0 = L[0] || {}; return {
    npi: String(p.npi || p.generated_key || ""), display_name: p.display_name || "", first_name: p.first_name || "",
    middle_name: p.middle_name || "", last_name: p.last_name || "", gender: p.gender || "", specialty: p.specialty || "",
    accepting_new_patients: p.accepting_new_patients || "", employed_or_contract: p.primary_employed_or_contract_type || "",
    average_rating: (typeof p.average_rating === "number") ? Math.round(p.average_rating * 100) / 100 : "",
    review_count: p.non_empty_review_count || "", languages: langs(p.languages), phone: p.display_phone || "",
    fax: p.display_fax || "", address: p.display_address || l0.display_address || "", zip: p.zip_code || l0.zip_code || "",
    cdo: p.cdo || "", num_locations: L.length || 1, primary_location_name: l0.location_name || "",
    medicare_advantage: p.medicare_advantage_flag || "", website_url: p.website_url || "",
    schedule_url: p.schedule_appointment_url || "", found_via: via }; };
  let i = 0, capped = [], auth401 = 0;
  for (const [kind, term] of terms) {
    i++;
    try {
      const res = await fetch(url(term), { headers: { "accept": "application/json, text/plain, */*", "authorization": "Bearer " + TOKEN } });
      if (res.status === 401) { auth401++; console.log(`[${i}/${terms.length}] ${kind}:${term} -> 401 (token expired?)`); if (auth401 >= 3) { console.log("Multiple 401s — token likely expired. Get a fresh Bearer token and update TOKEN."); break; } await sleep(400); continue; }
      if (!res.ok) { console.log(`[${i}/${terms.length}] ${kind}:${term} -> HTTP ${res.status}`); await sleep(400); continue; }
      const body = await res.json();
      let ps = []; try { ps = body.mongodb_query.data[0].hybrid_response || []; } catch (e) {}
      let nw = 0;
      for (const p of ps) { const npi = String(p.npi || p.generated_key || ""); if (npi && !seen.has(npi)) { seen.set(npi, rowOf(p, kind + ":" + term)); nw++; } }
      if (ps.length >= 100) capped.push(term);
      console.log(`[${i}/${terms.length}] ${kind}:${term} returned=${ps.length} new=${nw} total=${seen.size}${ps.length >= 100 ? "  CAPPED" : ""}`);
    } catch (e) { console.log(`[${i}/${terms.length}] ${kind}:${term} -> ERR ${e}`); }
    await sleep(450);
  }
  const rows = [...seen.values()];
  if (!rows.length) { console.log("No providers collected (check token / that you're on optum.com)."); return; }
  const cols = Object.keys(rows[0]);
  const esc = v => { v = (v == null) ? "" : String(v); return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
  const csv = [cols.join(",")].concat(rows.map(r => cols.map(c => esc(r[c])).join(","))).join("\r\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "optum_directory_ny.csv";
  document.body.appendChild(a); a.click(); a.remove();
  console.log(`DONE: ${seen.size} unique providers -> optum_directory_ny.csv downloaded`);
  if (capped.length) console.log(`CAPPED terms: ${capped.join(", ")}`);
})();
