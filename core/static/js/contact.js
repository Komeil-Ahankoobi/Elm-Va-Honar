//   <!-- ============================================================
//        CONTACT PAGE JAVASCRIPT
//        - Lightweight client-side form feedback (no backend wired up)
//        - FAQ accordion needs no JS — native <details> handles it
//        Vanilla JS only, consistent with home.js conventions.
//        ============================================================ -->

"use strict";

(function initContactForm() {
    const form = document.getElementById("contact-form");
    const note = document.getElementById("form-note");
    if (!form || !note) return;

    form.addEventListener("submit", () => {
        const name = form.querySelector("#cf-name").value.trim();
        note.textContent = name
            ? `Thank you, ${name} — we'll be in touch within one working day.`
            : "Thank you — we'll be in touch within one working day.";
        form.reset();
    });
})();

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.querySelector(".nav-mobile-toggle");
    const menu = document.querySelector(".nav-mobile-menu");
    const overlay = document.querySelector(".mobile-menu-overlay");
    const closeBtn = document.querySelector(".mobile-close-btn");

    if (!toggleBtn || !menu) return;

    function openMenu() {
        menu.classList.add("open");
        overlay.classList.add("show");
        toggleBtn.setAttribute("aria-expanded", "true");
        document.body.style.overflow = "hidden";
    }

    function closeMenu() {
        menu.classList.remove("open");
        overlay.classList.remove("show");
        toggleBtn.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
    }

    toggleBtn.addEventListener("click", () => {
        menu.classList.contains("open") ? closeMenu() : openMenu();
    });

    closeBtn?.addEventListener("click", closeMenu);
    overlay?.addEventListener("click", closeMenu);

    // Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && menu.classList.contains("open")) closeMenu();
    });

    // Close on link click
    menu.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });
});