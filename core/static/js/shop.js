"use strict";

(function initDate() {
    const el = document.getElementById("live-date");
    if (!el) return;
    const now = new Date();
    const opts = { weekday: "short", day: "numeric", month: "long" };
    el.textContent = now.toLocaleDateString("en-GB", opts);
})();

function formatPrice(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updatePriceDisplay(el) {
    const priceEl = document.getElementById("pd-price");
    const specPriceEl = document.getElementById("spec-price-value");
    if (el.dataset.price) {
        const formatted = formatPrice(Number(el.dataset.price)) + " تومان";
        if (priceEl) priceEl.textContent = formatted;
        if (specPriceEl) specPriceEl.textContent = formatted;
    }
}
function updateSpecVariantValue(text, targetId) {
    const specVariantEl = document.getElementById(targetId);
    if (specVariantEl) specVariantEl.textContent = text;
}

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

    // --- Add to cart (لیست محصولات، جزئیات محصول، محصولات مرتبط) ---
    document.querySelectorAll(".btn-add-cart, .btn-add-to-cart, .btn-card-add").forEach((btn) => {
        btn.addEventListener("click", () => {
            const colorPalette = document.getElementById("pd-color-palette");
            const sizePalette = document.getElementById("pd-size-palette");
            if (btn.classList.contains("btn-add-to-cart") && (colorPalette || sizePalette)) {
                const selectedVariant = document.getElementById("selected-variant-id")?.value;
                if (!selectedVariant) {
                    const message = colorPalette ? "لطفاً یک رنگ را انتخاب کنید" : "لطفاً یک سایز را انتخاب کنید";
                    showToast(message);
                    return;
                }
            }
            addToCart(btn.dataset.url, btn.dataset.productId);
        });
    });
});

(function initProductTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabPanes = document.querySelectorAll(".tab-pane");
    if (!tabBtns.length || !tabPanes.length) return;

    tabBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            tabBtns.forEach((b) => b.classList.remove("active"));
            tabPanes.forEach((p) => p.classList.remove("active"));

            btn.classList.add("active");
            const target = document.querySelector(`[data-tab-content="${btn.dataset.tab}"]`);
            if (target) target.classList.add("active");
        });
    });
})();

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

// --- کلیک روی کارت محصول (لیست محصولات و محصولات مرتبط) ---
// با کلیک روی هرجای کارت به صفحه محصول می‌ره، به جز دکمه‌های افزودن به سبد / علاقه‌مندی
document.addEventListener("click", function (e) {
    const card = e.target.closest(".product-card[data-href], .related-card[data-href]");
    if (!card) return;

    if (
        e.target.closest(
            ".wishlist-btn, .wishlist-icon-btn, .btn-wishlist, .btn-add-cart, .btn-add-to-cart, .btn-card-add",
        )
    ) {
        return;
    }

    window.location.href = card.dataset.href;
});

// --- پالت انتخاب رنگ در صفحه جزئیات محصول ---
(function initColorPalette() {
    const palette = document.getElementById("pd-color-palette");
    if (!palette) return;

    const hiddenInput = document.getElementById("selected-variant-id");
    const nameEl = document.getElementById("pd-color-selected-name");

    palette.querySelectorAll(".dot").forEach((dot) => {
        dot.addEventListener("click", () => {
            palette.querySelectorAll(".dot").forEach((d) => d.classList.remove("active"));
            dot.classList.add("active");
            hiddenInput.value = dot.dataset.variantId;
            if (nameEl) nameEl.textContent = dot.dataset.colorName || "#" + dot.dataset.colorCode;
            updateSpecVariantValue(dot.dataset.colorName || "#" + dot.dataset.colorCode, "spec-color-value");
            updatePriceDisplay(dot);
        });
    });
})();

(function initSizePalette() {
    const palette = document.getElementById("pd-size-palette");
    if (!palette) return;

    const hiddenInput = document.getElementById("selected-variant-id");
    const nameEl = document.getElementById("pd-size-selected-name");

    palette.querySelectorAll(".dot").forEach((dot) => {
        dot.addEventListener("click", () => {
            palette.querySelectorAll(".dot").forEach((d) => d.classList.remove("active"));
            dot.classList.add("active");
            hiddenInput.value = dot.dataset.variantId;
            if (nameEl) nameEl.textContent = "شماره " + dot.dataset.sizeCode;
            updateSpecVariantValue("شماره " + dot.dataset.sizeCode, "spec-size-value");
            updatePriceDisplay(dot);
        });
    });
})();
// --- کنترل تعداد در صفحه جزئیات محصول ---
(function initQuantityPicker() {
    document.querySelectorAll(".qty-picker").forEach((picker) => {
        const decreaseBtn = picker.querySelector(".qty-decrease");
        const increaseBtn = picker.querySelector(".qty-increase");
        const input = picker.querySelector(".qty-value");
        if (!decreaseBtn || !increaseBtn || !input) return;

        function toEnglishDigits(str) {
            return str.replace(/[۰-۹]/g, (d) => "۰۱۲۳۴۵۶۷۸۹".indexOf(d));
        }

        function getValue() {
            const n = parseInt(toEnglishDigits(input.value), 10);
            return isNaN(n) ? 1 : n;
        }

        decreaseBtn.addEventListener("click", () => {
            const current = getValue();
            if (current > 1) input.value = current - 1;
        });

        increaseBtn.addEventListener("click", () => {
            input.value = getValue() + 1;
        });
    });
})();

// --- حفظ پارامترهای فیلتر (قیمت، جستجو، دسته‌بندی، مرتب‌سازی و ...) هنگام تغییر صفحه ---
(function initPagination() {
    const links = document.querySelectorAll(".pagination a.page-item");
    if (!links.length) return;

    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            // شماره صفحه‌ای که این لینک بهش اشاره می‌کنه
            const linkUrl = new URL(link.href, window.location.origin);
            const targetPage = linkUrl.searchParams.get("page");

            // پارامترهای فعلی صفحه (فیلترها) رو نگه می‌داریم و فقط page رو عوض می‌کنیم
            const currentParams = new URLSearchParams(window.location.search);
            if (targetPage) {
                currentParams.set("page", targetPage);
            }

            window.location.href = `${window.location.pathname}?${currentParams.toString()}`;
        });
    });
})();

// --- نمایش پیام کوتاه (در صورت نبود پیاده‌سازی toast در جای دیگری از پروژه) ---
function showToast(message) {
    if (typeof window.showToast === "function" && window.showToast !== showToast) {
        window.showToast(message);
        return;
    }
    alert(message);
}
