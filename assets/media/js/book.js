// Reader controls — vanilla JS (no jQuery). Chapter/journal pages.
document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    function byClass(name) { return document.getElementsByClassName(name)[0]; }
    function on(el, ev, fn) { if (el) el.addEventListener(ev, fn); }

    // ── Modals: chapters list, "про книгу", (report removed — static site) ──────
    var chaptersModal = byClass("chapters-popup");
    var aboutModal = byClass("about-popup");

    on(byClass("open-chapters-popup"), "click", function () {
        if (chaptersModal) { chaptersModal.style.display = "block"; document.body.classList.add("modal-open"); }
    });
    on(byClass("close-chapters-popup"), "click", function () {
        if (chaptersModal) { chaptersModal.style.display = "none"; document.body.classList.remove("modal-open"); }
    });
    on(byClass("open-about-popup"), "click", function () {
        if (aboutModal) { aboutModal.style.display = "block"; document.body.classList.add("modal-open"); }
        closeDropdowns();
    });
    on(byClass("close-about-popup"), "click", function () {
        if (aboutModal) { aboutModal.style.display = "none"; document.body.classList.remove("modal-open"); }
    });

    // ── Fullscreen toggle ───────────────────────────────────────────────────────
    on(byClass("fullscreen"), "click", function () {
        var d = document, el = d.documentElement;
        var fs = d.fullscreenElement || d.webkitFullscreenElement || d.mozFullScreenElement;
        if (!fs) {
            (el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || function () {}).call(el);
        } else {
            (d.exitFullscreen || d.webkitExitFullscreen || d.mozCancelFullScreen || function () {}).call(d);
        }
    });

    // ── Dropdown menus (font / options) ─────────────────────────────────────────
    function closeDropdowns() {
        document.querySelectorAll(".dropdownButton").forEach(function (b) {
            var c = b.nextElementSibling;
            if (c) c.classList.remove("show");
        });
    }
    document.querySelectorAll(".dropdownButton").forEach(function (btn) {
        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            var content = btn.nextElementSibling;
            document.querySelectorAll(".dropdownButton").forEach(function (b) {
                if (b !== btn && b.nextElementSibling) b.nextElementSibling.classList.remove("show");
            });
            if (content) content.classList.toggle("show");
        });
    });
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".dropdownButton") && !e.target.closest(".dropdown-content")) {
            closeDropdowns();
        }
    });

    // ── Font size (max 3 steps up) ───────────────────────────────────────────────
    var readTargets = document.querySelectorAll("#book h1, #book h2, #book h3, #book h4, #book h5, #book h6, #book p, #book table");
    var fontDelta = 0;
    function changeFont(amount) {
        readTargets.forEach(function (el) {
            var base = parseInt(window.getComputedStyle(el).fontSize, 10) || 16;
            el.style.fontSize = (base + amount) + "px";
        });
    }
    on(document.getElementById("incfont"), "click", function (e) {
        e.preventDefault(); if (fontDelta < 3) { changeFont(2); fontDelta++; }
    });
    on(document.getElementById("decfont"), "click", function (e) {
        e.preventDefault(); if (fontDelta > 0) { changeFont(-2); fontDelta--; }
    });

    // ── Line height ──────────────────────────────────────────────────────────────
    function setLineHeight(cls) {
        document.body.classList.remove("line-height-small", "line-height-medium", "line-height-big");
        document.body.classList.add(cls);
    }
    on(document.getElementById("line-height-small"), "click", function () { setLineHeight("line-height-small"); });
    on(document.getElementById("line-height-medium"), "click", function () { setLineHeight("line-height-medium"); });
    on(document.getElementById("line-height-big"), "click", function () { setLineHeight("line-height-big"); });

    // ── Colour theme (persisted) ──────────────────────────────────────────────────
    function setBodyClass(className) {
        if (!className) return;
        document.body.className = className;
        try { localStorage.setItem("bodyClass", className); } catch (e) {}
    }
    var byId = function (id) { return document.getElementById(id); };
    on(byId("white"), "click", function () { setBodyClass("color-white"); });
    on(byId("sepia"), "click", function () { setBodyClass("color-sepia"); });
    on(byId("black"), "click", function () { setBodyClass("color-black"); });
    try {
        var saved = localStorage.getItem("bodyClass");
        if (saved) setBodyClass(saved);
    } catch (e) {}

    // ── Font family ───────────────────────────────────────────────────────────────
    var book = document.getElementById("book");
    function setFont(family) { if (book) book.style.fontFamily = family; }
    document.querySelectorAll("a.times").forEach(function (a) { a.addEventListener("click", function () { setFont('"Times New Roman", serif'); }); });
    document.querySelectorAll("a.arial").forEach(function (a) { a.addEventListener("click", function () { setFont("Arial, sans-serif"); }); });
    document.querySelectorAll("a.verdana").forEach(function (a) { a.addEventListener("click", function () { setFont("Verdana, sans-serif"); }); });

    // ── Click outside a modal closes it ─────────────────────────────────────────
    window.addEventListener("click", function (event) {
        if (chaptersModal && event.target === chaptersModal) chaptersModal.style.display = "none";
        if (aboutModal && event.target === aboutModal) aboutModal.style.display = "none";
        document.body.classList.remove("modal-open");
    });
});
