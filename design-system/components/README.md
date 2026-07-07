# Component previews (Claude Design `/design-sync`)

Each `.html` file here is a **self-contained, theme-aware preview of one component**, written
in the format Claude Design ingests: the **first line is a `<!-- @dsCard group="…" -->` marker**,
so `/design-sync` turns each file into a card in the Design System pane automatically.

| File | Group | Component |
|---|---|---|
| `01-color.html` | Foundations | Color palette |
| `02-type.html` | Foundations | Type scale |
| `03-slide-frame.html` | Layout | The fixed content-slide frame |
| `04-header-stack.html` | Components | Eyebrow → takeaway → cyan rule |
| `05-status-pills.html` | Components | Status pills |
| `06-feature-cards.html` | Components | Feature / benefit cards |
| `07-capability-ladder.html` | Components | Capability ladder |
| `08-landscape-table.html` | Components | Landscape table |
| `09-case-study-card.html` | Components | Case-study card |
| `10-options-matrix.html` | Components | Options / recommendation matrix |
| `11-sources-footer.html` | Components | Sources footer + page number |

All previews read from the same palette as [`../tokens.json`](../tokens.json) and render in both
light and dark. The written spec lives one level up in
[`../README.md`](../README.md) and its sibling docs.

## Syncing into Claude Design

From a Claude Code session **with Claude Design authorization** (local terminal, or a
"Send to Claude Code Web" workspace):

```
cd design-system
claude
/design-sync
```

`/design-sync` reads `tokens.json` + these previews and pushes them to a Claude Design project.
