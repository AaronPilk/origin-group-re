# Origin Group — origingroupre.com

Static rebuild of the Origin Group site (formerly Squarespace). Same URLs, same copy, new luxury design, full SEO + AI-search layer.

## Edit and rebuild

```bash
python3 build.py          # regenerates every page, sitemap, llms.txt, schema
PRUNE=1 python3 build.py  # same, and deletes image sizes no page uses
```

- **Copy, team, services, FAQ, contact details:** top of `build.py` (`SITE`, `HOME_CAPS`, `CAP_SERVICES`, `TEAM`, `ABOUT_INTRO`, `FAQ`).
- **Transactions:** `data/experience.json` (one object per property; `heads` = title lines, `images` = gallery in order). Add an entry, drop the WebP files into `assets/img/`, rebuild.
- **Styles / motion:** `assets/css/site.css`, `assets/js/site.js` (Lenis smooth scroll is vendored in `assets/js/lenis.min.js`).
- **Hero film:** `assets/video/hero-1920.mp4` (desktop) and `hero-portrait-720.mp4` (phones, center crop of the same drone shot).

## Hosting (Cloudflare Pages)

Framework preset **None** · build command **none** · output directory **`/`** · production branch **`main`**.
`_redirects` and `_headers` are Cloudflare-native. `vercel.json` mirrors them if it ever moves to Vercel.

## Forms

Contact form and the Select Insights signup post to FormSubmit (`SITE["form_endpoint"]`).
The **first** submission sends a one-time activation email to info@origingroupre.com — click the link once and all later submissions deliver. Swap the endpoint any time.

## SEO / AI search

- Canonical URLs identical to the old site: `/`, `/capabilities`, `/experience`, `/experience/<slug>`, `/team`, `/about`, `/contactus`. Old Squarespace-only paths 301 to the right page.
- JSON-LD graph on every page: `RealEstateAgent` organization (address, phone, founder, employees, services catalog, areas served), `WebSite`, `WebPage`/`AboutPage`/`ContactPage`/`CollectionPage`, `BreadcrumbList`, `Person` for each team member, `Service` per capability, `ItemList` of transactions, `Place` per property, `FAQPage`, `VideoObject`.
- `sitemap.xml` with image + video entries, `robots.txt` explicitly welcoming search and AI crawlers, `llms.txt` + `llms-full.txt` for AI assistants.
- Per-page titles, descriptions, Open Graph/Twitter cards with generated 1200×630 images in `assets/og/`.

Website by [Pilk.ai](https://pilk.ai)
