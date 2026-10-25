// Whitepaper-Anforderung: sendet das Formular per fetch an /api/whitepaper,
// zeigt Erfolg + Direkt-Download oder eine Fehlermeldung an.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form.wp-form").forEach(function (form) {
    // Zeitfalle: Ladezeitpunkt des Formulars festhalten (Bots senden sofort).
    var tsEl = form.querySelector('[name="ts"]');
    if (tsEl) tsEl.value = String(Date.now());

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector(".wp-status");
      var btn = form.querySelector('button[type="submit"]');
      var emailEl = form.querySelector('[name="email"]');
      var wpEl = form.querySelector('[name="wp"]');
      var nlEl = form.querySelector('[name="newsletter"]');
      var hpEl = form.querySelector('[name="website"]');
      var email = emailEl ? emailEl.value.trim() : "";
      var wp = wpEl ? wpEl.value : (form.dataset.wp || "");
      var newsletter = nlEl ? nlEl.checked : false;
      var website = hpEl ? hpEl.value : "";
      var ts = tsEl ? tsEl.value : "";

      function fail(msg) {
        if (status) { status.className = "wp-status wp-error"; status.textContent = msg; }
      }
      if (!email) { fail("Bitte geben Sie Ihre E-Mail-Adresse ein."); return; }
      if (!wp) { fail("Bitte wählen Sie ein Whitepaper aus."); return; }

      var old = btn ? btn.textContent : "";
      if (btn) { btn.disabled = true; btn.textContent = "Wird gesendet…"; }
      if (status) { status.className = "wp-status"; status.textContent = ""; }

      fetch("/api/whitepaper", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: email, wp: wp, newsletter: newsletter, website: website, ts: ts }),
      })
        .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
        .then(function (res) {
          if (res.ok && res.d && res.d.ok) {
            form.innerHTML =
              '<p class="wp-success">✓ Vielen Dank! Das Whitepaper „' + (res.d.title || "") +
              '" ist auf dem Weg in Ihr Postfach. ' +
              '<a href="' + res.d.url + '" target="_blank" rel="noopener">Jetzt direkt herunterladen</a>.</p>';
          } else {
            fail((res.d && res.d.error) || "Es ist ein Fehler aufgetreten. Bitte später erneut versuchen.");
            if (btn) { btn.disabled = false; btn.textContent = old; }
          }
        })
        .catch(function () {
          fail("Verbindungsfehler. Bitte später erneut versuchen oder per E-Mail an kontakt@beratung-hagl.de.");
          if (btn) { btn.disabled = false; btn.textContent = old; }
        });
    });
  });
});
