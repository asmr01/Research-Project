# Components

The reusable parts every slide is assembled from. Each entry gives the anatomy, the tokens
it uses, and the rule for when to reach for it. Sizes reference
[`foundations.md`](./foundations.md) and [`tokens.json`](./tokens.json).

---

## 1. Eyebrow label

A small uppercase kicker that names the section and its number.

- **Spec:** 11 pt Bold, Cyan `#00AEEF`, UPPERCASE, letter-tracked.
- **Format:** `NN · SECTION NAME` — zero-padded number, middle dot, then the label.
  Examples: `01 · WHY MANUFACTURE`, `05 · WHO MANUFACTURES TODAY`, `CASE STUDIES · 1 OF 3`.
- **Position:** top-left, y ≈ 0.34".
- **Why:** the running number gives the deck a spine — the reader always knows where they are.

## 2. Takeaway headline

The single most important component in the system. A **full declarative sentence** stating
the slide's conclusion.

- **Spec:** 20–21 pt, Indigo `#221F72`, flush left, one or two lines.
- **Position:** directly under the eyebrow, y ≈ 0.62".
- **Content rule:** it must be a claim you could argue, not a topic. See
  [content-voice.md](./content-voice.md). Everything below it is evidence.

## 3. Divider rule

- **Spec:** full content-width bar, Cyan `#00AEEF`, height 0.03", at y ≈ 1.42".
- Separates the headline stack from the content band. Present on every content slide.

## 4. Feature / benefit card

The default content unit — a titled point with a one-sentence explanation.

- **Anatomy:** (optional icon) → **title** 16 pt Bold Indigo → **body** 14 pt Ink Strong.
- **Layout:** 2-column grid, colA x=1.4", colB x=7.6", card width 4.9".
- **Fill:** usually transparent; use Surface `#EEF2F5` + Hairline `#D7DEE3` border when the
  cards need to read as discrete tiles.
- **Use for:** reasons, benefits, capabilities, risks — any 4–6 parallel points.

## 5. Status pill / tag

A rounded chip that categorizes an item at a glance.

- **Strong / positive:** filled Action Blue `#0C7CB2`, white 9.5 pt Bold text.
  (`Manufacturer`, `Frontier`.)
- **Neutral / weak:** filled Hairline `#D7DEE3`, Ink Strong text.
  (`Delivery only`, `Rare`.)
- **Rule:** pills classify; they never carry a sentence. One pill per item.

## 6. Capability ladder / ranked rows

A vertical sequence of numbered steps, each with a right-aligned status pill.

- **Anatomy per row:** Deep-Navy `#002060` numeral (18 pt) → title (12.5 pt Indigo) →
  gloss (10.5 pt Ink Strong) → status pill on the right.
- **Row fill:** alternating Surface `#EEF2F5` / Hairline `#D7DEE3` bands.
- **Use for:** maturity ladders, tiers, staged progressions (e.g. delivery-only → manufacturer
  → frontier).

## 7. Comparison "vs" pair

Frames a tradeoff as two poles.

- **Format:** `Left label  vs  Right label`, each with a one-line gloss below.
  Example: *Autologous vs Allogeneic — one batch per patient vs off-the-shelf donor batches.*
- **Spec:** labels 14 pt Indigo, glosses 12 pt Ink Strong, `vs` in Ink Muted.
- **Use for:** the "axes" that drive a decision. Keep to 2–3 pairs per slide.

## 8. Term — gloss (definition)

An inline definition device using an em-dash.

- **Format:** `**Term** — plain-language gloss`.
  Example: *Vectors — the delivery vehicle.*
- **Use for:** introducing jargon the first time it appears. Define, then use freely.

## 9. Data table

Full-width comparison grid.

- **Header row:** Indigo fill or Indigo text on Surface, Bold, small (9.5–11 pt).
- **Body cells:** 9.5–11 pt Ink Strong; keep entries to fragments, not sentences.
- **Highlight row:** shade the "our system" row (e.g. MSHS) with Surface `#EEF2F5` to make it
  findable.
- **Legend:** 8 pt strip beneath the table decoding any pills/abbreviations.
- **Use for:** landscape scans — "who does what" across many players.

## 10. Case-study card

A structured profile of one organization.

- **Header:** org name (Bold Indigo) → center/program name → `City, ST · Type · Designation`
  meta line in Ink Muted.
- **Body:** labeled rows — **History · People · Tech & facility · Funding · Results** — each a
  Bold label followed by a fact-dense sentence.
- **Layout:** two profiles side by side per slide; three case-study slides form a set
  (`CASE STUDIES · 1 OF 3`).
- **Honesty rule:** when a fact is unknown, write `Limited information available — …` rather
  than guessing or omitting the row.

## 11. Options / recommendation matrix

Parallel choices, each with a next step.

- **Anatomy per option:** `Option A` chip → **verb title** (Hold / Buy / Build / Partner) →
  one-line description → `Diligence — Validate: …` line in Ink Muted.
- **Layout:** 2×2 or 4-across.
- **Use for:** the recommendation slide. Options are mutually exclusive and named with a verb.

## 12. Executive summary + Contents

The slide-2 pattern: a stack of takeaways plus a table of contents.

- **Left / main:** 4–6 **bolded takeaway sentences**, each followed by a supporting clause —
  effectively the whole deck's argument in miniature.
- **Right / aside:** `CONTENTS` list mirroring the eyebrow numbers, so the summary and the
  spine agree.

## 13. Sources footer

- **Spec:** 8 pt, at y ≈ 6.85". Label `Sources:` in Ink Muted, each source name in Action Blue
  `#0C7CB2`, separated by ` · `.
- **Rule:** every slide that asserts external facts carries one. A dedicated **Sources & method**
  slide closes the deck with full URLs.

## 14. Page number

- **Spec:** 10 pt Muted Violet `#908FB8`, bottom-right, x ≈ 12.5", y ≈ 7.08".
- On every content slide; omit on the cover.

---

### Component → token quick map

| Component | Key color | Key size |
|---|---|---|
| Eyebrow | Cyan `#00AEEF` | 11 pt |
| Headline | Indigo `#221F72` | 20 pt |
| Divider rule | Cyan `#00AEEF` | h 0.03" |
| Card title / body | Indigo / Ink Strong `#44515B` | 16 / 14 pt |
| Pill (strong / neutral) | Action Blue `#0C7CB2` / Hairline `#D7DEE3` | 9.5 pt |
| Ladder numeral | Deep Navy `#002060` | 18 pt |
| Sources | Action Blue / Ink Muted | 8 pt |
| Page number | Violet `#908FB8` | 10 pt |
