# beratunghagl-website

Neue Haupt-Homepage für **Beratungsunternehmen Hagl** — statisches HTML/CSS,
Vercel-fähig, als Ersatz für die bisherige Onepage-Baukasten-Seite unter
www.andreas-hagl.de (Domain beratung-hagl.de).

Inhaltlich 1:1-Nachbau aller bisherigen Seiten und Unterseiten, mit
modernisiertem Design (Hagl-CI: Inter, Grün #517F34) sowie überarbeiteten,
SEO-/AI-optimierten Texten gemäß den Empfehlungen aus der Strategieanalyse
(siehe Schwesterprojekt `beratunghagl-strategy`).

## Struktur

```
beratunghagl-website/
├─ index.html                              # Startseite
├─ systemische-organisationsentwicklung/index.html
├─ compliance-kmu/index.html                # neu geschrieben (war auf alter Seite defekt/dupliziert)
├─ prozesse-ki-digitalisierung/index.html
├─ foerdermittelberatung/index.html
├─ inqa-coach-foerderung/index.html
├─ impressum/index.html
├─ datenschutz/index.html
├─ assets/
│  ├─ styles.css      # CI-Stylesheet
│  ├─ nav.js          # Mobile-Nav-Toggle
│  └─ logo-mark.png   # Logo
├─ robots.txt
├─ sitemap.xml
├─ vercel.json
└─ README.md
```

## Lokal ansehen

```bash
python -m http.server 8000
# http://localhost:8000
```

## Deploy

Statische Seite, direkt auf Vercel deploybar (`vercel` / Git-Integration).
**Nicht eigenmächtig deployen — nur auf ausdrückliche Ansage.**

Domain-Umstellung: `beratung-hagl.de` läuft aktuell über IONOS/Onepage.
Für den Wechsel muss bei Vercel die Domain hinzugefügt und bei IONOS der
DNS-Eintrag (A-Record bzw. CNAME laut Vercel-Anleitung) angepasst werden —
das Hosting der Domain selbst bleibt bei IONOS, nur das Routing zeigt dann
auf Vercel. Erst danach kann das Onepage-Abo gekündigt werden.

## Offene Punkte

- Domain `beratung-hagl.de` ist noch nicht auf dieses Projekt umgestellt.
- Eigenes Foto von Andreas Hagl für den Hero-Bereich fehlt noch (aktuell
  bewusst bildfrei mit SVG-Illustration gelöst).
- Entscheidung nötig: Soll Tracking (Google Analytics/Ads) wie auf der alten
  Seite zurückkommen? Aktuell bewusst weggelassen (schlanker, kein
  Cookie-Banner nötig). Falls gewünscht, braucht es einen Consent-Banner und
  ein Update der Datenschutzerklärung.
- Newsletter- und Fördermittelcheck-Buttons verlinken auf die bestehenden
  externen Anmeldeseiten (Brevo, Alchimedus) statt eingebettet zu sein.
