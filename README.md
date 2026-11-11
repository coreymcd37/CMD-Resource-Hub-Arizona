# CMD Resource Hub Arizona

A single-page, standalone directory of free and sponsored resources for Arizona residents, covering food, health care, housing, jobs, legal help, education, and business funding. Each listing links to the official program and its contact details.

![Desktop view](assets/screenshots/desktop.png)

## Features
- 9 categories: Health & Food, Legal & Law, Certs & School, Business & Funding, Super Cheap, All Services, Housing & Shelter, Job Placement & Help, State & Other Assistance.
- Works with no JavaScript (CSS-only tabs and native dropdowns), including sandboxed previews such as iPhone in-app viewers.
- With JavaScript: per-tab and global search, subcategory filter, print / save as PDF, and an optional AI "find similar" helper.
- AI uses free no-key providers with automatic fallback; you can add your own free Gemini, Groq, OpenRouter, or Mistral key in Settings. Keys are stored only in your browser's localStorage. No keys are in this repo.
- Dark glass theme in electric blue and orange; SEO metadata and JSON-LD included.

## Use
Open `index.html` in any browser, or host it on any static host (GitHub Pages, Netlify, Vercel, Cloudflare Pages). Serve it gzipped for best mobile performance.

## Repository layout
| Path | Contents |
|---|---|
| `index.html` | The complete, self-contained site |
| `src/` | Readable sources: `data.json` (listings), `config.py` (text), `css.css`, `core.js`, `app.js`, `providers.json` (AI providers), `build55.py` (builder) |
| `tests/` | Playwright test scripts (no-JS, JS features, failure fallbacks, links) |
| `docs/` | Full PDF printout, SEO keyword list, data audit log |
| `assets/screenshots/` | Desktop and mobile screenshots |

## Rebuild
```bash
cd src && python3 build55.py   # writes ../index.html
```
Tests need Python with Playwright (`pip install playwright && playwright install`) and are run from the repository root.

## Accuracy
Links and contact information were checked as of November 2026. All information came from official organization web pages or an authoritative .gov listing. Programs change; confirm details with the organization before applying.
