//   <!-- ============================================================
//        JAVASCRIPT
//        - Live date in header
//        - Scroll-driven header shadow + back-to-top visibility
//        - Hero parallax on mousemove (rAF-throttled, transform only)
//        - Card 3D tilt effect (CSS custom properties, transform only)
//        - Carousel arrow buttons
//        All JS is vanilla. No libraries. No layout-triggering properties.
//        ============================================================ -->

"use strict";

/* ----------------------------------------------------------
       1. LIVE DATE — updates once at page load
       ---------------------------------------------------------- */
(function initDate() {
    const el = document.getElementById("live-date");
    if (!el) return;
    const now = new Date();
    const opts = { weekday: "short", day: "numeric", month: "long" };
    el.textContent = now.toLocaleDateString("en-GB", opts);
})();

/* ----------------------------------------------------------
       2. SCROLL LISTENERS — header shadow + back-to-top
       Uses a single rAF-throttled scroll handler for 60fps.
       ---------------------------------------------------------- */
(function initScroll() {
    const header = document.getElementById("site-header");
    const backTop = document.getElementById("back-to-top");
    let ticking = false;

    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;

                /* Header shadow on scroll */
                header.classList.toggle("scrolled", scrollY > 40);

                /* Back-to-top: visible after 400px */
                backTop.classList.toggle("visible", scrollY > 400);

                ticking = false;
            });
            ticking = true;
        }
    }

    window.addEventListener("scroll", onScroll, { passive: true });

    backTop.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
})();

/* ----------------------------------------------------------
       3. HERO PARALLAX ON MOUSEMOVE
       Moves the paper-texture bg very subtly on cursor position.
       Only transform used — zero reflows.
       Throttled via rAF.
       ---------------------------------------------------------- */
(function initParallax() {
    const hero = document.getElementById("hero");
    const heroBg = document.getElementById("hero-bg");
    if (!hero || !heroBg) return;

    // Skip on touch devices — no mouse to track
    if (window.matchMedia("(hover: none)").matches) return;

    let rafId = null;
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;
    const STRENGTH = 18; // max px travel
    const LERP = 0.08; // easing — lower = lazier

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function tick() {
        currentX = lerp(currentX, targetX, LERP);
        currentY = lerp(currentY, targetY, LERP);

        // Only transform — no top/left changes
        heroBg.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;

        rafId = requestAnimationFrame(tick);
    }

    hero.addEventListener(
        "mousemove",
        (e) => {
            const { left, top, width, height } = hero.getBoundingClientRect();
            const nx = (e.clientX - left) / width - 0.5; // -0.5 … +0.5
            const ny = (e.clientY - top) / height - 0.5;
            targetX = nx * STRENGTH;
            targetY = ny * STRENGTH;
        },
        { passive: true },
    );

    hero.addEventListener("mouseleave", () => {
        targetX = 0;
        targetY = 0;
    });

    // Start the animation loop
    rafId = requestAnimationFrame(tick);
})();

/* ----------------------------------------------------------
       4. CARD 3D TILT EFFECT
       Sets CSS custom properties --rx / --ry on each card.
       The CSS applies them via perspective + rotateX/Y.
       Only transforms change — zero reflow.
       ---------------------------------------------------------- */
(function initTilt() {
    const cards = document.querySelectorAll("[data-tilt]");
    const MAX_TILT = 10; // degrees

    cards.forEach((card) => {
        card.addEventListener(
            "mousemove",
            (e) => {
                const rect = card.getBoundingClientRect();
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                const dx = (e.clientX - cx) / (rect.width / 2);
                const dy = (e.clientY - cy) / (rect.height / 2);
                const ry = dx * MAX_TILT;
                const rx = -dy * MAX_TILT;
                card.style.setProperty("--rx", rx + "deg");
                card.style.setProperty("--ry", ry + "deg");
                card.style.transform = `perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateZ(0)`;
            },
            { passive: true },
        );

        card.addEventListener("mouseleave", () => {
            // Spring back to flat
            card.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0)";
        });
    });
})();

/* ----------------------------------------------------------
       5. CAROUSEL ARROW NAVIGATION
       Scrolls the carousel by one card width on each click.
       Uses scrollBy with behavior:'smooth' — no JS animation loop.
       ---------------------------------------------------------- */
(function initCarousel() {
    const carousel = document.getElementById("carousel");
    const btnPrev = document.getElementById("carousel-prev");
    const btnNext = document.getElementById("carousel-next");
    if (!carousel || !btnPrev || !btnNext) return;

    function getCardWidth() {
        const firstCard = carousel.querySelector(".product-card");
        if (!firstCard) return 320;
        const gap = parseInt(getComputedStyle(carousel).gap) || 0;
        return firstCard.offsetWidth + gap;
    }

    btnNext.addEventListener("click", () => {
        carousel.scrollBy({ left: getCardWidth(), behavior: "smooth" });
    });

    btnPrev.addEventListener("click", () => {
        carousel.scrollBy({ left: -getCardWidth(), behavior: "smooth" });
    });

    // Dim arrows at scroll bounds
    function updateButtons() {
        const maxScroll = carousel.scrollWidth - carousel.clientWidth;
        btnPrev.style.opacity = carousel.scrollLeft <= 4 ? "0.35" : "1";
        btnNext.style.opacity = carousel.scrollLeft >= maxScroll - 4 ? "0.35" : "1";
    }

    carousel.addEventListener("scroll", updateButtons, { passive: true });
    updateButtons();
})();

/* ----------------------------------------------------------
       6. INTERSECTION OBSERVER — subtle fade-in for sections
       Only opacity + translateY used (transform + opacity = no reflow).
       ---------------------------------------------------------- */
(function initReveal() {
    // Skip if browser doesn't support IntersectionObserver
    if (!("IntersectionObserver" in window)) return;

    // Add CSS for the reveal states
    const style = document.createElement("style");
    style.textContent = `
        .reveal {
          opacity: 0;
          transform: translateY(32px);
          transition: opacity 0.7s ease, transform 0.7s ease;
          will-change: transform, opacity;
        }
        .reveal.revealed {
          opacity: 1;
          transform: translateY(0);
        }
      `;
    document.head.appendChild(style);

    // Mark elements for reveal (section headers + cards + product cards)
    const targets = document.querySelectorAll(
        ".section-header, .category-card, .product-card, .philosophy-quote, .newsletter-title",
    );

    targets.forEach((el, i) => {
        el.classList.add("reveal");
        // Stagger cards within a grid
        if (el.classList.contains("category-card") || el.classList.contains("product-card")) {
            el.style.transitionDelay = (i % 4) * 80 + "ms";
        }
    });

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed");
                    observer.unobserve(entry.target); // fire once only
                }
            });
        },
        { threshold: 0.12 },
    );

    targets.forEach((el) => observer.observe(el));
})();

document.querySelectorAll(".category-card").forEach((card) => {
    card.addEventListener("mouseenter", () => {
        card.style.transition = "transform 0.08s ease-out, box-shadow 0.3s ease";
    });
    card.addEventListener("mouseleave", () => {
        card.style.transition = "transform 0.15s ease-out, box-shadow 0.3s ease";
    });
});

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
