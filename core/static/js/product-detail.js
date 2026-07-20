"use strict";

(function initDate() {
    const el = document.getElementById("live-date");
    if (!el) return;
    const now = new Date();
    const opts = { weekday: "short", day: "numeric", month: "long" };
    el.textContent = now.toLocaleDateString("en-GB", opts);
})();

(function initScroll() {
    const header = document.getElementById("site-header");
    const backTop = document.getElementById("back-to-top");
    let ticking = false;

    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;
                header.classList.toggle("scrolled", scrollY > 40);
                backTop.classList.toggle("visible", scrollY > 400);
                ticking = false;
            });
            ticking = true;
        }
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    backTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
})();

/* Gallery thumbnail switching */
(function initGallery() {
    const mainImg = document.getElementById("pd-main-img");
    const thumbs = document.querySelectorAll(".pd-thumb");
    thumbs.forEach((thumb) => {
        thumb.addEventListener("click", () => {
            thumbs.forEach((t) => t.classList.remove("active"));
            thumb.classList.add("active");
            const src = thumb.querySelector("img").src.replace("/200/200", "/900/900");
            mainImg.style.opacity = "0";
            setTimeout(() => {
                mainImg.src = src;
                mainImg.style.opacity = "1";
            }, 150);
        });
    });
})();

/* Nib width selector */
(function initNibOptions() {
    const btns = document.querySelectorAll(".pd-nib-btn");
    const label = document.querySelector(".pd-option-group .selected-value");
    btns.forEach((btn) => {
        btn.addEventListener("click", () => {
            btns.forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            if (label) label.textContent = btn.textContent;
        });
    });
})();

/* Colour swatch selector */
(function initColorOptions() {
    const swatches = document.querySelectorAll(".pd-color-swatch");
    const labels = document.querySelectorAll(".pd-option-label .selected-value");
    const colorLabel = labels[1];
    swatches.forEach((sw) => {
        sw.addEventListener("click", () => {
            swatches.forEach((s) => s.classList.remove("active"));
            sw.classList.add("active");
            if (colorLabel) colorLabel.textContent = sw.getAttribute("aria-label");
        });
    });
})();

/* Quantity stepper */
(function initQty() {
    const input = document.getElementById("qty-input");
    const minus = document.getElementById("qty-minus");
    const plus = document.getElementById("qty-plus");
    if (!input) return;
    minus.addEventListener("click", () => {
        const v = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
        input.value = v;
    });
    plus.addEventListener("click", () => {
        const v = Math.min(99, (parseInt(input.value, 10) || 1) + 1);
        input.value = v;
    });
})();

/* Accordion */
(function initAccordion() {
    const items = document.querySelectorAll(".pd-accordion-item");
    items.forEach((item) => {
        const trigger = item.querySelector(".pd-accordion-trigger");
        trigger.addEventListener("click", () => {
            const isOpen = item.classList.contains("open");
            items.forEach((i) => {
                i.classList.remove("open");
                i.querySelector(".pd-accordion-trigger").setAttribute("aria-expanded", "false");
            });
            if (!isOpen) {
                item.classList.add("open");
                trigger.setAttribute("aria-expanded", "true");
            }
        });
    });
})();
