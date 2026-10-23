// Vercel Serverless Function: Whitepaper-Anforderung
// POST { email, wp, newsletter }  ->  Kontakt in Brevo, Whitepaper per Mail (Absender kontakt@),
// Benachrichtigung an Beratung Hagl bei JEDER Anforderung, Rueckgabe des Download-Links.
//
// Benoetigte Vercel-Umgebungsvariablen (Project Settings -> Environment Variables):
//   BREVO_API_KEY     (erforderlich)  v3-API-Key aus Brevo
//   BREVO_LIST_ID     (optional)      Zahl: Newsletter-Liste fuer Opt-in
//   BREVO_TEMPLATE_ID (optional)      Zahl: transaktionale Brevo-Vorlage fuer die Whitepaper-Mail
//                                     (Platzhalter: {{ params.TITLE }}, {{ params.DOWNLOAD_URL }}, {{ params.EMAIL }})
//   WP_SENDER_EMAIL   (optional)      Standard: kontakt@beratung-hagl.de  (in Brevo verifizierter Absender)
//   WP_NOTIFY_EMAIL   (optional)      Standard: kontakt@beratung-hagl.de  (Benachrichtigungsadresse)

const WP = {
  strategie: { file: "Whitepaper_Strategieupdate_Hagl.pdf", title: "Strategie ist Chefsache" },
  marke:     { file: "Whitepaper_Marke_Hagl.pdf",           title: "Eine echte Marke werden" },
  prozesse:  { file: "Whitepaper_Prozesse-Organisation_Hagl.pdf", title: "Wachstum braucht Struktur" },
  risiko:    { file: "Whitepaper_Risiko-Compliance_Hagl.pdf",     title: "Risiken erkennen. Handlungsfähig bleiben." },
  security:  { file: "Whitepaper_Security-Compliance_Hagl.pdf",   title: "Security & Compliance" },
  ki:        { file: "Whitepaper_KI-Digitalisierung_Hagl.pdf",    title: "KI mit Fahrplan" },
};

const BASE = "https://andreas-hagl.de";
const SENDER = process.env.WP_SENDER_EMAIL || "kontakt@beratung-hagl.de";
const NOTIFY = process.env.WP_NOTIFY_EMAIL || "kontakt@beratung-hagl.de";

function isEmail(x) {
  return typeof x === "string" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(x) && x.length <= 254;
}

async function brevo(path, body, key) {
  const r = await fetch("https://api.brevo.com/v3" + path, {
    method: "POST",
    headers: { "api-key": key, "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify(body),
  });
  // 201/204 = ok; 400 "Contact already exist" ist bei updateEnabled kein Fehler
  if (!r.ok && r.status !== 204) {
    let msg = "";
    try { msg = JSON.stringify(await r.json()); } catch (e) { msg = String(r.status); }
    const err = new Error("Brevo " + path + " -> " + r.status + " " + msg);
    err.status = r.status;
    throw err;
  }
  return r;
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }

  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};

  const email = (body.email || "").trim();
  const wpKey = (body.wp || "").trim();
  const newsletter = body.newsletter === true || body.newsletter === "true" || body.newsletter === "on";
  const wp = WP[wpKey];

  if (!isEmail(email)) return res.status(400).json({ ok: false, error: "Bitte eine gültige E-Mail-Adresse angeben." });
  if (!wp) return res.status(400).json({ ok: false, error: "Unbekanntes Whitepaper." });

  const key = process.env.BREVO_API_KEY;
  const link = BASE + "/downloads/" + wp.file;

  if (!key) {
    // Fehlende Konfiguration: nicht 200 melden, damit das Frontend einen Hinweis zeigt.
    console.error("BREVO_API_KEY fehlt – Whitepaper-Versand nicht moeglich.");
    return res.status(503).json({ ok: false, error: "Versand derzeit nicht möglich. Bitte später erneut versuchen oder per E-Mail an kontakt@beratung-hagl.de." });
  }

  try {
    // 1) Kontakt anlegen/aktualisieren (Newsletter-Liste nur bei Opt-in)
    const contact = {
      email,
      updateEnabled: true,
      attributes: { WHITEPAPER: wp.title, QUELLE: "Website Whitepaper" },
    };
    const listId = parseInt(process.env.BREVO_LIST_ID || "", 10);
    if (newsletter && Number.isFinite(listId)) contact.listIds = [listId];
    try { await brevo("/contacts", contact, key); }
    catch (e) { if (e.status !== 400) throw e; } // 400 = existiert bereits -> ok

    // 2) Whitepaper an den Interessenten (Absender kontakt@)
    //    Wenn BREVO_TEMPLATE_ID gesetzt ist, wird die in Brevo gestaltete Vorlage genutzt
    //    (Platzhalter dort: {{ params.TITLE }}, {{ params.DOWNLOAD_URL }}, {{ params.EMAIL }}).
    //    Sonst wird die untenstehende HTML-Mail mit CI-Button und Signatur verschickt.
    const mailToUser = {
      sender: { name: "Beratungsunternehmen Hagl", email: SENDER },
      to: [{ email }],
      replyTo: { email: NOTIFY, name: "Beratungsunternehmen Hagl" },
    };
    const templateId = parseInt(process.env.BREVO_TEMPLATE_ID || "", 10);
    if (Number.isFinite(templateId)) {
      mailToUser.templateId = templateId;
      mailToUser.params = { TITLE: wp.title, DOWNLOAD_URL: link, EMAIL: email };
    } else {
      mailToUser.subject = "Ihr Whitepaper: " + wp.title;
      mailToUser.htmlContent =
        '<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#1a1a1a;line-height:1.6;max-width:560px">' +
        "<p>Guten Tag,</p>" +
        "<p>vielen Dank für Ihr Interesse. Hier ist Ihr Whitepaper <strong>„" + wp.title + "“</strong>:</p>" +
        '<p style="margin:24px 0"><a href="' + link + '" style="background:#517F34;color:#ffffff;text-decoration:none;padding:12px 22px;font-weight:bold;display:inline-block">Whitepaper herunterladen (PDF)</a></p>' +
        '<p style="font-size:13px;color:#4a4a4a">Falls der Button nicht funktioniert, nutzen Sie diesen Link:<br>' +
        '<a href="' + link + '" style="color:#517F34">' + link + "</a></p>" +
        "<p>Bei Fragen melden Sie sich gern direkt bei mir.</p>" +
        '<hr style="border:none;border-top:1px solid #e0e0e0;margin:24px 0">' +
        '<table cellpadding="0" cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#4a4a4a;line-height:1.5"><tr><td>' +
        '<strong style="color:#1a1a1a">Andreas Hagl</strong><br>' +
        "Strategieberater &amp; Wirkungs-Architekt<br>" +
        "Beratungsunternehmen Hagl<br>" +
        "Schulstr. 15 · 84104 Rudelzhausen<br>" +
        'Tel. <a href="tel:+491704792475" style="color:#517F34">0170 4792475</a> · ' +
        '<a href="mailto:kontakt@beratung-hagl.de" style="color:#517F34">kontakt@beratung-hagl.de</a><br>' +
        '<a href="https://andreas-hagl.de" style="color:#517F34">andreas-hagl.de</a>' +
        "</td></tr></table></div>";
    }
    await brevo("/smtp/email", mailToUser, key);

    // 3) Benachrichtigung an Beratung Hagl (bei jeder Anforderung)
    await brevo("/smtp/email", {
      sender: { name: "Website Whitepaper", email: SENDER },
      to: [{ email: NOTIFY }],
      replyTo: { email },
      subject: "Whitepaper-Anforderung: " + wp.title,
      htmlContent:
        '<div style="font-family:Arial,sans-serif;font-size:15px">' +
        "<p><strong>Neue Whitepaper-Anforderung</strong></p>" +
        "<p>E-Mail: " + email + "<br>Whitepaper: " + wp.title +
        "<br>Newsletter gewünscht: " + (newsletter ? "ja" : "nein") + "</p>" +
        "</div>",
    }, key);

    return res.status(200).json({ ok: true, url: link, title: wp.title });
  } catch (e) {
    console.error("Whitepaper-Fehler:", e && e.message);
    return res.status(502).json({ ok: false, error: "Versand fehlgeschlagen. Bitte später erneut versuchen oder per E-Mail an kontakt@beratung-hagl.de." });
  }
}
