#!/usr/bin/env python3
"""
Origin Group — static site generator.

Edit SITE / page content below, then run:  python3 build.py
Outputs plain HTML at the repo root on the same URLs as the old Squarespace
site (/, /capabilities, /experience, /experience/<slug>, /team, /about,
/contactus) so existing search rankings carry over.

All page copy is the client's existing wording, unchanged.
"""
import json, os, re, html, hashlib, datetime, shutil
from pathlib import Path

ROOT = Path(__file__).parent
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year

SITE = {
    "name": "Origin Group",
    "legal": "Origin Group",
    "domain": "https://www.origingroupre.com",
    "phone_display": "+1 (323) 410-2650",
    "phone_tel": "+13234102650",
    "phone_schema": "+1-323-410-2650",
    "email": "info@origingroupre.com",
    "street": "9454 Wilshire Blvd",
    "city": "Beverly Hills",
    "region": "CA",
    "zip": "90212",
    "country": "US",
    "maps": "https://www.google.com/maps/search/?api=1&query=9454+Wilshire+Blvd+Beverly+Hills+CA+90212",
    # Form delivery. FormSubmit sends one activation email to the inbox below on
    # the first submission; click it once and every form after that delivers.
    # Swap for a GoHighLevel / Cloudflare endpoint any time.
    "form_endpoint": "https://formsubmit.co/ajax/info@origingroupre.com",
    "description": "Origin Group is a Beverly Hills commercial real estate advisory and investment platform. "
                   "Acquisitions, dispositions, leasing, asset advisory and capital strategy across retail, "
                   "restaurant, medical, healthcare, industrial, net lease, self-storage, office and land — "
                   "Southern California and select U.S. markets.",
}

META = json.load(open(ROOT / "data/imgmeta.json"))
EXP = json.load(open(ROOT / "data/experience.json"))
EXP = [e for e in EXP if e["images"]]
BYSLUG = {e["slug"]: e for e in EXP}
USED = set()

def esc(s): return html.escape(s, quote=True)

def asset_v(path):
    p = ROOT / path.lstrip("/")
    return hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "1"

# ---------------------------------------------------------------- images
def _variants(stem, hero):
    m = META[stem]
    return [s for s in m["sizes"] if s < 2400 or hero]

def srcset(stem, hero=False):
    m = META[stem]; out = []
    for s in _variants(stem, hero):
        USED.add(f"{stem}-{s}.webp")
        out.append(f"/assets/img/{stem}-{s}.webp {min(s, m['w'])}w")
    return ", ".join(out)

def src(stem, pref=1600):
    m = META[stem]
    s = pref if pref in m["sizes"] else max(x for x in m["sizes"] if x <= max(pref, 800))
    USED.add(f"{stem}-{s}.webp")
    return f"/assets/img/{stem}-{s}.webp"

def img(stem, alt, sizes="100vw", cls="", eager=False, hero=False, extra=""):
    m = META[stem]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{src(stem)}" srcset="{srcset(stem, hero)}" sizes="{sizes}" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{esc(alt)}" {load} decoding="async"'
            f'{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} {extra}>')

def abs_img(stem, pref=1600): return SITE["domain"] + src(stem, pref)

# ---------------------------------------------------------------- content
HOME_FEATURED = [
    ("250-256-s-la-cienega-blvd-beverly-hills", "Beverly Hills Surgical Center", "250-256-s-la-cienega-blvd-2-baa2a1"),
    ("8327-reseda-blvd-endeavor-medical-plaza", "Endeavor Medical Plaza", "8327-reseda-blvd-compass-aerial-1c86ec"),
    ("2431-nw-2nd-ave-society-wynwood-miami-florida", "Society Wynwood | Miami", "176-nw-25th-st-miami-fl-aerial-29-largehighdefinit-b6241e"),
    ("2140-e-el-segundo-blvd", "Chargers Commons", "2140-el-segundo-blvd-chargers-commons-cc2541"),
]

HOME_CAPS = [
    ("Acquisition, Disposition & Asset Management",
     "Acquisition, repositioning, asset management, and disposition across retail, medical, healthcare, industrial, office, and land properties.",
     "1257061333-ec051c"),
    ("Asset Advisory",
     "Strategic support across valuation, 1031 exchanges, capital markets, sale-leasebacks, owner-user and SBA strategies, corporate relocation, and workplace planning. Focused on informed decision-making and long-term real estate planning.",
     "photo-2-c54b82"),
    ("Capital & Transaction Execution",
     "Structured transaction execution aligned with long-term investment objectives, supported by disciplined underwriting and established capital relationships.",
     "1073907230-0416d8"),
    ("Select Clientele",
     "Origin Group serves a focused group of private investors, high-net-worth individuals, family offices, private equity firms, institutional capital, and regional and national operating companies. Relationships are built on discretion, trust, and repeat execution.",
     "1604086218-df7413"),
    ("Specializations",
     "Retail · Restaurant · Medical · Healthcare · Industrial · Net Lease · Self-Storage · Office · Land",
     "photo-1-5d0f4a"),
    ("Markets & Reach",
     "Primary markets served include Southern California, with select advisory and investment activity across major U.S. markets.",
     "city-buildings-with-sunset-reflection-c0310e"),
]
SPECIALIZATIONS = ["Retail", "Restaurant", "Medical", "Healthcare", "Industrial", "Net Lease", "Self-Storage", "Office", "Land"]

CAP_SERVICES = [
    {"title": "Transaction Advisory & Execution", "img": "1257061333-ec051c",
     "paras": ["We structure and execute acquisitions, recapitalizations, repositionings, and dispositions across a range of commercial asset types. Each transaction is grounded in underwriting discipline, strategic positioning, and clear alignment of objectives from initial analysis through closing."],
     "lead": None,
     "items": [("Investment Sales and Leasing", "Across Retail, Restaurant, Medical, Office, Industrial, Land"),
               ("Landlord and Tenant Advisory", None), ("Owner-User Transactions", None),
               ("Confidential and Off-Market Processes", None)]},
    {"title": "Asset-Level & Portfolio Advisory", "img": "photo-2-c54b82",
     "paras": ["We oversee asset strategy across operational, leasing, and capital planning phases to drive performance and long-term value. Our approach integrates repositioning strategy, tenant curation, and disciplined asset management."],
     "lead": "Advisory assignments may include:",
     "items": [("Hold vs. Sell Analysis", None), ("Asset Repositioning Strategy", None),
               ("Portfolio Planning and Sequencing", None), ("Long-Term Real Estate Planning", None)]},
    {"title": "Owner-User & Operating Company Advisory", "img": "1604086218-df7413",
     "paras": ["We work closely with business owners and operating companies where real estate decisions directly impact operations, growth, and capital allocation.",
               "Our work considers both real estate and business objectives, ensuring ownership, leasing, or monetization decisions support the broader enterprise."],
     "lead": "Services may include:",
     "items": [("Owner-User Transactions", None), ("Sale-Leaseback Advisory", None),
               ("Expansion, Consolidation, and Relocation Planning", None),
               ("Coordination with Lenders, Attorneys, Wealth Managers, Estate Planners, and Professional Advisors", None)]},
    {"title": "Market Intelligence & Underwriting", "img": "1073907230-0416d8",
     "paras": ["We provide valuation insight and market analysis to support informed decision-making.",
               "Investment decisions are informed by active market knowledge, transaction experience, and rigorous underwriting. Emphasis is placed on clarity of basis, timing, and risk-adjusted execution."],
     "lead": "Services include:",
     "items": [("Pricing and Valuation Guidance", None), ("Market and Submarket Analysis", None),
               ("Underwriting and Feasibility Support", None), ("Strategic Review of Alternatives", None)]},
]

TEAM = [
    {"name": "Oliver Ghadoushi", "role": "Founder & Principal", "img": "main-oliver-ghadoushi-headshot-2f55a3", "id": "oliver-ghadoushi",
     "bio": ["Oliver Ghadoushi is the Founder and Principal of Origin Group, a commercial real estate advisory and investment platform focused on complex acquisitions, asset repositioning, and strategic opportunities across Southern California and select U.S. markets.",
             "Origin Group works across the full transaction lifecycle, spanning acquisitions, dispositions, leasing, and long-term portfolio strategy — on assignments where thoughtful structuring and precise execution materially influence outcomes. The platform works closely with private investors, family offices, institutional capital, and operating businesses navigating significant real estate decisions.",
             "Known for a disciplined and thoughtful approach, Oliver prioritizes clarity and discretion while executing complex transactions with a focus on risk management and long-term value creation. His front-line transactional experience enables him to identify challenges early, structure solutions, and execute with precision — reflecting a relationship-driven practice grounded in trusted advisory and a deep understanding of market dynamics."]},
    {"name": "Anthony Assatourian", "role": "Associate", "img": "anthony-assatourian-headshot-054c05", "id": "anthony-assatourian",
     "bio": ["Anthony Assatourian is an Associate at Origin Group, where he supports advisory and transactional initiatives across a range of commercial real estate opportunities, including retail, industrial, medical, office, land, and development assets.",
             "Anthony brings a disciplined and analytical perspective to transactions, evaluating opportunities, identifying risk, and supporting thoughtful structuring and execution. His work is grounded in careful preparation, market awareness, and a focus on outcomes that support long-term value.",
             "With a strong foundation in business and finance, Anthony works closely across all stages of the transaction process. He is known for his professionalism, attention to detail, and ability to deliver clear, well-supported insight in dynamic and competitive environments.",
             "Anthony approaches each transaction with focus and accountability, building trust through preparation, responsiveness, and a consistent commitment to high-quality execution."]},
    {"name": "Jonah Kharrazi", "role": "Associate", "img": "jonah-kharrazi-headshot-master-fcdf88", "id": "jonah-kharrazi",
     "bio": ["Jonah Kharrazi is an Associate at Origin Group, where he supports advisory and transactional initiatives across a range of commercial real estate opportunities.",
             "Jonah focuses on investment analysis, market research, and due diligence related to acquisitions, dispositions, and development-related opportunities. His work emphasizes accuracy, preparation, and a thorough understanding of asset fundamentals, helping ensure decisions are informed and well-supported.",
             "He contributes throughout the transaction process, assisting with underwriting, market evaluation, and the organization of materials that support clear positioning and effective execution. Jonah approaches his work with a methodical and detail-oriented mindset, contributing to consistency and reliability across the team’s work.",
             "Jonah is valued for his professionalism, work ethic, and analytical discipline. He works collaboratively within the team and approaches his work with focus and care, contributing to high-quality execution."]},
]

ABOUT_INTRO = [
    "Origin Group was founded on a simple belief: the best outcomes are created at the beginning. From acquisition strategy and disposition planning to leasing, repositioning, and long-term portfolio decisions, value is not accidental – it is originated.",
    "Origin Group advises across the full lifecycle of commercial real estate, with a focus on strategic clarity, disciplined execution, and alignment of interests. Our approach blends institutional rigor with boutique-level attention, allowing us to operate with both precision and flexibility in dynamic markets.",
]
PRINCIPLES = ["Strategy before execution", "Alignment over speed", "Clarity over complexity", "Long-term relationship"]
WHAT_WE_DO = ["Investment Sales, Leasing, and Dispositions", "Owner-User Acquisitions and Sale-Leasebacks",
              "Leasing and Tenant Representation", "Portfolio Strategy and Repositioning Advisory",
              "Market Analysis and Valuation Guidance"]

# Questions are phrased for search/AI engines; every answer is the client's own wording.
FAQ = [
    ("What does Origin Group do?", ABOUT_INTRO[1]),
    ("What advisory services does Origin Group provide?",
     "Origin Group provides a range of advisory services, including: Investment Sales, Leasing, and Dispositions; Owner-User Acquisitions and Sale-Leasebacks; Leasing and Tenant Representation; Portfolio Strategy and Repositioning Advisory; and Market Analysis and Valuation Guidance."),
    ("What property types does Origin Group work with?",
     "Our experience spans retail, restaurant, medical, industrial, office, land, and mixed-use assets, with a particular strength in transactions where structure, timing, and strategy materially impact outcomes."),
    ("Which markets does Origin Group serve?",
     "Primary markets served include Southern California, with select advisory and investment activity across major U.S. markets."),
    ("Who does Origin Group work with?",
     "Origin Group works alongside private and institutional investors, family offices, owner-operators, and regional and national operating businesses. Our work is relationship-based and defined by confidentiality, trust, and consistent execution."),
    ("Who leads Origin Group?", TEAM[0]["bio"][0]),
    ("Where is Origin Group located?",
     "Main offices: 9454 Wilshire Blvd, Beverly Hills, CA 90212. Phone: +1 (323) 410-2650. Email: info@origingroupre.com."),
]

NAV = [("Home", "/"), ("Capabilities", "/capabilities"), ("Experience", "/experience"),
       ("Team", "/team"), ("About", "/about"), ("Contact", "/contactus")]

# ---------------------------------------------------------------- experience helpers
def split_title(t):
    if "|" in t:
        a, b = [x.strip() for x in t.split("|", 1)]
        return a, b
    return t.strip(), ""

def exp_hero(e): return e["images"][0]
def exp_thumb(e): return e["thumb"] if e.get("thumb") in META else e["images"][0]

def exp_region(e):
    t = " ".join(e["heads"]) + " " + e["slug"]
    if "Miami" in t: return "FL"
    if "Eagle" in t and "ID" in t: return "ID"
    return "CA"

def exp_locality(e):
    a, b = split_title(e["listTitle"])
    if b and not re.match(r"^\d", b): return b.replace(", Florida", "")
    for h in e["heads"][1:3]:
        h2 = h.split("|")[-1].strip()
        if h2 and not re.search(r"\d", h2) and len(h2) < 30: return h2.replace(", Florida", "").replace(", ID", "")
    return ""

def exp_street(e):
    for h in [e["listTitle"]] + e["heads"]:
        for part in re.split(r"\s*\|\s*|,\s*", h):
            if re.match(r"^[\d±]", part.strip()) and re.search(r"[A-Za-z]{2,}", part): return part.strip()
    return ""

def exp_descriptor(e):
    for h in e["heads"][1:]:
        if re.match(r"^[\d,±.]+\s*(SF|UNITS|AC)\b", h): continue
        for seg in [s.strip() for s in h.split(" | ")]:
            if len(seg) > 18 and not re.match(r"^[\d±]", seg) and seg not in e["listTitle"]: return h if not re.match(r"^[\d±]", h) else seg
    return ""

def exp_name(e):
    """Search-friendly label: property name + address when both exist."""
    name = e["heads"][0].split("|")[0].strip()
    addr = e["listTitle"].replace(" | ", ", ")
    if name.lower() in addr.lower(): return addr
    if re.match(r"^\d", name): return addr
    parts = [s.strip() for s in e["listTitle"].split("|") if s.strip().lower() not in name.lower()]
    return ", ".join([name] + parts)

def alt_for(e, i=None):
    d = exp_descriptor(e)
    base = e["listTitle"].replace(" | ", ", ")
    if i is None: return f"{base}{' — ' + d if d else ''}"
    return f"{base} — photo {i}"

# ---------------------------------------------------------------- JSON-LD
ORG_ID = SITE["domain"] + "/#organization"
WEB_ID = SITE["domain"] + "/#website"

def person_ld(p):
    return {"@type": "Person", "@id": f"{SITE['domain']}/team#{p['id']}", "name": p["name"], "jobTitle": p["role"],
            "image": abs_img(p["img"], 800), "description": p["bio"][0],
            "worksFor": {"@id": ORG_ID}, "url": f"{SITE['domain']}/team#{p['id']}",
            "knowsAbout": ["Commercial real estate", "Investment sales", "Acquisitions", "Dispositions", "Leasing", "Underwriting"]}

def org_ld():
    services = []
    for s in CAP_SERVICES:
        services.append({"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["title"], "description": s["paras"][0],
                         "provider": {"@id": ORG_ID}, "areaServed": [{"@type": "AdministrativeArea", "name": "Southern California"}, {"@type": "Country", "name": "United States"}],
                         "serviceType": s["title"]}})
    return {
        "@type": ["RealEstateAgent", "ProfessionalService"], "@id": ORG_ID, "name": SITE["name"],
        "alternateName": ["Origin Group RE", "Origin Group Real Estate", "Origin Group Commercial Real Estate"],
        "url": SITE["domain"] + "/", "logo": {"@type": "ImageObject", "url": SITE["domain"] + "/assets/brand/logo-navy.png", "width": 900, "height": 313},
        "image": SITE["domain"] + "/assets/og/home.jpg",
        "description": SITE["description"], "slogan": "Every Property Has An Origin.",
        "telephone": SITE["phone_schema"], "email": SITE["email"],
        "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "addressLocality": SITE["city"],
                    "addressRegion": SITE["region"], "postalCode": SITE["zip"], "addressCountry": SITE["country"]},
        "hasMap": SITE["maps"],
        "areaServed": [{"@type": "AdministrativeArea", "name": "Southern California"}, {"@type": "City", "name": "Los Angeles"},
                       {"@type": "City", "name": "Beverly Hills"}, {"@type": "Country", "name": "United States"}],
        "founder": {"@id": f"{SITE['domain']}/team#oliver-ghadoushi"},
        "employee": [{"@id": f"{SITE['domain']}/team#{p['id']}"} for p in TEAM],
        "knowsAbout": ["Commercial real estate advisory", "Investment sales", "Acquisitions", "Dispositions", "Leasing",
                       "Tenant representation", "1031 exchanges", "Sale-leasebacks", "Owner-user transactions", "SBA strategies",
                       "Capital markets", "Asset management", "Asset repositioning", "Valuation", "Underwriting", "Net lease"] + SPECIALIZATIONS,
        "contactPoint": {"@type": "ContactPoint", "telephone": SITE["phone_schema"], "email": SITE["email"], "contactType": "sales",
                         "areaServed": "US", "availableLanguage": ["English"]},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Capabilities", "itemListElement": services},
    }

def website_ld():
    return {"@type": "WebSite", "@id": WEB_ID, "url": SITE["domain"] + "/", "name": SITE["name"],
            "description": SITE["description"], "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "@id": items[-1][1] + "#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def page_ld(kind, url, name, desc, image, crumbs, extra=None, about=None):
    page = {"@type": kind, "@id": url + "#webpage", "url": url, "name": name, "description": desc,
            "isPartOf": {"@id": WEB_ID}, "about": about or {"@id": ORG_ID}, "inLanguage": "en-US",
            "primaryImageOfPage": {"@type": "ImageObject", "url": image}, "breadcrumb": {"@id": crumbs[-1][1] + "#breadcrumb"},
            "dateModified": TODAY}
    graph = [page, crumbs_ld(crumbs), org_ld(), website_ld()] + [person_ld(p) for p in TEAM] + (extra or [])
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- layout
CSS_V = JS_V = "1"

def head(title, desc, path, og_img, ld, preload="", robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"):
    url = SITE["domain"] + path
    fonts_css = (ROOT / "assets/fonts/fonts.css").read_text()
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="author" content="Origin Group">
<meta name="theme-color" content="#0E2A35">
<meta name="format-detection" content="telephone=no">
<meta name="geo.region" content="US-CA"><meta name="geo.placename" content="Beverly Hills">
<meta property="og:site_name" content="Origin Group">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/brand/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/brand/icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="alternate" type="text/markdown" href="/llms.txt" title="Origin Group summary for AI assistants">
<link rel="preload" href="/assets/fonts/InstrumentSerif-normal-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/Manrope-normal-300-700.woff2" as="font" type="font/woff2" crossorigin>
{preload}
<style>{fonts_css}</style>
<link rel="stylesheet" href="/assets/css/site.css?v={CSS_V}">
<script>document.documentElement.classList.add('js');try{{if(sessionStorage.getItem('og-nav'))document.documentElement.classList.add('arriving')}}catch(e){{}}</script>
<script type="application/ld+json">{ld}</script>
</head>
"""

def nav_html(active):
    links = "".join(f'<li><a href="{u}"{" aria-current=page" if u == active else ""}>{n}</a></li>' for n, u in NAV[1:])
    mlinks = "".join(f'<li style="--i:{i}"><a href="{u}"><span class="menu__num">0{i+1}</span>{n}</a></li>' for i, (n, u) in enumerate(NAV))
    return f"""<body>
<a class="skip" href="#main">Skip to content</a>
<div class="curtain" aria-hidden="true"><img src="/assets/brand/logo-gold.webp" alt="" width="900" height="313"></div>
<header class="nav" data-nav>
  <div class="nav__inner">
    <a class="nav__logo" href="/" aria-label="Origin Group home"><img src="/assets/brand/logo-white.webp" alt="Origin Group" width="900" height="313"></a>
    <nav class="nav__links" aria-label="Primary"><ul>{links}</ul></nav>
    <a class="btn btn--line nav__cta" href="/contactus">Connect With Us</a>
    <button class="nav__burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu" data-menu-toggle><span></span><span></span></button>
  </div>
</header>
<div class="menu" id="menu" aria-hidden="true">
  <div class="menu__inner">
    <ul class="menu__links">{mlinks}</ul>
    <div class="menu__foot">
      <p class="eyebrow">Main Offices</p>
      <p>{SITE['street']}<br>{SITE['city']}, {SITE['region']} {SITE['zip']}</p>
      <p><a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a><br><a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
    </div>
  </div>
</div>
<main id="main">
"""

def cta_band(title="Connect With Us", label="Contact", img_stem="1--14-a56765", button="Connect With Us"):
    return f"""<section class="cta" data-theme="dark">
  <div class="cta__media" data-parallax="-0.12">{img(img_stem, "Aerial view of downtown Los Angeles at dusk", sizes="100vw")}</div>
  <div class="cta__scrim"></div>
  <div class="container cta__inner">
    <p class="eyebrow" data-reveal>{label}</p>
    <h2 class="display cta__title" data-split>{title}</h2>
    <div class="cta__row" data-reveal style="--d:2">
      <a class="btn btn--gold" href="/contactus" data-magnetic>{button}</a>
      <a class="cta__link" href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a>
      <a class="cta__link" href="mailto:{SITE['email']}">{SITE['email']}</a>
    </div>
  </div>
</section>
"""

def footer_html():
    links = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in NAV)
    return f"""</main>
<footer class="footer" data-theme="dark">
  <div class="container footer__top">
    <div class="footer__brand">
      <a href="/" aria-label="Origin Group home"><img src="/assets/brand/logo-white.webp" alt="Origin Group" width="900" height="313" loading="lazy"></a>
    </div>
    <div class="footer__col">
      <p class="eyebrow">Main Offices</p>
      <address>{SITE['street']}<br>{SITE['city']}, {SITE['region']} {SITE['zip']}</address>
      <p>Phone: <a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a></p>
      <p><a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
    </div>
    <nav class="footer__col" aria-label="Footer"><p class="eyebrow">Navigate</p><ul class="footer__nav">{links}</ul></nav>
    <div class="footer__col footer__news">
      <h2 class="h3">Sign Up for Select Insights</h2>
      <p class="footer__sub">On commercial real estate strategy, markets, and transactions</p>
      <form class="news" data-form data-kind="newsletter" novalidate>
        <label class="sr-only" for="news-email">Email Address</label>
        <input id="news-email" type="email" name="email" placeholder="Email Address" autocomplete="email" required>
        <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
        <button class="btn btn--gold" type="submit">Subscribe</button>
        <p class="form__ok" role="status" hidden>Thank you, We’ll be in touch!</p>
        <p class="form__err" role="alert" hidden></p>
      </form>
    </div>
  </div>
  <div class="footer__mark" aria-hidden="true"><img src="/assets/brand/logo-white.webp" alt="" width="900" height="313" loading="lazy" data-parallax="0.08"></div>
  <div class="container footer__base">
    <p>© {YEAR} Origin Group. All rights reserved.</p>
    <p><a href="/llms.txt">AI summary</a><span aria-hidden="true"> · </span><a href="/sitemap.xml">Sitemap</a><span aria-hidden="true"> · </span>Website by <a href="https://pilk.ai" rel="noopener">Pilk.ai</a></p>
  </div>
</footer>
<script>window.OG_FORM={json.dumps(SITE['form_endpoint'])};window.OG_EMAIL={json.dumps(SITE['email'])};</script>
<script src="/assets/js/lenis.min.js" defer></script>
<script src="/assets/js/site.js?v={JS_V}" defer></script>
</body>
</html>
"""

def write(path, content):
    p = ROOT / path.lstrip("/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

def split_amp(text):
    # mark ampersands so the display face can italicize them in gold
    return text

def page_hero(stem, alt, eyebrow, h1, sub_html="", cls=""):
    return f"""<section class="phero {cls}" data-theme="dark" data-hero>
  <div class="phero__media" data-hero-media>{img(stem, alt, sizes="100vw", eager=True, hero=True)}</div>
  <div class="phero__scrim"></div>
  <div class="container phero__inner">
    <p class="eyebrow phero__eyebrow" data-reveal>{eyebrow}</p>
    <h1 class="display" data-split>{esc(h1)}</h1>
    {sub_html}
  </div>
</section>
"""

def hero_preload(stem):
    return (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{srcset(stem, True)}" imagesizes="100vw" fetchpriority="high">')

# ---------------------------------------------------------------- pages
def build_home():
    path = "/"
    title = "Origin Group | Commercial Real Estate Advisory & Investment Platform | Beverly Hills"
    desc = "Origin Group is a Beverly Hills commercial real estate advisory and investment platform — a trusted partner across transactions, asset advisory, and capital strategy in Southern California and select U.S. markets."
    video_ld = {"@type": "VideoObject", "@id": SITE["domain"] + "/#hero-video", "name": "Beverly Hills aerial — Origin Group",
                "description": "Aerial drone footage over the palm-lined streets of Beverly Hills at golden hour.",
                "thumbnailUrl": SITE["domain"] + "/assets/video/hero-poster.jpg", "uploadDate": "2026-10-30",
                "contentUrl": SITE["domain"] + "/assets/video/hero-1920.mp4", "duration": "PT44S", "publisher": {"@id": ORG_ID}}
    itemlist = {"@type": "ItemList", "name": "Selected Transactions", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "url": f"{SITE['domain']}/experience/{s}"} for i, (s, n, _) in enumerate(HOME_FEATURED)]}
    ld = page_ld("WebPage", SITE["domain"] + "/", title, desc, SITE["domain"] + "/assets/og/home.jpg",
                 [("Home", SITE["domain"] + "/")], extra=[video_ld, itemlist])
    preload = ('<link rel="preload" as="image" href="/assets/video/hero-poster.webp" media="(min-aspect-ratio: 4/5)" fetchpriority="high">'
               '<link rel="preload" as="image" href="/assets/video/hero-poster-portrait.webp" media="(max-aspect-ratio: 4/5)" fetchpriority="high">')

    cards = []
    for i, (slug, name, stem) in enumerate(HOME_FEATURED):
        e = BYSLUG[slug]
        line = e["heads"][1].split(" | ")[0] if len(e["heads"]) > 1 else ""
        desc_line = exp_descriptor(e)
        cards.append(f"""<a class="tx-card" href="/experience/{slug}" data-cursor="View">
        <figure class="tx-card__fig">{img(stem, alt_for(e), sizes="(min-width: 900px) 42vw, 86vw")}</figure>
        <div class="tx-card__meta"><span class="tx-card__num">0{i+1}</span><div><h3 class="h3">{esc(name)}</h3><p>{esc(line)}</p>{f'<p class="tx-card__desc">{esc(desc_line)}</p>' if desc_line else ''}</div></div>
      </a>""")
    cards.append("""<a class="tx-card tx-card--end" href="/experience" data-cursor="View">
        <span class="eyebrow">Experience</span><span class="display tx-card__all">View All<span class="sr-only"> transactions</span></span><span class="tx-card__arrow" aria-hidden="true"></span>
      </a>""")

    caps_imgs = "".join(f'<div class="caps__img{" is-active" if i == 0 else ""}" data-cap-img="{i}">{img(stem, "", sizes="(min-width: 900px) 40vw, 100vw")}</div>'
                        for i, (t, _, stem) in enumerate(HOME_CAPS))
    caps_items = []
    for i, (t, body, stem) in enumerate(HOME_CAPS):
        if t == "Specializations":
            inner = '<ul class="chips">' + "".join(f"<li>{s}</li>" for s in SPECIALIZATIONS) + '</ul>' + f'<p class="sr-only">{esc(body)}</p>'
        else:
            inner = f"<p>{esc(body)}</p>"
        caps_items.append(f"""<li class="cap{" is-active" if i == 0 else ""}" data-cap="{i}">
          <span class="cap__num">0{i+1}</span>
          <div class="cap__body"><h3 class="h2">{esc(t)}</h3><div class="cap__mobile-img">{img(stem, "", sizes="100vw")}</div>{inner}</div>
        </li>""")

    floats = [("250-256-s-la-cienega-blvd-2-baa2a1", "f1", "-0.25"), ("176-nw-25th-st-miami-fl-aerial-29-largehighdefinit-b6241e", "f2", "0.18"),
              ("8327-reseda-blvd-compass-aerial-1c86ec", "f3", "-0.12"), ("2140-el-segundo-blvd-chargers-commons-cc2541", "f4", "0.3")]
    float_html = "".join(f'<figure class="float {c}" data-parallax="{sp}">{img(s, "", sizes="22vw")}</figure>' for s, c, sp in floats)

    strip_items = []
    for e in EXP[:18]:
        a, b = split_title(e["listTitle"])
        strip_items.append(f'<a class="strip__item" href="/experience/{e["slug"]}" data-cursor="View"><figure>{img(exp_thumb(e), "", sizes="(min-width: 900px) 26vw, 64vw")}</figure><span>{esc(a)}</span></a>')
    strip = "".join(strip_items)
    marquee_words = "".join(f'<span class="mq__word">{s}</span><span class="mq__dot" aria-hidden="true"></span>' for s in SPECIALIZATIONS)

    body = f"""
<section class="hero" data-theme="dark" data-hero>
  <div class="hero__media" data-hero-media>
    <video class="hero__video" muted loop playsinline preload="none" poster="/assets/video/hero-poster.webp" data-poster-portrait="/assets/video/hero-poster-portrait.webp" aria-hidden="true" tabindex="-1">
      <source src="/assets/video/hero-portrait-720.mp4" type="video/mp4" media="(max-aspect-ratio: 4/5)">
      <source src="/assets/video/hero-1920.mp4" type="video/mp4">
    </video>
  </div>
  <div class="hero__scrim"></div>
  <div class="container hero__inner" data-hero-content>
    <p class="eyebrow" data-reveal>Origin Group</p>
    <h1 class="display hero__title" data-split>Commercial Real Estate Advisory &amp; Investment Platform</h1>
    <div class="hero__foot">
      <p class="lede" data-reveal style="--d:3">A trusted partner across commercial real estate transactions, advisory, and capital strategy</p>
      <div class="actions" data-reveal style="--d:4">
        <a class="btn btn--gold" href="/capabilities" data-magnetic>View Capabilities</a>
        <a class="btn btn--ghost" href="/about" data-magnetic>Our Approach</a>
      </div>
    </div>
  </div>
  <div class="hero__scroll" aria-hidden="true"><span>Scroll</span><i></i></div>
</section>

<section class="statement" data-theme="light">
  <div class="statement__floats" aria-hidden="true">{float_html}</div>
  <div class="container statement__inner">
    <p class="eyebrow eyebrow--ink" data-reveal>Every Property Has An Origin.</p>
    <p class="statement__text" data-words>Origin Group executes structured real estate investments grounded in disciplined strategy, asset advisory, and long-term performance.</p>
    <a class="link-arrow link-arrow--ink" href="/about" data-reveal>Our Approach<span aria-hidden="true"></span></a>
  </div>
</section>

<div class="mq" data-theme="dark" aria-label="Specializations"><div class="mq__track" data-marquee="1">{marquee_words}{marquee_words}</div></div>

<section class="tx" data-theme="dark" data-hscroll>
  <div class="tx__sticky">
    <div class="container tx__head">
      <div><p class="eyebrow" data-reveal>Experience</p><h2 class="h1" data-split>Selected Transactions</h2></div>
      <a class="link-arrow" href="/experience" data-reveal>View All<span class="sr-only"> transactions</span><span aria-hidden="true"></span></a>
    </div>
    <div class="tx__viewport"><div class="tx__track" data-htrack>{"".join(cards)}</div></div>
    <div class="container"><div class="tx__progress" aria-hidden="true"><span data-hprogress></span></div></div>
  </div>
</section>

<section class="caps" data-theme="light">
  <div class="container caps__head">
    <h2 class="h1" data-split>Capabilities</h2>
    <div class="caps__intro">
      <p class="lede lede--ink" data-reveal>Centered on clarity, discipline, and execution, we structure and execute complex real estate transactions aligned with long-term ownership and value creation.</p>
      <a class="btn btn--ink" href="/capabilities" data-reveal data-magnetic>Learn More<span class="sr-only"> about Origin Group capabilities</span></a>
    </div>
  </div>
  <div class="container caps__split">
    <div class="caps__media"><div class="caps__sticky">{caps_imgs}<div class="caps__frame" aria-hidden="true"></div></div></div>
    <ol class="caps__list">{"".join(caps_items)}</ol>
  </div>
</section>

<section class="strip" data-theme="dark" aria-label="Representative transactions">
  <div class="strip__row"><div class="strip__track" data-marquee="0.6">{strip}{strip}</div></div>
</section>
{cta_band()}
"""
    write("index.html", head(title, desc, path, SITE["domain"] + "/assets/og/home.jpg", ld, preload) + nav_html("/") + body + footer_html())


def build_capabilities():
    path = "/capabilities"; url = SITE["domain"] + path
    title = "Capabilities | Commercial Real Estate Transaction, Asset & Owner-User Advisory | Origin Group"
    desc = "Every property has an origin. Origin Group executes structured real estate investments grounded in disciplined strategy, asset advisory, and long-term performance — transaction advisory, portfolio advisory, owner-user advisory, and market intelligence."
    svc = [{"@type": "Service", "@id": f"{url}#{re.sub(r'[^a-z]+', '-', s['title'].lower()).strip('-')}", "name": s["title"],
            "description": " ".join(s["paras"]), "provider": {"@id": ORG_ID}, "serviceType": s["title"],
            "areaServed": [{"@type": "AdministrativeArea", "name": "Southern California"}, {"@type": "Country", "name": "United States"}],
            "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["title"], "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": a}} for a, _ in s["items"]]}}
           for s in CAP_SERVICES]
    ld = page_ld("WebPage", url, title, desc, abs_img("group-1000006965-57294a"), [("Home", SITE["domain"] + "/"), ("Capabilities", url)], extra=svc)
    blocks = []
    for i, s in enumerate(CAP_SERVICES):
        items = "".join(f'<li data-reveal style="--d:{j}"><span>{esc(a)}</span>{f"<small>{esc(b)}</small>" if b else ""}</li>' for j, (a, b) in enumerate(s["items"]))
        paras = "".join(f'<p data-reveal>{esc(p)}</p>' for p in s["paras"])
        lead = f'<p class="svc__lead" data-reveal>{esc(s["lead"])}</p>' if s["lead"] else ""
        sid = re.sub(r'[^a-z]+', '-', s['title'].lower()).strip('-')
        blocks.append(f"""<article class="svc{' svc--flip' if i % 2 else ''}" id="{sid}">
      <div class="svc__media"><figure class="reveal-img" data-img>{img(s['img'], s['title'], sizes="(min-width: 900px) 46vw, 100vw", extra='data-parallax-inner="0.08"')}</figure><span class="svc__num" data-num="0{i+1}" aria-hidden="true"></span></div>
      <div class="svc__body">
        <p class="eyebrow eyebrow--ink" data-reveal>0{i+1} / 04</p>
        <h2 class="h1" data-split>{esc(s['title'])}</h2>
        {paras}{lead}
        <ul class="svc__list">{items}</ul>
      </div>
    </article>""")
    body = page_hero("group-1000006965-57294a", "Modern glass office towers", "Capabilities", "Every Property Has An Origin.",
                     '<p class="lede phero__lede" data-reveal style="--d:3">Origin Group executes structured real estate investments grounded in disciplined strategy, asset advisory, and long-term performance.</p>')
    body = body.replace('<p class="eyebrow phero__eyebrow" data-reveal>Capabilities</p>', '<h1 class="eyebrow phero__eyebrow" data-reveal>Capabilities</h1>')
    body = body.replace('<h1 class="display" data-split>Every Property Has An Origin.</h1>', '<h2 class="display" data-split>Every Property Has An Origin.</h2>')
    body += f"""<section class="svcs" data-theme="light"><div class="container">{''.join(blocks)}</div></section>
<div class="mq mq--light" aria-label="Specializations"><div class="mq__track" data-marquee="-1">{''.join(f'<span class="mq__word">{s}</span><span class="mq__dot" aria-hidden="true"></span>' for s in SPECIALIZATIONS) * 2}</div></div>
{cta_band()}"""
    write("capabilities.html", head(title, desc, path, SITE["domain"] + "/assets/og/capabilities.jpg", ld, hero_preload("group-1000006965-57294a")) + nav_html(path) + body + footer_html())


def build_experience():
    path = "/experience"; url = SITE["domain"] + path
    title = "Experience | Representative Commercial Real Estate Transactions | Origin Group"
    desc = "Representative commercial real estate transactions, advisory assignments, and capital events by Origin Group — acquisitions, dispositions, and leasing across medical, retail, restaurant, office, industrial, mixed-use and land in Southern California and beyond."
    il = {"@type": "ItemList", "@id": url + "#transactions", "name": "Representative transactions", "numberOfItems": len(EXP),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{url}/{e['slug']}", "name": e["listTitle"],
                               "image": abs_img(exp_thumb(e), 800)} for i, e in enumerate(EXP)]}
    ld = page_ld("CollectionPage", url, title, desc, abs_img("group-1000006967-008256"), [("Home", SITE["domain"] + "/"), ("Experience", url)], extra=[il])
    cards = []
    for i, e in enumerate(EXP):
        a, b = split_title(e["listTitle"])
        cards.append(f"""<a class="xcard" href="/experience/{e['slug']}" data-cursor="View" data-reveal style="--d:{i % 3}">
      <figure class="xcard__fig">{img(exp_thumb(e), alt_for(e), sizes="(min-width: 1100px) 31vw, (min-width: 700px) 46vw, 92vw")}</figure>
      <div class="xcard__meta"><span class="xcard__num">{i+1:02d}</span><h2 class="xcard__title">{esc(a)}</h2>{f'<p>{esc(b)}</p>' if b else ''}</div>
    </a>""")
    sub = f"""<h2 class="lede phero__lede" data-reveal style="--d:3">Representative commercial real estate transactions, advisory assignments, and capital events.</h2>
    <div class="phero__row" data-reveal style="--d:4"><p class="phero__tags">Acquisitions · Dispositions · Leasing</p><a class="btn btn--gold" href="/contactus" data-magnetic>Discuss an Opportunity</a></div>"""
    body = page_hero("group-1000006967-008256", "Looking up at a Los Angeles office tower at dusk", "Origin Group", "Experience", sub)
    body += f"""<section class="xgrid-wrap" data-theme="light"><div class="container"><div class="xgrid">{''.join(cards)}</div></div></section>
{cta_band(button="Discuss an Opportunity")}"""
    write("experience.html", head(title, desc, path, SITE["domain"] + "/assets/og/experience.jpg", ld, hero_preload("group-1000006967-008256")) + nav_html(path) + body + footer_html())


def build_projects():
    for i, e in enumerate(EXP):
        slug = e["slug"]; path = f"/experience/{slug}"; url = SITE["domain"] + path
        heads = e["heads"]
        h1 = heads[0]
        rest = heads[1:]
        # Bella Terra style stat pairs ("850,000 SF" + "RETAIL")
        stats, lines = [], []
        j = 0
        while j < len(rest):
            h = rest[j]
            if re.match(r"^[\d,±.]+\s*(SF|UNITS|AC)\b", h) and j + 1 < len(rest) and rest[j + 1].isupper() and len(rest[j + 1]) < 20:
                stats.append((h, rest[j + 1])); j += 2; continue
            if re.match(r"^[\d,±.]+\s*(SF|UNITS|AC)\b", h):
                stats.append((h, "")); j += 1; continue
            lines.append(h); j += 1
        desc_line = exp_descriptor(e)
        locality = exp_locality(e)
        street = exp_street(e)
        nm = exp_name(e)
        title = f"{nm} | {desc_line + ' | ' if desc_line and len(nm) + len(desc_line) < 72 else ''}Origin Group"
        desc = nm + (f" — {desc_line}." if desc_line else ".") + \
               " A representative commercial real estate transaction by Origin Group, a Beverly Hills advisory and investment platform."
        hero = exp_hero(e)
        gallery = e["images"][1:]
        place = {"@type": "Place", "@id": url + "#property", "name": nm,
                 "description": desc_line or None,
                 "address": {"@type": "PostalAddress", "streetAddress": street or None, "addressLocality": locality or None,
                             "addressRegion": exp_region(e), "addressCountry": "US"},
                 "image": [abs_img(s, 1600) for s in e["images"][:6]]}
        place["address"] = {k: v for k, v in place["address"].items() if v}
        place = {k: v for k, v in place.items() if v}
        ld = page_ld("WebPage", url, title, desc, abs_img(hero), [("Home", SITE["domain"] + "/"), ("Experience", SITE["domain"] + "/experience"), (e["listTitle"], url)],
                     extra=[place], about={"@id": url + "#property"})
        prev_e = EXP[i - 1]; next_e = EXP[(i + 1) % len(EXP)]
        lines_html = "".join(f'<p class="proj__line" data-reveal style="--d:{k+2}">{esc(l)}</p>' for k, l in enumerate(lines))
        stats_html = ("<div class=\"proj__stats\" data-reveal style=\"--d:4\">" + "".join(f'<div><strong>{esc(a)}</strong>{f"<span>{esc(b)}</span>" if b else ""}</div>' for a, b in stats) + "</div>") if stats else ""
        gal = []
        for k, s in enumerate(gallery):
            m = META[s]; wide = (k % 5 == 0) or (m["w"] / m["h"] > 2.1)
            gal.append(f'<a class="gal__item{" gal__item--wide" if wide else ""}" href="{src(s, 1600)}" data-lightbox data-cursor="Expand" data-reveal style="--d:{k % 2}">{img(s, alt_for(e, k + 2), sizes="(min-width: 900px) " + ("92vw" if wide else "46vw") + ", 100vw")}</a>')
        if 2400 in META[hero]["sizes"]: USED.add(f"{hero}-2400.webp")
        gallery_html = f'<section class="gal" data-theme="light" aria-label="Gallery"><div class="container"><div class="gal__grid" data-gallery>{"".join(gal)}</div></div></section>' if gal else ""
        pa, pb = split_title(prev_e["listTitle"]); na, nb = split_title(next_e["listTitle"])
        body = f"""<section class="proj-hero" data-theme="dark" data-hero>
  <a class="proj-hero__media" href="{src(hero, 1600)}" data-lightbox data-hero-media data-cursor="Expand" aria-label="Open photo">{img(hero, alt_for(e), sizes="100vw", eager=True, hero=True)}</a>
  <div class="phero__scrim"></div>
  <div class="container proj-hero__inner">
    <nav class="crumbs" aria-label="Breadcrumb" data-reveal><a href="/experience">Experience</a><span aria-hidden="true">/</span><span aria-current="page">{esc(split_title(e['listTitle'])[0])}</span></nav>
    <h1 class="display proj__title" data-split>{esc(h1)}</h1>
    {lines_html}{stats_html}
  </div>
</section>
{gallery_html}
<nav class="pager" aria-label="More transactions" data-theme="dark">
  <a class="pager__link" href="/experience/{prev_e['slug']}" data-cursor="Prev"><figure>{img(exp_thumb(prev_e), alt_for(prev_e), sizes="50vw")}</figure><span class="eyebrow">Previous</span><span class="h2">{esc(pa)}</span>{f'<small>{esc(pb)}</small>' if pb else ''}</a>
  <a class="pager__link pager__link--next" href="/experience/{next_e['slug']}" data-cursor="Next"><figure>{img(exp_thumb(next_e), alt_for(next_e), sizes="50vw")}</figure><span class="eyebrow">Next</span><span class="h2">{esc(na)}</span>{f'<small>{esc(nb)}</small>' if nb else ''}</a>
</nav>
{cta_band(title="Discuss an Opportunity", label="Experience", button="Connect With Us")}"""
        og = SITE["domain"] + f"/assets/og/x-{slug}.jpg"
        write(f"experience/{slug}.html", head(title, desc, path, og, ld, hero_preload(hero)) + nav_html("/experience") + body + footer_html())


def build_team():
    path = "/team"; url = SITE["domain"] + path
    title = "Team | Oliver Ghadoushi, Founder & Principal | Origin Group Commercial Real Estate"
    desc = "Meet the Origin Group team — Oliver Ghadoushi, Founder & Principal, with Associates Anthony Assatourian and Jonah Kharrazi. Commercial real estate advisory and investment across Southern California and select U.S. markets."
    ld = page_ld("AboutPage", url, title, desc, abs_img(TEAM[0]["img"], 800), [("Home", SITE["domain"] + "/"), ("Team", url)])
    members = []
    for i, p in enumerate(TEAM):
        bio = "".join(f'<p data-reveal>{esc(b)}</p>' for b in p["bio"])
        members.append(f"""<article class="member{' member--flip' if i % 2 else ''}" id="{p['id']}">
      <div class="member__media"><div class="member__sticky"><figure class="reveal-img" data-img>{img(p['img'], p['name'] + ', ' + p['role'] + ', Origin Group', sizes="(min-width: 900px) 38vw, 100vw", eager=(i == 0))}</figure></div></div>
      <div class="member__body">
        <p class="eyebrow eyebrow--ink" data-reveal>{esc(p['role'])}</p>
        <h2 class="display member__name" data-split>{esc(p['name'])}</h2>
        <div class="member__bio">{bio}</div>
      </div>
    </article>""")
    body = f"""<section class="thero" data-theme="dark" data-hero>
  <div class="container thero__inner">
    <p class="eyebrow" data-reveal>Origin Group</p>
    <h1 class="display thero__title" data-split>Team</h1>
    <ul class="thero__names" data-reveal style="--d:3">{''.join(f'<li><a href="#{p["id"]}">{esc(p["name"])}<small>{esc(p["role"])}</small></a></li>' for p in TEAM)}</ul>
  </div>
</section>
<section class="members" data-theme="light"><div class="container">{''.join(members)}</div></section>
{cta_band(title="Contact Us", label="Origin Group", img_stem="1--14-2a0f39", button="Connect With Us")}"""
    write("team.html", head(title, desc, path, SITE["domain"] + "/assets/og/team.jpg", ld) + nav_html(path) + body + footer_html())


def build_about():
    path = "/about"; url = SITE["domain"] + path
    title = "About Origin Group | Advisory-Led Commercial Real Estate Firm in Beverly Hills"
    desc = "Origin Group was founded on a simple belief: the best outcomes are created at the beginning. An advisory-led commercial real estate firm blending institutional rigor with boutique-level attention."
    faq = {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    ld = page_ld("AboutPage", url, title, desc, abs_img("banner-1--1-1e0848"), [("Home", SITE["domain"] + "/"), ("About", url)], extra=[faq])
    principles = "".join(f'<li class="pr" data-reveal style="--d:{i}"><span class="pr__num">0{i+1}</span><span class="pr__text">{esc(p)}</span></li>' for i, p in enumerate(PRINCIPLES))
    wwd = "".join(f'<li data-reveal style="--d:{i}">{esc(w)}</li>' for i, w in enumerate(WHAT_WE_DO))
    faqs = "".join(f'<details class="faq__item" data-reveal><summary><span>{esc(q)}</span><i aria-hidden="true"></i></summary><div class="faq__a"><p>{esc(a)}</p></div></details>' for q, a in FAQ)
    body = page_hero("banner-1--1-1e0848", "Glass office towers in a blue haze", "Origin Group", "About Us")
    body += f"""
<section class="intro" data-theme="light">
  <div class="container intro__inner">
    <p class="statement__text statement__text--sm" data-words>{esc(ABOUT_INTRO[0])}</p>
    <p class="intro__p" data-reveal>{esc(ABOUT_INTRO[1])}</p>
  </div>
</section>

<section class="split" data-theme="light">
  <div class="container split__grid">
    <div class="split__media"><figure class="reveal-img" data-img>{img("621801468-e6f373", "Commercial office building facade", sizes="(min-width: 900px) 44vw, 100vw", extra='data-parallax-inner="0.08"')}</figure></div>
    <div class="split__body">
      <p class="eyebrow eyebrow--ink" data-reveal>01</p>
      <h2 class="h1" data-split>Our Approach</h2>
      <p data-reveal>Unlike traditional models driven by volume, Origin Group is advisory-led. Every engagement begins with understanding the project’s broader objectives – financial, operational, and strategic – before determining the most optimal path.</p>
      <p data-reveal>We work selectively and deliberately, ensuring that each assignment receives senior-level involvement, market intelligence, and thoughtful execution.</p>
      <p class="svc__lead" data-reveal>Key principles that guide our work:</p>
    </div>
  </div>
  <div class="container"><ol class="principles">{principles}</ol></div>
</section>

<section class="split split--dark" data-theme="dark">
  <div class="container split__grid split__grid--flip">
    <div class="split__media"><figure class="reveal-img" data-img>{img("1552141787-c3901e", "Downtown commercial real estate skyline", sizes="(min-width: 900px) 44vw, 100vw", extra='data-parallax-inner="0.08"')}</figure></div>
    <div class="split__body">
      <p class="eyebrow" data-reveal>02</p>
      <h2 class="h1" data-split>What We Do</h2>
      <p data-reveal>Origin Group provides a range of advisory services, including:</p>
      <ul class="svc__list svc__list--light">{wwd}</ul>
      <p data-reveal>Our experience spans retail, restaurant, medical, industrial, office, land, and mixed-use assets, with a particular strength in transactions where structure, timing, and strategy materially impact outcomes.</p>
    </div>
  </div>
</section>

<section class="split" data-theme="light">
  <div class="container split__grid">
    <div class="split__media"><figure class="reveal-img" data-img>{img("photo-3-baf6cb", "Office tower exterior", sizes="(min-width: 900px) 44vw, 100vw", extra='data-parallax-inner="0.08"')}</figure></div>
    <div class="split__body">
      <p class="eyebrow eyebrow--ink" data-reveal>03</p>
      <h2 class="h1" data-split>Who We Work With</h2>
      <p data-reveal>Origin Group works alongside private and institutional investors, family offices, owner-operators, and regional and national operating businesses. Our work is relationship-based and defined by confidentiality, trust, and consistent execution.</p>
      <p data-reveal>Our clients value discretion, informed guidance, and a clear process – especially in situations involving complexity, urgency, or long-term planning.</p>
    </div>
  </div>
</section>

<section class="why" data-theme="dark">
  <div class="why__media" data-parallax="-0.15">{img("645469389-a1b4d1", "City skyline", sizes="100vw")}</div>
  <div class="why__scrim"></div>
  <div class="container why__inner">
    <p class="eyebrow" data-reveal>04</p>
    <h2 class="display" data-split>Why Origin Group</h2>
    <p class="why__text" data-reveal style="--d:2">The name Origin reflects our philosophy: value is created at the point of origin. By combining market expertise, disciplined process, and a relationship-driven mindset, we deliver outcomes that are thoughtful, defensible, and aligned with our partners’ broader goals.</p>
  </div>
</section>

<section class="faq" data-theme="light" id="faq">
  <div class="container faq__grid">
    <div><p class="eyebrow eyebrow--ink" data-reveal>Origin Group</p><h2 class="h1" data-split>Questions</h2></div>
    <div class="faq__list">{faqs}</div>
  </div>
</section>
{cta_band()}"""
    write("about.html", head(title, desc, path, SITE["domain"] + "/assets/og/about.jpg", ld, hero_preload("banner-1--1-1e0848")) + nav_html(path) + body + footer_html())


def build_contact():
    path = "/contactus"; url = SITE["domain"] + path
    title = "Contact Origin Group | 9454 Wilshire Blvd, Beverly Hills | +1 (323) 410-2650"
    desc = "Connect with Origin Group — commercial real estate advisory and investment. Main offices at 9454 Wilshire Blvd, Beverly Hills, CA 90212. Call +1 (323) 410-2650 or email info@origingroupre.com."
    ld = page_ld("ContactPage", url, title, desc, abs_img("1--14-a56765"), [("Home", SITE["domain"] + "/"), ("Contact", url)])
    body = f"""<section class="contact" data-theme="dark" data-hero>
  <div class="contact__media" data-hero-media>{img("1--14-a56765", "Aerial view of downtown Los Angeles at dusk", sizes="100vw", eager=True, hero=True)}</div>
  <div class="contact__scrim"></div>
  <div class="container contact__grid">
    <div class="contact__info">
      <p class="eyebrow" data-reveal>Contact</p>
      <h1 class="display" data-split>Connect With Us</h1>
      <div class="contact__details" data-reveal style="--d:3">
        <div><p class="eyebrow">Main Offices</p><address><a href="{SITE['maps']}" rel="noopener" target="_blank">{SITE['street']}<br>{SITE['city']}, {SITE['region']} {SITE['zip']}</a></address></div>
        <div><p class="eyebrow">Phone</p><p><a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a></p></div>
        <div><p class="eyebrow">Email</p><p><a href="mailto:{SITE['email']}">{SITE['email']}</a></p></div>
      </div>
    </div>
    <form class="cform" data-form data-kind="contact" novalidate data-reveal style="--d:2">
      <fieldset class="cform__row">
        <legend class="cform__legend">Name <span>(required)</span></legend>
        <label><span>First Name</span><input name="first_name" autocomplete="given-name" required></label>
        <label><span>Last Name</span><input name="last_name" autocomplete="family-name" required></label>
      </fieldset>
      <label><span>Email <em>(required)</em></span><input type="email" name="email" autocomplete="email" required></label>
      <label><span>Subject <em>(required)</em></span><input name="subject" required></label>
      <label><span>Message <em>(required)</em></span><textarea name="message" rows="5" required></textarea></label>
      <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
      <button class="btn btn--gold cform__submit" type="submit" data-magnetic>Submit</button>
      <p class="form__ok" role="status" hidden>Thank you, We’ll be in touch!</p>
      <p class="form__err" role="alert" hidden></p>
    </form>
  </div>
</section>
<section class="map" data-theme="dark" aria-label="Map to Origin Group">
  <iframe title="Map: 9454 Wilshire Blvd, Beverly Hills, CA 90212" src="https://www.google.com/maps?q=9454+Wilshire+Blvd,+Beverly+Hills,+CA+90212&amp;z=15&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</section>"""
    write("contactus.html", head(title, desc, path, SITE["domain"] + "/assets/og/contact.jpg", ld, hero_preload("1--14-a56765")) + nav_html(path) + body + footer_html())


def build_404():
    title = "Page not found | Origin Group"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [org_ld(), website_ld()]}, separators=(",", ":"))
    body = f"""<section class="thero thero--404" data-theme="dark" data-hero>
  <div class="container thero__inner">
    <p class="eyebrow" data-reveal>404</p>
    <h1 class="display thero__title" data-split>Page not found</h1>
    <div class="actions" data-reveal style="--d:3"><a class="btn btn--gold" href="/">Home</a><a class="btn btn--ghost" href="/experience">Experience</a></div>
  </div>
</section>"""
    write("404.html", head(title, "The page you were looking for has moved.", "/404", SITE["domain"] + "/assets/og/home.jpg", ld, robots="noindex, follow") + nav_html("") + body + footer_html())

# ---------------------------------------------------------------- SEO / AI files
def build_seo_files():
    urls = [("/", "1.0", ["city-buildings-with-sunset-reflection-c0310e"]), ("/capabilities", "0.9", [s["img"] for s in CAP_SERVICES]),
            ("/experience", "0.9", [exp_thumb(e) for e in EXP]), ("/team", "0.8", [p["img"] for p in TEAM]),
            ("/about", "0.8", ["banner-1--1-1e0848", "621801468-e6f373", "1552141787-c3901e"]), ("/contactus", "0.8", ["1--14-a56765"])]
    for e in EXP: urls.append((f"/experience/{e['slug']}", "0.6", e["images"]))
    parts = []
    for u, pr, imgs in urls:
        im = "".join(f"<image:image><image:loc>{abs_img(s)}</image:loc></image:image>" for s in imgs[:30])
        vid = ""
        if u == "/":
            vid = ("<video:video><video:thumbnail_loc>{d}/assets/video/hero-poster.jpg</video:thumbnail_loc>"
                   "<video:title>Beverly Hills aerial — Origin Group</video:title>"
                   "<video:description>Aerial drone footage over the palm-lined streets of Beverly Hills at golden hour.</video:description>"
                   "<video:content_loc>{d}/assets/video/hero-1920.mp4</video:content_loc><video:duration>44</video:duration></video:video>").format(d=SITE["domain"])
        parts.append(f"<url><loc>{SITE['domain']}{u}</loc><lastmod>{TODAY}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority>{im}{vid}</url>")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">\n'
          + "\n".join(parts) + "\n</urlset>\n")

    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
            "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot", "Applebot", "Applebot-Extended",
            "Amazonbot", "meta-externalagent", "DuckAssistBot", "MistralAI-User", "YouBot", "CCBot"]
    robots = "# Origin Group — search engines and AI assistants are welcome.\n\n" + \
             "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + \
             "User-agent: *\nAllow: /\nDisallow: /data/\nDisallow: /build.py\n\n" + f"Sitemap: {SITE['domain']}/sitemap.xml\n"
    write("robots.txt", robots)

    # llms.txt — concise, link-first summary for AI assistants (llmstxt.org)
    tx = "\n".join(f"- [{e['listTitle']}]({SITE['domain']}/experience/{e['slug']})" + (f": {exp_descriptor(e)}" if exp_descriptor(e) else "") for e in EXP)
    llms = f"""# Origin Group

> Origin Group is a commercial real estate advisory and investment platform headquartered at 9454 Wilshire Blvd, Beverly Hills, CA 90212. A trusted partner across commercial real estate transactions, advisory, and capital strategy, serving Southern California with select advisory and investment activity across major U.S. markets.

Key facts:
- Founder & Principal: Oliver Ghadoushi. Associates: Anthony Assatourian, Jonah Kharrazi.
- Phone: {SITE['phone_display']} · Email: {SITE['email']} · Web: {SITE['domain']}
- Specializations: {', '.join(SPECIALIZATIONS)}.
- Core work: acquisitions, dispositions, investment sales, leasing, landlord and tenant advisory, owner-user transactions, sale-leasebacks, 1031 exchanges, capital markets, SBA strategies, hold vs. sell analysis, asset repositioning, valuation and underwriting, confidential and off-market processes.
- Clients: private investors, high-net-worth individuals, family offices, private equity firms, institutional capital, and regional and national operating companies.
- Approach: advisory-led, not volume-driven. Principles: Strategy before execution; Alignment over speed; Clarity over complexity; Long-term relationship.

## Pages
- [Home]({SITE['domain']}/): Overview, selected transactions, and capabilities.
- [Capabilities]({SITE['domain']}/capabilities): Transaction Advisory & Execution; Asset-Level & Portfolio Advisory; Owner-User & Operating Company Advisory; Market Intelligence & Underwriting.
- [Experience]({SITE['domain']}/experience): {len(EXP)} representative transactions, advisory assignments, and capital events.
- [Team]({SITE['domain']}/team): Oliver Ghadoushi, Anthony Assatourian, Jonah Kharrazi.
- [About]({SITE['domain']}/about): Founding philosophy, approach, services, clients, and FAQ.
- [Contact]({SITE['domain']}/contactus): Office address, phone, email, and inquiry form.
- [Full text for AI assistants]({SITE['domain']}/llms-full.txt)

## Representative transactions
{tx}
"""
    write("llms.txt", llms)

    full = [f"# Origin Group — full site text\n\nSource: {SITE['domain']} · Updated {TODAY}\n",
            "## Home\n\n### Commercial Real Estate Advisory & Investment Platform\nA trusted partner across commercial real estate transactions, advisory, and capital strategy\n",
            "### Capabilities\nCentered on clarity, discipline, and execution, we structure and execute complex real estate transactions aligned with long-term ownership and value creation.\n"
            + "\n".join(f"- **{t}** — {b}" for t, b, _ in HOME_CAPS),
            "\n## Capabilities\n\n### Every Property Has An Origin.\nOrigin Group executes structured real estate investments grounded in disciplined strategy, asset advisory, and long-term performance.\n"]
    for s in CAP_SERVICES:
        full.append(f"### {s['title']}\n" + "\n\n".join(s["paras"]) + ("\n\n" + s["lead"] if s["lead"] else "") + "\n" +
                    "\n".join(f"- {a}" + (f" ({b})" if b else "") for a, b in s["items"]) + "\n")
    full.append("## About\n\n" + "\n\n".join(ABOUT_INTRO) + "\n\n### Our Approach\nUnlike traditional models driven by volume, Origin Group is advisory-led. Every engagement begins with understanding the project’s broader objectives – financial, operational, and strategic – before determining the most optimal path.\n\nWe work selectively and deliberately, ensuring that each assignment receives senior-level involvement, market intelligence, and thoughtful execution.\n\nKey principles that guide our work:\n"
                + "\n".join(f"{i+1}. {p}" for i, p in enumerate(PRINCIPLES))
                + "\n\n### What We Do\nOrigin Group provides a range of advisory services, including:\n" + "\n".join(f"- {w}" for w in WHAT_WE_DO)
                + "\n\nOur experience spans retail, restaurant, medical, industrial, office, land, and mixed-use assets, with a particular strength in transactions where structure, timing, and strategy materially impact outcomes.\n\n### Who We Work With\nOrigin Group works alongside private and institutional investors, family offices, owner-operators, and regional and national operating businesses. Our work is relationship-based and defined by confidentiality, trust, and consistent execution.\n\nOur clients value discretion, informed guidance, and a clear process – especially in situations involving complexity, urgency, or long-term planning.\n\n### Why Origin Group\nThe name Origin reflects our philosophy: value is created at the point of origin. By combining market expertise, disciplined process, and a relationship-driven mindset, we deliver outcomes that are thoughtful, defensible, and aligned with our partners’ broader goals.\n")
    full.append("## Team\n\n" + "\n\n".join(f"### {p['name']} — {p['role']}\n" + "\n\n".join(p["bio"]) for p in TEAM) + "\n")
    full.append("## Frequently asked questions\n\n" + "\n\n".join(f"**{q}**\n{a}" for q, a in FAQ) + "\n")
    full.append("## Experience — representative transactions\n\n" + "\n".join(f"- {' — '.join(e['heads'])} ({SITE['domain']}/experience/{e['slug']})" for e in EXP) + "\n")
    full.append(f"## Contact\n\nMain offices: {SITE['street']}, {SITE['city']}, {SITE['region']} {SITE['zip']}\nPhone: {SITE['phone_display']}\nEmail: {SITE['email']}\n")
    write("llms-full.txt", "\n".join(full))

    write("site.webmanifest", json.dumps({"name": "Origin Group", "short_name": "Origin Group", "start_url": "/", "display": "standalone",
                                          "background_color": "#0E2A35", "theme_color": "#0E2A35",
                                          "icons": [{"src": "/assets/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
                                                    {"src": "/assets/brand/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1))

    redirects = [("/home", "/"), ("/new-page", "/"), ("/cart", "/"), ("/contact", "/contactus"), ("/contact-us", "/contactus"),
                 ("/store-1", "/experience"), ("/store-1/*", "/experience"), ("/index.html", "/")]
    write("_redirects", "\n".join(f"{a} {b} 301" for a, b in redirects) + "\n")
    write("_headers", """/assets/*
  Cache-Control: public, max-age=31536000, immutable
/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  X-Frame-Options: SAMEORIGIN
/llms.txt
  Content-Type: text/markdown; charset=utf-8
/llms-full.txt
  Content-Type: text/markdown; charset=utf-8
""")
    write("vercel.json", json.dumps({"cleanUrls": True, "trailingSlash": False,
        "redirects": [{"source": a.replace("/*", "/:path*"), "destination": b, "permanent": True} for a, b in redirects if a != "/index.html"],
        "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}]}, indent=1))

def build_og():
    from PIL import Image, ImageDraw, ImageFilter
    outdir = ROOT / "assets/og"; outdir.mkdir(parents=True, exist_ok=True)
    logo = Image.open(ROOT / "assets/brand/logo-white.png").convert("RGBA")
    def make(stem_or_path, name, is_path=False):
        out = outdir / f"{name}.jpg"
        if out.exists(): return
        p = stem_or_path if is_path else ROOT / f"assets/img/{stem_or_path}-1600.webp"
        if not Path(p).exists(): p = ROOT / f"assets/img/{stem_or_path}-800.webp"
        im = Image.open(p).convert("RGB")
        W, H = 1200, 630; r = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
        im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
        grad = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(grad)
        for y in range(H):
            a = int(60 + 150 * (y / H) ** 1.4); d.line([(0, y), (W, y)], fill=(14, 42, 53, a))
        im = Image.alpha_composite(im.convert("RGBA"), grad)
        lg = logo.copy(); lg.thumbnail((360, 200))
        im.alpha_composite(lg, (72, H - lg.height - 64))
        d = ImageDraw.Draw(im); d.line([(72, H - lg.height - 92), (152, H - lg.height - 92)], fill=(197, 164, 109, 255), width=2)
        im.convert("RGB").save(out, "JPEG", quality=82, optimize=True)
    make(ROOT / "assets/video/hero-poster.jpg" if (ROOT / "assets/video/hero-poster.jpg").exists() else ROOT / "assets/img/city-buildings-with-sunset-reflection-c0310e-1600.webp", "home", True)
    make("group-1000006965-57294a", "capabilities"); make("group-1000006967-008256", "experience")
    make("main-oliver-ghadoushi-headshot-2f55a3", "team"); make("banner-1--1-1e0848", "about"); make("1--14-a56765", "contact")
    for e in EXP: make(exp_hero(e), f"x-{e['slug']}")

def prune_images():
    d = ROOT / "assets/img"; removed = 0
    for f in d.iterdir():
        if f.suffix == ".webp" and f.name not in USED:
            # keep 800/1600 of anything referenced in data (cheap), drop unused 2400s and orphans
            f.unlink(); removed += 1
    return removed

if __name__ == "__main__":
    CSS_V = asset_v("/assets/css/site.css"); JS_V = asset_v("/assets/js/site.js")
    build_home(); build_capabilities(); build_experience(); build_projects()
    build_team(); build_about(); build_contact(); build_404()
    build_seo_files(); build_og()
    n = prune_images() if os.environ.get("PRUNE") else 0
    print(f"built {7 + len(EXP)} pages · {len(USED)} image files referenced · pruned {n}")
