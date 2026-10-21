// Vanilla JS — no jQuery dependency.
document.addEventListener("DOMContentLoaded", function () {
    // On content pages, move the sidebar (#form-control) above the text on narrow
    // screens so it reads first on mobile (mirrors the old insertBefore behaviour).
    document.querySelectorAll("#useful-info #form-control").forEach(function (el) {
        var prev = el.previousElementSibling;
        if (prev && prev.classList.contains("text-content")) {
            el.parentNode.insertBefore(el, prev);
        }
    });

    // Lightweight mobile nav: turn the sidebar menu into a <select> on small
    // screens (replacement for the old tinyNav jQuery plugin).
    var menu = document.getElementById("form-menu");
    if (menu && !document.getElementById("form-menu-nav")) {
        var select = document.createElement("select");
        select.id = "form-menu-nav";
        select.className = "tinynav";
        var def = document.createElement("option");
        def.textContent = "Меню…";
        def.value = "";
        select.appendChild(def);
        menu.querySelectorAll("a").forEach(function (a) {
            var opt = document.createElement("option");
            opt.value = a.getAttribute("href");
            opt.textContent = a.textContent.trim();
            select.appendChild(opt);
        });
        select.addEventListener("change", function () {
            if (select.value) window.location.href = select.value;
        });
        menu.parentNode.insertBefore(select, menu);
    }
});
