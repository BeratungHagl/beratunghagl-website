# CLAUDE.md – beratunghagl-website

Neue Haupt-Homepage für Beratungsunternehmen Hagl als statisches HTML/CSS,
Ersatz für die bisherige Onepage-Baukasten-Seite (www.andreas-hagl.de).
Ziel: Onepage-Abo kündbar machen, Domain beratung-hagl.de auf Vercel.

## Stack
- Statisches HTML/CSS (kein Build-Step), pro Route ein Ordner mit `index.html`
  (z. B. `compliance-kmu/index.html`) für saubere URLs ohne `.html`-Endung.
- Gemeinsames Stylesheet: `assets/styles.css`, Nav-Toggle-JS: `assets/nav.js`.
- Schrift: Inter (Google Fonts).
- Header/Footer/Nav sind in jeder Seite dupliziert (kein Build-Step) — bei
  Nav-/Footer-Änderungen alle Seiten konsistent nachziehen.

## Seitenstruktur (muss vollständig erhalten bleiben)
- `/` Startseite
- `/systemische-organisationsentwicklung`
- `/compliance-kmu` (auf der alten Seite fälschlich identisch mit
  `/foerdermittelberatung` — hier mit echtem, eigenem Inhalt neu geschrieben)
- `/prozesse-ki-digitalisierung`
- `/foerdermittelberatung`
- `/inqa-coach-foerderung`
- `/impressum`
- `/datenschutz`

## Corporate Identity (fix)
- Schrift: **Inter** überall
- Farben: Grün `#517F34`, Grün-Dark `#3f6427`, Schwarz `#000`, Weiß `#fff`,
  Mittelgrau `#4A4A4A`, Hellgrau `#F2F2F2`, Grün-Tint `#EAF2E0`,
  Kräftiggrau `#A6A6A6`, Rahmen `#E0E0E0`
- Logo: `assets/logo-mark.png` (grüner Rundpfeil/„G"-Form mit B/H, Original-Markenzeichen)
- Schreibstil: Deutsch, formell („Sie"), kein Gendern, korrekte Umlaute,
  sachlich-inspirierend. Positionierung: Wirkungs-Architekt & systemische OE,
  Pilot-Metapher „Reiseflughöhe".

## SEO-Strategie
Diese Seite setzt die Empfehlungen aus [[project-beratunghagl-strategy]] um:
gezielte Inhalte zu belegter Suchnachfrage (Sistrix-Daten), u. a.:
- `/compliance-kmu`: „welche 4 Phasen im Risikomanagement" (~63.200/Mon.),
  „3 Schritte Risikomanagement" (~26.000/Mon.)
- `/systemische-organisationsentwicklung`: „7 Phasen der OE", „was ist OE"
- `/prozesse-ki-digitalisierung`: „Beispiele digitale Transformation"
- `/foerdermittelberatung`: „wo finde ich Fördermittelberatung"
Jede Content-Seite hat Article- + FAQPage-JSON-LD; die Startseite trägt
ProfessionalService- + Person-Schema.

## Externe Dienste (bewusst schlank gehalten)
- Calendly (Terminbuchung): `https://calendly.com/kontakt-hagl/30min` — nur Link, kein Embed
- Brevo/Sendinblue (Newsletter): sibforms-Serve-Link, nur Link, kein Embed
- Alchimedus-Fördermittelcheck: externer Link (personalisierter Tracking-Link, nicht dekodieren/ändern)
- WhatsApp: `https://wa.me/491704792475`
- Keine Analytics/Tracking-Cookies eingebunden (Entscheidung: schlanker & DSGVO-einfacher
  als die alte Seite mit Google Ads/Analytics/Cookiebot — ggf. mit Andreas abstimmen,
  falls Tracking zurückgewünscht wird → dann Cookie-Consent-Banner nötig).

## Rechtliches
Impressum/Datenschutz enthalten echte, geprüfte Daten (Adresse, USt-ID,
Berufshaftpflicht). Bei Änderungen an eingebundenen Diensten IMMER auch
`datenschutz/index.html` aktualisieren.

## Deploy
Nicht eigenmächtig deployen – nur auf ausdrückliche Ansage
(siehe [[feedback-superanalyst-deploy]], gilt sinngemäß für alle Hagl-Projekte).
