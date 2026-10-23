// Cookie-Consent + Google-Ads-Tag (AW-496686154) – strikt opt-in.
// Google wird NICHT geladen, bevor der Besucher aktiv zustimmt (DSGVO/TTDSG).
// Zusätzlich Google Consent Mode v2 (Default: denied, bei Zustimmung: granted).
(function () {
  var KEY = "cookie-consent-v1";
  var GA_ID = "AW-496686154";

  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function loadGoogle() {
    if (window.__gtagLoaded) return;
    window.__gtagLoaded = true;
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("consent", "default", {
      ad_storage: "denied", ad_user_data: "denied",
      ad_personalization: "denied", analytics_storage: "denied",
    });
    gtag("consent", "update", {
      ad_storage: "granted", ad_user_data: "granted",
      ad_personalization: "granted", analytics_storage: "granted",
    });
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(s);
    gtag("config", GA_ID);
  }

  function removeBanner() {
    var b = document.getElementById("cookie-banner");
    if (b && b.parentNode) b.parentNode.removeChild(b);
  }

  function accept() { set("granted"); removeBanner(); loadGoogle(); }
  function decline() { set("denied"); removeBanner(); }

  function showBanner() {
    if (document.getElementById("cookie-banner")) return;
    var wrap = document.createElement("div");
    wrap.id = "cookie-banner";
    wrap.setAttribute("role", "dialog");
    wrap.setAttribute("aria-label", "Hinweis zu Cookies");
    wrap.innerHTML =
      '<div class="cb-inner">' +
      '<p class="cb-text">Wir setzen Cookies und den Google-Ads-Tag nur mit Ihrer Einwilligung ein, ' +
      "um die Wirksamkeit unserer Werbung zu messen. Sie können frei entscheiden und Ihre Wahl " +
      'jederzeit über „Cookie-Einstellungen" im Fußbereich ändern. Mehr in der ' +
      '<a href="/datenschutz">Datenschutzerklärung</a>.</p>' +
      '<div class="cb-actions">' +
      '<button type="button" class="btn btn-ghost cb-decline">Ablehnen</button>' +
      '<button type="button" class="btn btn-primary cb-accept">Akzeptieren</button>' +
      "</div></div>";
    document.body.appendChild(wrap);
    wrap.querySelector(".cb-accept").addEventListener("click", accept);
    wrap.querySelector(".cb-decline").addEventListener("click", decline);
  }

  function init() {
    // Widerruf/Änderung über Elemente mit .cookie-settings (z. B. Footer-Link)
    document.querySelectorAll(".cookie-settings").forEach(function (el) {
      el.addEventListener("click", function (e) { e.preventDefault(); showBanner(); });
    });
    var c = get();
    if (c === "granted") { loadGoogle(); return; }
    if (c === "denied") { return; }
    showBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
