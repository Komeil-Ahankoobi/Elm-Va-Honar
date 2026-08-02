"use strict";

function formatPrice(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function showToast(message) {
    const toastEl = document.getElementById("toast");
    if (!toastEl) {
        alert(message);
        return;
    }
    toastEl.textContent = message;
    toastEl.classList.add("show");
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => {
        toastEl.classList.remove("show");
    }, 2500);
}

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
    if (!header || !backTop) return;

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

function formatPrice(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updatePriceDisplay(swatch) {
    const priceEl = document.getElementById("pd-price");
    const priceOldEl = document.getElementById("pd-price-old");
    const badgeEl = document.getElementById("pd-discount-badge");
    if (!priceEl) return;

    const price = Number(swatch.dataset.price);
    const priceOld = Number(swatch.dataset.priceOld);

    priceEl.textContent = formatPrice(price) + " تومان";

    if (priceOldEl) {
        if (priceOld > price) {
            priceOldEl.textContent = formatPrice(priceOld) + " تومان";
            priceOldEl.style.display = "";
            if (badgeEl) badgeEl.style.display = "";
        } else {
            priceOldEl.style.display = "none";
            if (badgeEl) badgeEl.style.display = "none";
        }
    }
}

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
    const targets = document.querySelectorAll(".reveal");
    if (!targets.length) return;

    if (!("IntersectionObserver" in window)) {
        targets.forEach((el) => el.classList.add("revealed"));
        return;
    }
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

    if (toggleBtn && menu) {
        function openMenu() {
            menu.classList.add("open");
            overlay?.classList.add("show");
            toggleBtn.setAttribute("aria-expanded", "true");
            document.body.style.overflow = "hidden";
        }

        function closeMenu() {
            menu.classList.remove("open");
            overlay?.classList.remove("show");
            toggleBtn.setAttribute("aria-expanded", "false");
            document.body.style.overflow = "";
        }

        toggleBtn.addEventListener("click", () => {
            menu.classList.contains("open") ? closeMenu() : openMenu();
        });

        closeBtn?.addEventListener("click", closeMenu);
        overlay?.addEventListener("click", closeMenu);

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && menu.classList.contains("open")) closeMenu();
        });

        menu.querySelectorAll("a").forEach((link) => {
            link.addEventListener("click", closeMenu);
        });
    }

    // --- Add to cart ---
    document.querySelectorAll(".btn-add-to-cart").forEach((btn) => {
        btn.addEventListener("click", () => {
            const colorPalette = document.getElementById("pd-color-palette");
            const sizePalette = document.getElementById("pd-size-palette");

            if (colorPalette || sizePalette) {
                const selectedInput = document.getElementById("selected-variant-id");
                if (selectedInput && !selectedInput.value) {
                    const message = colorPalette ? "لطفاً یک رنگ را انتخاب کنید" : "لطفاً یک سایز را انتخاب کنید";
                    showToast(message);
                    return;
                }
            }
            addToCart(btn.dataset.url, btn.dataset.productId);
        });
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
    const variantInput = document.getElementById("selected-variant-id");
    const variant_id = variantInput && variantInput.value ? variantInput.value : null;

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                product_id: product_id,
                variant_id: variant_id,
            }),
        }); 
        if (!response.ok) {
            throw new Error(`Server responded with status ${response.status}`);
        }

        const data = await response.json();

        const cartCountEl = document.querySelector(".cart-count");
        if (cartCountEl) {
            cartCountEl.textContent = `${data.total_quantity}`;
        }
    } catch (err) {
        console.error("خطا در افزودن محصول به سبد خرید:", err);
    }
}

document.addEventListener('click', function (e) {
    const card = e.target.closest('.product-card[data-href]');
    if (!card) return;

    
    if (e.target.closest('.product-wishlist, .btn-add-to-cart, .btn-quick-view')) {
        return;
    }

    window.location.href = card.dataset.href;
});


(function initColorPalette() {
    const palette = document.getElementById("pd-color-palette");
    if (!palette) return;

    const hiddenInput = document.getElementById("selected-variant-id");
    const nameEl = document.getElementById("pd-color-selected-name");

    palette.querySelectorAll(".pd-color-swatch").forEach((swatch) => {
        swatch.addEventListener("click", () => {
            palette.querySelectorAll(".pd-color-swatch").forEach((s) => s.classList.remove("active"));
            swatch.classList.add("active");
            hiddenInput.value = swatch.dataset.variantId;
            if (nameEl) nameEl.textContent = swatch.dataset.colorName || ("#" + swatch.dataset.colorCode);
            updatePriceDisplay(swatch);
        });
    });
})();

(function initSizePalette() {
    const palette = document.getElementById("pd-size-palette");
    if (!palette) return;

    const hiddenInput = document.getElementById("selected-variant-id");
    const nameEl = document.getElementById("pd-size-selected-name");

    palette.querySelectorAll(".pd-color-swatch").forEach((swatch) => {
        swatch.addEventListener("click", () => {
            palette.querySelectorAll(".pd-color-swatch").forEach((s) => s.classList.remove("active"));
            swatch.classList.add("active");
            hiddenInput.value = swatch.dataset.variantId;
            if (nameEl) nameEl.textContent = "شماره " + swatch.dataset.sizeCode;
            updatePriceDisplay(swatch);
        });
    });
})();
