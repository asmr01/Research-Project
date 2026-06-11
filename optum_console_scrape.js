/* Optum NY directory scraper (FULL roster). RUN IN THE BROWSER CONSOLE
   on an optum.com find-care page. Paste this whole script, press Enter,
   then paste your Bearer token (or the whole cURL) into the popup.
   ~2-3 min -> optum_directory_ny.csv downloads. */
(async () => {
  let TOKEN = (prompt("Paste the Bearer token (eyJ...). Pasting the whole cURL is fine — I'll extract it.") || "");
  // pull eyJ....  out of whatever was pasted, then keep only valid JWT chars (drops spaces/newlines/^/quotes)
  let m = TOKEN.match(/eyJ[A-Za-z0-9._-]+/g);
  TOKEN = m ? m.sort((a, b) => b.length - a.length)[0] : TOKEN.replace(/[^A-Za-z0-9._-]/g, "");
  if (!TOKEN.startsWith("eyJ") || (TOKEN.split(".").length !== 3)) { console.log("Could not find a valid token. Copy the value after 'authorization: Bearer ' (starts with eyJ, has two dots) and try again."); return; }
  console.log("token ok:", TOKEN.slice(0, 16) + "... (" + TOKEN.length + " chars)");
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
    p.append("radius", "25"); p.append("limit", "100"); p.append("entity_type", "p");
    p.append("partner", "cdo_hybrid"); p.append("distance", "25");
    p.append("with_filters", "true"); p.append("edit_distance", "1");   // re_new_patient removed = full roster
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
      if (res.status === 401) { auth401++; console.log(`[${i}/${terms.length}] ${kind}:${term} -> 401 (token expired?)`); if (auth401 >= 3) { console.log("Multiple 401s — token expired. Get a fresh token, replace it on the TOKEN line, paste again."); break; } await sleep(400); continue; }
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
  if (!rows.length) { console.log("No providers collected (check token)."); return; }
  const cols = Object.keys(rows[0]);
  const esc = v => { v = (v == null) ? "" : String(v); return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
  const csv = [cols.join(",")].concat(rows.map(r => cols.map(c => esc(r[c])).join(","))).join("\r\n");
  const blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "optum_directory_ny.csv";
  document.body.appendChild(a); a.click(); a.remove();
  console.log(`DONE: ${seen.size} unique providers -> optum_directory_ny.csv downloaded`);
  if (capped.length) console.log(`CAPPED terms: ${capped.join(", ")}`);
})();
