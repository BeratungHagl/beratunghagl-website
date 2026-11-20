"""Blog-Generator für andreas-hagl.de (statisch, ohne Build-Step auf Vercel).

Quellen:  _blog/posts/<slug>.html  (Kopfblock zwischen '---' + HTML-Body)
Ausgabe:  blog/index.html, blog/<slug>/index.html, blog/feed.xml
          + Blöcke zwischen Markern in index.html, sitemap.xml, llms.txt

Aufruf (im Repo-Root):  python _blog/build.py
Header/Navigation und Footer werden aus der Startseite übernommen, damit sie
mit dem Rest der Website synchron bleiben.

Pflichtfelder im Kopfblock: title, date (JJJJ-MM-TT), category, description, lead, excerpt
Optional: seo_title, updated, keywords, cta_title, cta_text, cta2_label, cta2_href,
          ai_note, source, draft (true = wird nicht veröffentlicht)
"""
import html
import json
import pathlib
import re
import sys
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://andreas-hagl.de"
BRAND = "Beratungsunternehmen Hagl"
CALENDLY = "https://calendly.com/kontakt-hagl/30min"
NEWSLETTER = ("https://bcddc0ee.sibforms.com/serve/MUIFAPcH7exu8aU8ls_9ZJm-FEe68nXHUpYhcO5Sp0cz2Yuj"
              "WTvj_kFJHqgXh_1-TQRT14tX7_QLu9XeqaPcqYtR97N8faxCxA8S4IIs67sO4vCPY_L-39jSnXB1yYNE3w_"
              "HZZUN9KIC5eb-jv9zZCZwbeOk2lra9nQe67WjjTc0_NJfuDalHrRZh2-1fOX97oNAGfwEuhgjQHAz")
OG_IMAGE = f"{SITE}/assets/og-cover.jpg"
BLOG_TITLE = "Blog"
BLOG_H1 = "Impulse für den Mittelstand"
BLOG_LEAD = ("Praxisberichte und Gedanken zu Strategie, Organisation, KI und Förderung — aus der "
             "Beratung von Unternehmen mit 10 bis 100 Mitarbeitern und aus dem eigenen Haus.")
BLOG_DESC = ("Blog von Andreas Hagl: Praxisberichte und Impulse zu Strategie, Organisation, KI, "
             "Digitalisierung und Förderung für kleine und mittlere Unternehmen.")
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]

ORG_PERSON = [
    {
        "@type": "ProfessionalService",
        "@id": f"{SITE}/#organization",
        "name": BRAND,
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/logo-mark.png",
        "telephone": "+49 170 4792475",
        "email": "kontakt@beratung-hagl.de",
        "address": {"@type": "PostalAddress", "streetAddress": "Schulstr. 15", "postalCode": "84104",
                    "addressLocality": "Rudelzhausen", "addressRegion": "Bayern", "addressCountry": "DE"},
        "founder": {"@id": f"{SITE}/#person"},
        "sameAs": ["https://www.linkedin.com/company/beratungsunternehmen-hagl/",
                   "https://www.facebook.com/BeratungHagl",
                   "https://www.alchimedus.de/beraterstandorte/beratungsunternehmen-hagl-2/"],
    },
    {
        "@type": "Person",
        "@id": f"{SITE}/#person",
        "name": "Andreas Hagl",
        "jobTitle": "Strategieberater und Wirkungs-Architekt",
        "image": f"{SITE}/assets/andreas-hagl.jpg",
        "url": f"{SITE}/#ueber-mich",
        "worksFor": {"@id": f"{SITE}/#organization"},
        "memberOf": {"@type": "Organization", "name": "Alchimedus® consulting network"},
        "sameAs": ["https://de.linkedin.com/in/andreas-hagl"],
    },
]

e = lambda s: html.escape(s, quote=True)


# ---------------------------------------------------------------- Einlesen
def parse_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n(.*)", raw, re.S)
    if not m:
        sys.exit(f"Kopfblock fehlt: {path.name}")
    meta = {}
    for line in m.group(1).splitlines():
        if line.strip():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for req in ("title", "date", "category", "description", "lead", "excerpt"):
        if not meta.get(req):
            sys.exit(f"{path.name}: Feld '{req}' fehlt")
    meta["slug"] = path.stem
    meta["body"] = m.group(2).strip()
    meta["date_obj"] = date.fromisoformat(meta["date"])
    meta["updated"] = meta.get("updated") or meta["date"]
    meta["url"] = f"{SITE}/blog/{meta['slug']}"
    text = re.sub(r"<[^>]+>", " ", meta["body"])
    meta["words"] = len(text.split())
    meta["minutes"] = max(1, round(meta["words"] / 200))
    if len(meta["description"]) > 160:
        print(f"Hinweis: description von {meta['slug']} hat {len(meta['description'])} Zeichen (>160)")
    return meta


def de_datum(d):
    return f"{d.day}. {MONATE[d.month - 1]} {d.year}"


# ---------------------------------------------------------------- Bausteine
def site_chrome():
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    nav = re.search(r'<nav class="nav">.*?</nav>', home, re.S).group(0)
    footer = re.search(r"<footer>.*?</footer>", home, re.S).group(0)
    nav = nav.replace('<a href="/blog">Blog</a>', '<a href="/blog" aria-current="page">Blog</a>')
    return nav, footer


def head(title, desc, canonical, og_type, graph, extra=""):
    t = e(title)
    d = e(desc)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{t}</title>
<meta name="description" content="{d}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="{og_type}" />
<meta property="og:title" content="{t}" />
<meta property="og:description" content="{d}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:locale" content="de_DE" />
<meta property="og:site_name" content="{BRAND}" />
<meta property="og:image" content="{OG_IMAGE}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
{extra}<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{t}" />
<meta name="twitter:description" content="{d}" />
<meta name="twitter:image" content="{OG_IMAGE}" />
<link rel="icon" type="image/png" href="/assets/logo-mark.png" />
<link rel="alternate" type="application/rss+xml" title="{BRAND} — Blog" href="{SITE}/blog/feed.xml" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" media="print" onload="this.media='all'" />
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" /></noscript>
<link rel="stylesheet" href="/assets/styles.css" />
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip-link" href="#main">Zum Inhalt springen</a>
"""


def tail(footer):
    return f"""
{footer}

<script src="/assets/nav.js"></script>
<script src="/assets/consent.js"></script>
</body>
</html>
"""


def post_card(p, heading="h3"):
    return f"""        <a class="post-card" href="/blog/{p['slug']}">
          <p class="post-card__meta"><span class="post-card__cat">{e(p['category'])}</span> · <time datetime="{p['date']}">{de_datum(p['date_obj'])}</time> · {p['minutes']} Min. Lesezeit</p>
          <{heading}>{e(p['title'])}</{heading}>
          <p>{e(p['excerpt'])}</p>
          <span class="go">Weiterlesen →</span>
        </a>"""


AUTHOR_BOX = """      <aside class="author-box" aria-label="Über den Autor">
        <img src="/assets/andreas-hagl.jpg" width="600" height="750" loading="lazy" decoding="async" alt="Andreas Hagl" />
        <div>
          <p class="author-box__name">Andreas Hagl</p>
          <p>Andreas Hagl ist Unternehmensberater und Wirkungs-Architekt mit Schwerpunkt auf Strategie
            und Organisationsentwicklung im deutschen Mittelstand. Er begleitet Unternehmen dabei,
            Klarheit, Struktur und Steuerungsfähigkeit zu entwickeln — von der Potenzialanalyse bis zur
            konkreten Umsetzung. <a href="/#ueber-mich">Mehr über Andreas Hagl</a></p>
        </div>
      </aside>"""


# ---------------------------------------------------------------- Seiten
def render_post(p, posts, nav, footer):
    seo_title = f"{p.get('seo_title') or p['title']} | {BRAND}"
    graph = ORG_PERSON + [
        {
            "@type": "BlogPosting",
            "@id": f"{p['url']}#article",
            "headline": p["title"][:110],
            "description": p["description"],
            "datePublished": p["date"],
            "dateModified": p["updated"],
            "inLanguage": "de",
            "articleSection": p["category"],
            "wordCount": p["words"],
            "author": {"@id": f"{SITE}/#person"},
            "publisher": {"@id": f"{SITE}/#organization"},
            "image": OG_IMAGE,
            "mainEntityOfPage": p["url"],
            "isPartOf": {"@id": f"{SITE}/blog#blog"},
            **({"keywords": p["keywords"]} if p.get("keywords") else {}),
            **({"citation": p["source"]} if p.get("source") else {}),
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog"},
                {"@type": "ListItem", "position": 3, "name": p.get("seo_title") or p["title"], "item": p["url"]},
            ],
        },
    ]
    extra = (f'<meta property="article:published_time" content="{p["date"]}" />\n'
             f'<meta property="article:modified_time" content="{p["updated"]}" />\n'
             f'<meta property="article:section" content="{e(p["category"])}" />\n'
             f'<meta property="article:author" content="Andreas Hagl" />\n')
    notes = ""
    if p.get("ai_note") or p.get("source"):
        notes = '\n      <div class="post-notes small muted">'
        if p.get("source"):
            notes += f"\n        <p>Quelle: {e(p['source'])}</p>"
        if p.get("ai_note"):
            notes += f"\n        <p>{e(p['ai_note'])}</p>"
        notes += "\n      </div>"
    updated = ""
    if p["updated"] != p["date"]:
        updated = f'\n        <span>Aktualisiert: <time datetime="{p["updated"]}">{de_datum(date.fromisoformat(p["updated"]))}</time></span>'
    others = [o for o in posts if o["slug"] != p["slug"]][:3]
    more = ""
    if others:
        more = ("\n  <section class=\"tinted\">\n    <div class=\"wrap\">\n      <h2>Weitere Beiträge</h2>\n"
                "      <div class=\"post-list\">\n" + "\n".join(post_card(o) for o in others) +
                "\n      </div>\n    </div>\n  </section>\n")
    cta_title = p.get("cta_title") or "Sprechen wir über Ihr Vorhaben"
    cta_text = f'\n      <p class="lead">{e(p["cta_text"])}</p>' if p.get("cta_text") else ""
    cta2 = ""
    if p.get("cta2_label") and p.get("cta2_href"):
        cta2 = f'\n        <a class="btn btn-ghost btn-lg" href="{e(p["cta2_href"])}">{e(p["cta2_label"])}</a>'

    return head(seo_title, p["description"], p["url"], "article", graph, extra) + f"""
{nav}

<main id="main">
  <header class="hero post-hero">
    <div class="wrap">
      <p class="crumb"><a href="/">Startseite</a> / <a href="/blog">Blog</a> / {e(p.get('seo_title') or p['title'])}</p>
      <p class="eyebrow">Blog · {e(p['category'])}</p>
      <h1>{e(p['title'])}</h1>
      <p class="lead">{e(p['lead'])}</p>
      <p class="meta">
        <span><span class="dot"></span>Andreas Hagl</span>
        <span><time datetime="{p['date']}">{de_datum(p['date_obj'])}</time></span>{updated}
        <span>{p['minutes']} Min. Lesezeit</span>
      </p>
    </div>
  </header>

  <section class="post-section">
    <div class="wrap">
      <article class="prose">
{p['body']}
      </article>
{AUTHOR_BOX}{notes}
    </div>
  </section>
{more}
  <section class="gruen final-cta">
    <div class="wrap">
      <h2>{e(cta_title)}</h2>{cta_text}
      <div class="btn-row">
        <a class="btn btn-primary btn-lg" href="{CALENDLY}" target="_blank" rel="noopener">Kostenloses Erstgespräch</a>{cta2}
      </div>
    </div>
  </section>
</main>
""" + tail(footer)


def render_index(posts, nav, footer):
    graph = ORG_PERSON + [
        {
            "@type": "Blog",
            "@id": f"{SITE}/blog#blog",
            "url": f"{SITE}/blog",
            "name": f"{BRAND} — Blog",
            "description": BLOG_DESC,
            "inLanguage": "de",
            "publisher": {"@id": f"{SITE}/#organization"},
            "author": {"@id": f"{SITE}/#person"},
            "blogPost": [{"@type": "BlogPosting", "@id": f"{p['url']}#article", "headline": p["title"][:110],
                          "url": p["url"], "datePublished": p["date"]} for p in posts],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Startseite", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog"},
            ],
        },
    ]
    cards = "\n".join(post_card(p, "h2") for p in posts)
    return head(f"Blog: Impulse für den Mittelstand | {BRAND}", BLOG_DESC, f"{SITE}/blog", "website", graph) + f"""
{nav}

<main id="main">
  <header class="hero" style="padding-bottom:24px;">
    <div class="wrap">
      <p class="crumb"><a href="/">Startseite</a> / Blog</p>
      <p class="eyebrow">{BLOG_TITLE}</p>
      <h1>{BLOG_H1}</h1>
      <p class="lead">{BLOG_LEAD}</p>
    </div>
  </header>

  <section>
    <div class="wrap">
      <div class="post-list post-list--index">
{cards}
      </div>
      <div class="newsletter-box" style="margin-top:40px;">
        <div class="txt">
          <h3>Neue Beiträge nicht verpassen</h3>
          <p>Der Newsletter bringt Impulse für KMU direkt ins Postfach — jederzeit abbestellbar.</p>
        </div>
        <div class="btn-row" style="margin:0;">
          <a class="btn btn-primary" href="{NEWSLETTER}" target="_blank" rel="noopener">Newsletter anmelden</a>
          <a class="btn btn-ghost" href="/blog/feed.xml">RSS-Feed</a>
        </div>
      </div>
    </div>
  </section>

  <section class="gruen final-cta">
    <div class="wrap">
      <h2>Lieber direkt sprechen?</h2>
      <p class="lead">Im kostenlosen Erstgespräch klären wir, wo in Ihrem Unternehmen der größte Hebel liegt.</p>
      <div class="btn-row">
        <a class="btn btn-primary btn-lg" href="{CALENDLY}" target="_blank" rel="noopener">Kostenloses Erstgespräch</a>
      </div>
    </div>
  </section>
</main>
""" + tail(footer)


def render_feed(posts):
    def rfc(d):
        return format_datetime(datetime(d.year, d.month, d.day, 8, 0, tzinfo=timezone.utc))
    items = "\n".join(f"""    <item>
      <title>{e(p['title'])}</title>
      <link>{p['url']}</link>
      <guid isPermaLink="true">{p['url']}</guid>
      <pubDate>{rfc(p['date_obj'])}</pubDate>
      <category>{e(p['category'])}</category>
      <description>{e(p['excerpt'])}</description>
    </item>""" for p in posts)
    last = rfc(posts[0]["date_obj"]) if posts else rfc(date.today())
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{BRAND} — Blog</title>
    <link>{SITE}/blog</link>
    <atom:link href="{SITE}/blog/feed.xml" rel="self" type="application/rss+xml" />
    <description>{e(BLOG_DESC)}</description>
    <language>de-DE</language>
    <lastBuildDate>{last}</lastBuildDate>
{items}
  </channel>
</rss>
"""


def replace_block(path, start, end, content):
    s = path.read_text(encoding="utf-8")
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(s):
        sys.exit(f"Marker {start} fehlt in {path.name}")
    s = pat.sub(lambda m: start + content + end, s, count=1)
    path.write_text(s, encoding="utf-8", newline="")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    print("geschrieben:", path.relative_to(ROOT))


# ---------------------------------------------------------------- Hauptlauf
def main():
    posts = [parse_post(f) for f in sorted((ROOT / "_blog" / "posts").glob("*.html"))]
    posts = [p for p in posts if p.get("draft", "").lower() != "true"]
    posts.sort(key=lambda p: p["date"], reverse=True)
    nav, footer = site_chrome()

    # verwaiste Artikelordner entfernen (Beitrag gelöscht/umbenannt)
    slugs = {p["slug"] for p in posts}
    for d in (ROOT / "blog").glob("*/"):
        if d.is_dir() and d.name not in slugs and (d / "index.html").exists():
            (d / "index.html").unlink()
            d.rmdir()
            print("entfernt:", d.relative_to(ROOT))

    for p in posts:
        write(ROOT / "blog" / p["slug"] / "index.html", render_post(p, posts, nav, footer))
    write(ROOT / "blog" / "index.html", render_index(posts, nav, footer))
    write(ROOT / "blog" / "feed.xml", render_feed(posts))

    # Sitemap
    newest = max([p["updated"] for p in posts], default=date.today().isoformat())
    sm = [f"""  <url>
    <loc>{SITE}/blog</loc>
    <lastmod>{newest}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>"""] + [f"""  <url>
    <loc>{p['url']}</loc>
    <lastmod>{p['updated']}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.6</priority>
  </url>""" for p in posts]
    replace_block(ROOT / "sitemap.xml", "<!-- BLOG:START -->", "<!-- BLOG:END -->", "\n" + "\n".join(sm) + "\n  ")

    # llms.txt
    llms = ["## Blog", f"- [Blog-Übersicht]({SITE}/blog): {BLOG_DESC}"] + \
           [f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts]
    replace_block(ROOT / "llms.txt", "<!-- BLOG:START -->", "<!-- BLOG:END -->", "\n" + "\n".join(llms) + "\n")

    # Startseite: neueste drei Beiträge
    teaser = ""
    if posts:
        teaser = f"""
  <section id="blog">
    <div class="wrap">
      <p class="eyebrow">Blog</p>
      <h2>Aus dem Blog</h2>
      <div class="post-list">
{chr(10).join(post_card(p) for p in posts[:3])}
      </div>
      <p style="margin-top:22px;"><a class="btn btn-secondary" href="/blog">Alle Beiträge</a></p>
    </div>
  </section>
  """
    replace_block(ROOT / "index.html", "<!-- BLOG-TEASER:START -->", "<!-- BLOG-TEASER:END -->", teaser)
    print(f"{len(posts)} Beitrag/Beiträge, Sitemap, llms.txt und Startseite aktualisiert.")


if __name__ == "__main__":
    main()
