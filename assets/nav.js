document.addEventListener("DOMContentLoaded", function () {
  // Untermenü "Leistungen"
  var groups = document.querySelectorAll(".nav__group");
  function setOpen(g, open) {
    g.classList.toggle("open", open);
    g.querySelector(".nav__group-toggle").setAttribute("aria-expanded", open ? "true" : "false");
  }
  groups.forEach(function (g) {
    var btn = g.querySelector(".nav__group-toggle");
    btn.addEventListener("click", function () { setOpen(g, !g.classList.contains("open")); });
    g.addEventListener("focusout", function (e) {
      if (!g.contains(e.relatedTarget)) setOpen(g, false);
    });
  });
  document.addEventListener("click", function (e) {
    groups.forEach(function (g) { if (!g.contains(e.target)) setOpen(g, false); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    groups.forEach(function (g) {
      if (g.classList.contains("open")) { setOpen(g, false); g.querySelector(".nav__group-toggle").focus(); }
    });
  });

  // Mobilmenü
  var toggle = document.querySelector(".nav__toggle");
  var links = document.querySelector(".nav__links");
  if (!toggle || !links) return;
  toggle.addEventListener("click", function () {
    var open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  links.querySelectorAll("a").forEach(function (a) {
    a.addEventListener("click", function () { links.classList.remove("open"); });
  });
});
