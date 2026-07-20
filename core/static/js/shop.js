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


<script>
document.querySelectorAll('.custom-select').forEach(function (wrapper) {
  const trigger = wrapper.querySelector('.custom-select-trigger');
  const valueLabel = wrapper.querySelector('.custom-select-value');
  const hiddenInput = wrapper.querySelector('input[type="hidden"]');
  const options = wrapper.querySelectorAll('.custom-select-option');

  trigger.addEventListener('click', function () {
    wrapper.classList.toggle('open');
    trigger.setAttribute('aria-expanded', wrapper.classList.contains('open'));
  });

  options.forEach(function (option) {
    if (option.dataset.value === hiddenInput.value) {
      option.classList.add('selected');
      valueLabel.textContent = option.textContent.trim();
    }
    option.addEventListener('click', function () {
      hiddenInput.value = option.dataset.value;
      valueLabel.textContent = option.textContent.trim();
      options.forEach(function (o) { o.classList.remove('selected'); });
      option.classList.add('selected');
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
    });
  });

  document.addEventListener('click', function (e) {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
    }
  });
});
</script>