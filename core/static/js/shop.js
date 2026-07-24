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

(function initFilters() {
    document.querySelectorAll(".filter-option").forEach((opt) => {
        opt.addEventListener("click", () => {
            opt.parentElement.querySelectorAll(".filter-option").forEach((o) => o.classList.remove("active"));
            opt.classList.add("active");
        });
    });
    document.querySelectorAll(".filter-swatch").forEach((sw) => {
        sw.addEventListener("click", () => {
            document.querySelectorAll(".filter-swatch").forEach((s) => s.classList.remove("active"));
            sw.classList.add("active");
        });
    });
})();

(function initReveal() {
    if (!("IntersectionObserver" in window)) {
        document.querySelectorAll(".reveal").forEach((el) => el.classList.add("revealed"));
        return;
    }
    const targets = document.querySelectorAll(".reveal");
    targets.forEach((el, i) => {
        el.style.transitionDelay = (i % 3) * 80 + "ms";
    });
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 },
    );
    targets.forEach((el) => observer.observe(el));
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

function goToPage(event, pageNumber) {
    event.preventDefault();

    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    params.set("page", pageNumber);

    const newUrl = `${url.pathname}?${params.toString()}`;

    window.location.href = newUrl;
}

function filterProducts(selectedElemnt) {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    const paramsName = selectedElemnt.name;
    const paramsValue = selectedElemnt.value;

    params.set(paramsName, paramsValue);

    const newUrl = `${url.pathname}?${params.toString()}`;
    window.location.href = newUrl;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

async function addToCart(url, product_id) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
            product_id: product_id,
        }),
    });

    const data = await response.json();
    console.log(data);
}

document.querySelectorAll(".btn-add-to-cart").forEach((btn) => {
    btn.addEventListener("click", () => {
        addToCart(btn.dataset.url, btn.dataset.productId);
    });
});
