# CMD Resource Hub Arizona: keyword research (updated Nov 11, 2026 after the header, tab and footer changes)

Researched Nov 11, 2026 (America/Phoenix). Nothing here is invented: every keyword below was returned by a real source listed in the table, and the placements were checked against the built HTML with a script.

## Sources and what was reachable

| Source | Result |
|---|---|
| Google Autocomplete (`suggestqueries.google.com`), 30 seed phrases, raw output in `hub/v55/kw_suggest.json` | **Worked.** Primary source for every keyword below. This shows what people actually type (frequency rank only, not search volume). |
| Competitor / authority pages (title and meta read live): 211arizona.org, findhelp.org, azfoodbanks.org, azahcccs.gov | **Worked.** Used to confirm vocabulary (see "Competitor wording"). |
| Google Trends | **Not accessible.** The request returned HTTP 400 from the box. No numbers are quoted. |
| Google search results / People Also Ask | **Not accessible.** Google serves a JavaScript gate page to automated requests. I did not bypass it. The FAQ questions were written from the real programs on the site, not copied from PAA. |
| Bing suggestions | **Returned empty/errors**, so not used. |

Limit: autocomplete shows what is commonly searched, not monthly volumes. No volume or ranking numbers are claimed anywhere.

## Final keyword list (28)

"Seen as" is the exact autocomplete suggestion (or seed) that returned it.

| # | Keyword | Seen as (Google Autocomplete) | Theme | Used on the site as |
|---|---|---|---|---|
| 1 | arizona assistance programs | "arizona assistance programs" (seed, plus "...for seniors", "...financial", "...government", "...state", "...rental") | overall | exact: title, State subheader, logo alt |
| 2 | arizona rental assistance | "arizona rental assistance", "arizona rental assistance program" | housing | exact: Housing intro |
| 3 | arizona housing assistance | "arizona housing assistance", "...for low income", "...application" | housing | partial: Housing subheader "housing assistance in Arizona" |
| 4 | help with rent phoenix | "help with rent phoenix", "help paying rent phoenix az" | housing | partial: Housing intro "help with rent" (+ "Phoenix" in same sentence) |
| 5 | emergency shelter phoenix | "emergency shelter phoenix", "...phoenix az" | housing | exact: description, Housing subheader, Housing intro, FAQ |
| 6 | homeless shelters phoenix | "homeless shelters phoenix az", "homeless shelter phoenix" | housing | exact: Housing intro ("homeless shelters in Phoenix") |
| 7 | low income housing phoenix | "low income housing phoenix az" | housing | partial: Housing intro "low-income public housing", Phoenix named in same sentence |
| 8 | food banks phoenix | "food banks phoenix", "food banks phoenix az" | food | exact: description, Health subheader ("FOOD BANKS"), Health intro "food banks ... in Phoenix" |
| 9 | free food pantry phoenix | "free food pantry phoenix" | food | partial: Health intro "free food pantries in Phoenix and Tempe" |
| 10 | tempe food bank | "tempe food bank", "tempe food pantry" | food | partial: Health intro ("food banks ... Phoenix and Tempe") |
| 11 | snap arizona | "snap arizona", "snap arizona application", "...eligibility", "...income limits" | food/benefits | exact ("SNAP" + "Arizona" in context): description, Health subheader, FAQ |
| 12 | ahcccs | "ahcccs", "ahcccs arizona", "ahcccs insurance" | health | exact: description, Health intro, FAQ |
| 13 | free clinics phoenix | "free clinics phoenix az", "free medical clinics phoenix az" | health | partial: Health intro "free and sliding-fee clinics" |
| 14 | free dental phoenix | "free dental phoenix", "free dental clinic phoenix" | health | partial: Health intro "dental help" |
| 15 | free legal aid arizona | "free legal aid arizona" | legal | exact: description ("legal aid"), Legal subheader, FAQ |
| 16 | legal help arizona | "legal help arizona", "legal assistance in arizona" | legal | exact: Legal subheader, Legal intro, FAQ |
| 17 | free legal help phoenix | "free legal help phoenix", "...phoenix az" | legal | exact: Legal intro, FAQ |
| 18 | arizona unemployment benefits | "arizona unemployment benefits", "arizona unemployment insurance" | jobs | exact: Jobs subheader, FAQ |
| 19 | free job training arizona | "free job training arizona", "free job training programs in phoenix az" | jobs | exact: Jobs subheader, Jobs intro, description ("job training") |
| 20 | arizona cash assistance | "arizona cash assistance", "...program", "...eligibility" | state | exact: State subheader, State intro |
| 21 | arizona child care assistance | "arizona child care assistance", "...eligibility", "...application" | state | exact: State intro ("child care assistance"); State subheader says "child care" |
| 22 | utility bill assistance arizona | "utility bill assistance arizona", "electric bill help arizona" | state | partial: State subheader "UTILITY BILL HELP", State intro "utility bill assistance" |
| 23 | arizona veterans assistance | "arizona veterans assistance", "arizona veterans benefits" | state | partial: State intro "Arizona veterans benefits" |
| 24 | 211 arizona | "211 arizona", "211 arizona rental assistance" | directory | exact: FAQ (+ JSON-LD FAQPage) |
| 25 | arizona social services | "arizona social services", "arizona human services" | state | partial: State intro "social services" |
| 26 | community resources phoenix | "community resources phoenix az", "community resource center phoenix" | directory | not used as a phrase (would repeat the tab text) |
| 27 | tempe community resources | "tempe community resources", "tempe homeless resources", "tempe housing resources" | directory | partial: State intro names Tempe, Phoenix and Maricopa County services |
| 28 | arizona benefits | "arizona benefits", "arizona benefits application" | state | not used as a phrase ("benefits" appears in the Jobs/State subheaders and intros) |

Rejected: "free assistance arizona" (returned only roadside-assistance and unrelated results), "free food phoenix" (mixed with gluten-free and pet food), and Phoenixville PA / Phoenix OR variants.

### Competitor wording (read live)
- 211arizona.org title: "2-1-1 Arizona - A Program of Solari".
- findhelp.org title: "Search and Connect to Social Care"; description mentions "financial assistance, food pantries, medical care, and other free or reduced-cost help".
- azfoodbanks.org title: "Find Food Banks in Arizona".
- azahcccs.gov meta keywords: "arizona, medicaid, ..., medical assistance".
- des.az.gov and housing.az.gov block automated requests (Cloudflare), so their titles were not read.

## Where the keywords are placed

Placed as natural phrases. Long-tail variants are used where the exact phrase would read badly. No hidden text and no `meta keywords` tag.

| Location | Text | Keywords covered |
|---|---|---|
| `<title>` (54 chars) | CMD Resource Hub Arizona \| Arizona Assistance Programs | 1 |
| Meta description / og:description / twitter:description (158 chars) | "Free help in Arizona: rent and housing assistance, food banks, emergency shelter, legal aid, AHCCCS, SNAP, job training and more. Official links and contacts." | 2-3, 5, 8, 11, 12, 15, 19 |
| `<h1>` (visible) | RESOURCE HUB ARIZONA, next to the CMD logo | brand |
| Tab headings (h2, ALL CAPS) | HEALTH & FOOD, LEGAL & LAW, FREE CERTS & SCHOOL, BUSINESS & FUNDING, SUPER CHEAP, ALL FREE SERVICES, HOUSING & SHELTER, JOB PLACEMENT & HELP, STATE & OTHER ASSISTANCE | tab names |
| Blue subheaders (h3, ALL CAPS) | FOOD BANKS, HEALTHCARE, AND SNAP; LEGAL AID AND LEGAL HELP; EMERGENCY SHELTER IN PHOENIX, RENT HELP, AND HOUSING ASSISTANCE; JOB HELP, ARIZONA UNEMPLOYMENT BENEFITS, AND FREE JOB TRAINING; ARIZONA ASSISTANCE PROGRAMS: CASH ASSISTANCE, UTILITY BILL HELP, AND CHILD CARE; (others without forced keywords) | 1, 5, 8, 11, 15, 16, 18, 19, 20, 22 |
| Tab intro lines (grey text under each subheader, visible without JS) | e.g. Health: "Food banks and free food pantries in Phoenix and Tempe, SNAP and WIC, AHCCCS coverage through Health-e-Arizona Plus, free and sliding-fee clinics, dental help, and the 988 mental health line." Housing: "...Arizona rental assistance, Section 8 and low-income public housing..." State: "Arizona DES cash assistance and child care assistance, utility bill assistance, Arizona veterans benefits, free tax help, and social services from Tempe, Phoenix and Maricopa County." | 2, 3, 6, 7, 9, 10, 13, 14, 17, 20-23, 25 |
| Visible FAQ (6 questions, same text in JSON-LD FAQPage) | SNAP application, AHCCCS coverage, emergency shelter in Phoenix, free legal help, unemployment benefits, "not sure which program?" (211 Arizona) | 11, 12, 15-18, 24 |
| Logo image alt (`aria-label` and `<title>` of the inline SVG) | "CMD Resource Hub Arizona logo: Arizona assistance programs directory" | 1 |
| JSON-LD | `WebSite` (name, description), `ItemList` (all 549 listings: name and URL), `FAQPage` (the six real FAQ entries) | 1, 11, 12, 15-18, 24 |
| Open Graph / Twitter | og:title, og:description, og:site_name, twitter:title, twitter:description | 1 and the description set |
| Canonical placeholder | HTML comment in `<head>` with `canonical` and `og:url` lines to uncomment once a real domain exists. No fake URL is live. | n/a |

Match types: "exact" means the keyword's words appear together in order, allowing a small connecting word such as "in" (for example "food banks ... in Phoenix", "legal help in Arizona"); "partial" means a natural variant is used (for example "free and sliding-fee clinics" instead of "free clinics Phoenix") because forcing the exact string would read as stuffing. Keywords 26 and 28 are researched but deliberately not used as phrases. Counts: 15 exact, 11 partial, 2 not used. (Checked again against the Nov 11 build with a script after the heading changes.)

## Single place to edit
All SEO text (title, description, per-tab h2/intro, FAQ) and the approved intro live in `hub/v55/config.py`. Rebuild with `python3 build55.py`.
