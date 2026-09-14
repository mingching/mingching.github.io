# vanlinlin.github.io

Personal academic homepage: https://vanlinlin.github.io/

## 🖊️ How to update content (no HTML needed)

All content lives in `_data/*.yml` — edit the YAML, commit, done.
The templates render everything (cards, badges, buttons, timeline) automatically.

| What to update | File | How |
|---|---|---|
| Add a publication | `_data/publications.yml` | Copy an entry to the **top**, edit fields. `media:` ending in `.mp4` auto-plays as a muted looping video. Only fill the `links:` you have (`paper` / `arxiv` / `project` / `code`) — buttons appear automatically. |
| Add news | `_data/news.yml` | New entry at top. `hot: true` = highlighted gradient dot. |
| Add an award | `_data/awards.yml` | New entry at top. `tier: gold / silver / bronze` picks the medal 🥇🥈🥉. |
| Research projects | `_data/research_projects.yml` | Same format as publications. |
| Funded projects | `_data/funded_projects.yml` | `period` + `text`. |
| Education / services | `_data/education.yml`, `_data/services.yml` | Self-explanatory fields. |
| Biography / hero | `_pages/about.md` | The intro text, typing-effect roles (`data-roles`), interest chips, CV link. |
| Nav bar | `_data/navigation.yml` | Section anchors. |

## 🖥️ Local preview (Windows)

```bash
bundle _2.6.7_ install          # first time only
bundle _2.6.7_ exec jekyll serve --watch
# open http://127.0.0.1:4000/
```

Notes:
- Use bundler `2.6.7` (`bundle _2.6.7_ ...`) — the default 2.2.19 crashes on Ruby 3.4.
- Test dark mode with the 🌙 button (bottom-right), or force it via `http://127.0.0.1:4000/?theme=dark`.

## 🎨 Design system

- Dual light/dark theme via CSS variables — tokens defined at the top of `_sass/_theme.scss` (`:root` = light, `html[data-theme="dark"]` = dark). Change accent colors there.
- Interactions (theme toggle, scroll reveal, stat counters, typing effect, news show-more, card tilt/spotlight) in `assets/js/theme.js`.
- Live Google-Scholar data (total citations, h-index, per-paper "Cited by" chips, citation-trend sparkline) comes from `google_scholar_crawler/results/gs_data.json` on `main`, refreshed daily by the GitHub Action — no manual upkeep. Per-paper chips match cards by title, so keep `_data/publications.yml` titles close to the Scholar titles.
- Card / timeline / chip / button templates in `_includes/pub-cards.html`, `news-timeline.html`, `awards-list.html`, `stats-row.html`, etc.
