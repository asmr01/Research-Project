# MSHS Presentation Design System

A design system for building presentations that look and read like the Mount Sinai Health System
(MSHS) template — and, just as importantly, that *communicate* like the reference deck that
resonates: clear headline takeaways, precise quantified language, lead-with-the-conclusion
structure.

It is written so that **Claude (or a person) can pick it up and produce a new on-brand,
on-voice deck** without seeing the original files.

## Source material

| File | Role | What we took from it |
|---|---|---|
| `MSHS_Template.potx` | **Template** | Colors, fonts, grid, slide layouts, the three-peaks motif |
| `DRAFT_MSHS_CGT_Manufacturing_Assessment.pptx` | **Reference** | How the template is applied, and the content/language patterns that work |

## What's inside

| File | Read it for |
|---|---|
| [`foundations.md`](./foundations.md) | Brand, color, typography, grid, motif — the visual bedrock |
| [`components.md`](./components.md) | The 14 reusable parts (eyebrow, takeaway headline, pills, cards, ladders, tables, case-study cards…) |
| [`slide-templates.md`](./slide-templates.md) | 9 slide archetypes and when to use each |
| [`content-voice.md`](./content-voice.md) | The writing system — 12 rules for language that lands |
| [`tokens.json`](./tokens.json) | Machine-readable colors, type scale, layout metrics |
| [`tokens.css`](./tokens.css) | The same tokens as CSS custom properties for web/HTML renders |

## The system in one screen

**Visual DNA**
- One typeface (**Arial**), a narrow palette led by **Indigo `#221F72`** + **Cyan `#00AEEF`**,
  body in **Ink Strong `#44515B`**.
- Every content slide shares one frame: **eyebrow → takeaway headline → cyan rule → content →
  sources + page number.**
- Generous margins, thin rules, one accent doing the work. Never busy.

**Voice DNA**
- **Lead with the takeaway.** Headlines are full sentences stating the conclusion; the body backs
  them with facts.
- **Quantify everything**, define jargon inline, frame tradeoffs as *X vs Y*, classify with pills,
  flag unknowns honestly, cite as you go.
- If a reader skimmed only the headlines, they'd get the whole argument.

## How to use it to build a deck

1. **Pick the archetype** for each slide from [`slide-templates.md`](./slide-templates.md).
2. **Write the takeaway headline first** — a sentence, not a topic ([`content-voice.md`](./content-voice.md)).
3. **Assemble the body** from [`components.md`](./components.md) on the shared grid.
4. **Apply tokens** from [`tokens.json`](./tokens.json) for exact colors and sizes.
5. **Run the checklist** at the bottom of [`content-voice.md`](./content-voice.md) on every slide.

## Non-negotiables

- Headlines are conclusions, not labels.
- Indigo + cyan carry the slide; one call-out accent, maximum.
- The eyebrow/headline/rule stack and the sources/page-number footer appear on every content slide.
- Body text is Ink Strong `#44515B`, never pure black.
- Every fact-bearing slide cites its sources.
