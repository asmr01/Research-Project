# Foundations

The visual bedrock of the system: brand, color, type, grid, and the graphic motif.
All values are pulled directly from the MSHS template (`MSHS_Template.potx`) and the
way the reference deck applies them. Machine-readable equivalents live in
[`tokens.json`](./tokens.json) and [`tokens.css`](./tokens.css).

---

## Brand

- **Owner:** Mount Sinai Health System (MSHS).
- **Signature mark:** the "three peaks" — three overlapping line-art mountain summits
  (`image1.png` in the template). Use as a quiet, oversized, low-contrast graphic device
  in a corner or as a cover backdrop — never as loud foreground decoration.
- **Wordmark:** available in a white knockout version for dark/photographic covers.
- **Voice of the visuals:** clinical, precise, confident. Lots of white space, thin rules,
  one accent color doing the work. Never busy.

---

## Color

The palette is deliberately narrow: **indigo + cyan carry ~90% of every slide**, neutrals
carry the text, and the remaining hues appear only in charts or as a single call-out.

### Brand (from the theme)

| Token | Hex | Theme slot | Where it goes |
|---|---|---|---|
| **Sinai Cyan** | `#00AEEF` | accent1 | Eyebrow labels, divider rules, key highlights |
| **Sinai Indigo** | `#221F72` | accent2 | Headlines, titles, card titles — the "ink" of the brand |
| **Sinai Magenta** | `#D80B8C` | accent3 | One call-out per slide, maximum. Never body text |
| Light Blue | `#7FD6F7` | accent4 | Chart series only |
| Muted Violet | `#908FB8` | accent5 | Page numbers, secondary meta |
| Light Pink | `#EB85C5` | accent6 | Chart series only |

### Neutrals

| Token | Hex | Use |
|---|---|---|
| Black | `#000000` | Reserve; prefer Ink Strong for body |
| White | `#FFFFFF` | Backgrounds, knockout text |
| Gray | `#666666` | Disabled / tertiary |
| Light Gray | `#CCCCCC` | Hairlines (theme default) |

### Working palette — *use these for real content*

The theme is the legal palette; these are the colors the reference deck actually renders
with. When in doubt, prefer this row over the raw accents for text and surfaces.

| Token | Hex | Use |
|---|---|---|
| Action Blue | `#0C7CB2` | Source-link text, filled status pills |
| Deep Navy | `#002060` | Step / ladder numerals |
| Gradient Blue | `#0067A8` | Cover gradient overlay |
| **Ink Strong** | `#44515B` | **Body copy and card body — the real workhorse** |
| Ink Muted | `#5B6B78` | Lead-in lines, source captions |
| Surface | `#EEF2F5` | Card / panel fills |
| Hairline | `#D7DEE3` | Borders, neutral pill fills |

### Rules

1. **Indigo for what matters, cyan to point at it.** Headlines are indigo; the eyebrow and
   the rule beneath them are cyan.
2. **Body text is Ink Strong (`#44515B`), not black.** Pure black reads as heavy and dated
   against this palette.
3. **One accent call-out per slide.** Magenta or a filled blue pill — never both, never many.
4. **Light blue / pink / violet are chart colors.** Keep them out of text.

---

## Typography

**One typeface: Arial.** Both major and minor fonts in the theme are Arial, so the whole
system is a single family working across weight and size. (Courier New is the declared
mono fallback; you will almost never need it.)

The scale is compact and purposeful — six sizes do the work:

| Role | Size | Weight | Color | Notes |
|---|---|---|---|---|
| Cover title | 48 pt | Bold | Indigo / White on cover | Two lines max |
| Cover subtitle | 18–24 pt | Regular | Indigo / White | |
| **Eyebrow** | 11 pt | Bold | Cyan | UPPERCASE, tracked, `## · LABEL` |
| **Headline (takeaway)** | 20–21 pt | Regular | Indigo | The load-bearing line of the slide |
| Card / subhead title | 16 pt (dense 12.5) | Bold | Indigo | |
| Lead-in line | 12.5 pt | Regular | Ink Muted | Optional intro under headline |
| Body | 14 pt (dense 10.5–12.5) | Regular | Ink Strong | |
| Pill / tag | 9.5 pt | Bold | White on blue / Ink on gray | |
| Step numeral | 18 pt | Bold | Deep Navy | Ladders, ranked lists |
| Sources | 8 pt | Regular | Action Blue links / Ink Muted | |
| Page number | 10 pt | Regular | Muted Violet | Bottom-right |

**Type rules**

- The **headline is a sentence, not a label** (see [content-voice.md](./content-voice.md)) —
  it is sized to be read first and set in indigo to own the slide.
- Dense grids (tables, 8-cell matrices) drop body to 10.5–12.5 pt but never shrink the
  headline. The takeaway always stays 20 pt.
- Set headlines and body **flush left, ragged right.** No centered paragraphs, no justification.

---

## Grid & layout

Canvas is **16:9 — 13.333 in × 7.5 in.** Every content slide shares one skeleton:

```
 0.6"┌─────────────────────────────────────────────┐
     │ 01 · SECTION LABEL              (eyebrow, cyan, y≈0.34)
     │ Full-sentence takeaway headline (indigo, y≈0.62)
     │ ───────────────────────────────  (cyan rule, y≈1.42)
     │
     │        content band  (y ≈ 1.7 – 6.7)
     │        two-column card grid: colA x=1.4"  colB x=7.6"
     │        card width 4.9"
     │
     │ Sources: … (8pt, y≈6.85)                    12│ (page #, x≈12.5 y≈7.08)
     └─────────────────────────────────────────────┘
```

| Metric | Value |
|---|---|
| Left / right margin | 0.6 in |
| Content width | 12.13 in |
| Eyebrow baseline | y ≈ 0.34 in |
| Headline top | y ≈ 0.62 in |
| Cyan divider rule | y ≈ 1.42 in, height 0.03 in |
| Content band | y ≈ 1.7 – 6.7 in |
| Sources footer | y ≈ 6.85 in |
| Page number | x ≈ 12.5 in, y ≈ 7.08 in |
| Two-col cards | colA x = 1.4", colB x = 7.6", width 4.9", gutter ≈ 0.8" |

**Grid rules**

- The **eyebrow → headline → cyan rule** stack is fixed. It appears on every content slide and
  anchors the reader. Never skip the rule.
- Content hangs below the rule in a **2-column card grid** by default; tables and ladders span
  the full 12.13" width.
- Keep the **sources footer and page number** on every content slide. They are part of the
  frame, not optional.
- Generous margins are the look. If content feels cramped, cut words or split the slide —
  do not shrink the margins.

---

## The motif

The three-peaks mark is the only decorative element. Deploy it as:

- an **oversized, ~8% opacity** watermark bleeding off a cover or divider corner, or
- a **small cyan or indigo mark** top-left of a cover.

Never stretch it, recolor it into the magenta, or place it over text.
