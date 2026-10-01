// در ابتدای فایل shop.js بعد از "use strict";
const isProductDetail = !!document.getElementById("pd-gallery") || !!document.getElementById("pd-color-palette");
const isProductList = !!document.getElementById("product-grid");

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

(function initSortSelectSync() {

    if (!isProductDetail) return;

    const sortSelect = document.querySelector('select[name="filter-by"]');
    if (!sortSelect) return;

    const params = new URLSearchParams(window.location.search);
    const currentSort = params.get("filter-by") || "new";
    sortSelect.value = currentSort;
})();

function updatePriceDisplay(el) {
    if (!el.dataset.price) return;

    const priceEl = document.getElementById("pd-price");
    const specPriceEl = document.getElementById("spec-price-value");
    const oldPriceEl = document.getElementById("pd-price-old");
    const discountBadgeEl = document.getElementById("pd-discount-badge");
    const oldPriceLineEl = document.getElementById("pd-price-old-line");

    // اگه وریانت انتخاب‌شده موجودی نداشته باشه، به‌جای قیمت یه استایل مخصوص "ناموجود" نشون می‌دیم
    const stock = el.dataset.stock !== undefined ? Number(el.dataset.stock) : null;
    const inStock = stock === null || stock > 0;

    if (!inStock) {
        if (priceEl) {
            priceEl.textContent = "ناموجود";
            priceEl.classList.remove("price-placeholder", "price-discounted");
            priceEl.classList.add("price-unavailable");
        }
        if (specPriceEl) specPriceEl.textContent = "ناموجود";
        if (oldPriceLineEl) oldPriceLineEl.style.display = "none";
        return;
    }

    const finalPrice = Number(el.dataset.price);
    const originalPrice = el.dataset.originalPrice ? Number(el.dataset.originalPrice) : finalPrice;
    const discountPercent = el.dataset.discount ? Number(el.dataset.discount) : 0;
    const hasDiscount = discountPercent > 0 && originalPrice > finalPrice;

    const formattedFinal = formatPrice(finalPrice) + " تومان";

    if (priceEl) {
        priceEl.textContent = formattedFinal;
        priceEl.classList.remove("price-placeholder", "price-unavailable");
        priceEl.classList.toggle("price-discounted", hasDiscount);
    }
    if (specPriceEl) specPriceEl.textContent = formattedFinal;

    // این سایز/رنگ تخفیف داره: قیمت قبلی + بج تخفیف رو نشون بده
    if (hasDiscount) {
        if (oldPriceEl) oldPriceEl.textContent = formatPrice(originalPrice) + " تومان";
        if (discountBadgeEl) discountBadgeEl.textContent = discountPercent + "٪ تخفیف";
        if (oldPriceLineEl) oldPriceLineEl.style.display = "";
    } else {
        // این سایز/رنگ تخفیف نداره: مثل حالت عادی، قیمت قبلی مخفی می‌شه
        if (oldPriceLineEl) oldPriceLineEl.style.display = "none";
    }
}
function updateSpecVariantValue(text, targetId) {
    const specVariantEl = document.getElementById(targetId);
    if (specVariantEl) specVariantEl.textContent = text;
}

// جدول "مشخصات محصول" رو بر اساس مشخصات مخصوص همون وریانت انتخاب‌شده (سایز/رنگ) بازسازی می‌کنه
function updateVariantSpecs(el) {
    const specsBody = document.getElementById("variant-specs-body");
    if (!specsBody || el.dataset.specs === undefined) return;

    let specs = [];
    try {
        specs = JSON.parse(el.dataset.specs);
    } catch (err) {
        console.error("خطا در خواندن مشخصات وریانت:", err);
        return;
    }

    specsBody.innerHTML = "";
    specs.forEach((spec) => {
        const row = document.createElement("tr");

        const titleCell = document.createElement("td");
        titleCell.textContent = spec.title;

        const valueCell = document.createElement("td");
        valueCell.textContent = spec.description;

        row.appendChild(titleCell);
        row.appendChild(valueCell);
        specsBody.appendChild(row);
    });
}

// موجودی مخصوص همون وریانت انتخاب‌شده (نه فیلد stock کلی خود محصول) رو نشون می‌ده
function updateStockDisplay(el) {
    if (el.dataset.stock === undefined) return;

    const stockStatusEl = document.getElementById("pd-stock-status");
    const stockIconEl = document.getElementById("pd-stock-icon");
    const stockTextEl = document.getElementById("pd-stock-text");
    const addToCartBtn = document.querySelector(".btn-add-to-cart");
    const cartIconEl = document.getElementById("pd-cart-icon");
    const cartTextEl = document.getElementById("pd-cart-btn-text");
    if (!stockStatusEl) return;

    const stock = Number(el.dataset.stock);
    const inStock = stock > 0;
    // موجودیِ همون وریانت انتخاب‌شده کمه یا نه (بین ۱ تا ۵ عدد)
    const isLowStock = inStock && stock <= 5;

    stockStatusEl.classList.remove("stock-status-pending");
    stockStatusEl.classList.toggle("stock-status-out", !inStock);
    stockStatusEl.classList.toggle("stock-status-low", isLowStock);

    if (stockIconEl) {
        stockIconEl.classList.remove("fa-check", "fa-xmark", "fa-circle-info");
        stockIconEl.classList.add(inStock ? "fa-check" : "fa-xmark");
    }

    // وقتی موجودیِ وریانت انتخاب‌شده کمه، تعداد رو مستقیم همون‌جا
    // کنار «موجود در انبار» می‌نویسیم تا واضح باشه
    if (stockTextEl) {
        if (!inStock) {
            stockTextEl.textContent = "ناموجود";
        } else if (isLowStock) {
            stockTextEl.textContent = `موجود در انبار (فقط ${stock} عدد باقی مانده)`;
        } else {
            stockTextEl.textContent = "موجود در انبار";
        }
    }

    // دکمه افزودن به سبد هم باید موجودی همون وریانت رو بشناسه، نه موجودی کلی محصول
    if (addToCartBtn) {
        addToCartBtn.dataset.stock = stock;
        addToCartBtn.disabled = !inStock;
        addToCartBtn.classList.toggle("is-disabled", !inStock);
    }
    if (cartIconEl) {
        cartIconEl.classList.remove("fa-cart-shopping", "fa-ban");
        cartIconEl.classList.add(inStock ? "fa-cart-shopping" : "fa-ban");
    }
    if (cartTextEl) cartTextEl.textContent = inStock ? "افزودن به سبد خرید" : "ناموجود";
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
            // لینک «انتخاب گزینه‌ها» خودش به صفحه جزئیات می‌ره، نباید addToCart صدا زده بشه
            if (btn.tagName === "A") return;

            if (btn.disabled || btn.classList.contains("is-disabled")) {
                showToast("این محصول در حال حاضر ناموجود است", "warn");
                return;
            }

            const colorPalette = document.getElementById("pd-color-palette");
            const sizePalette = document.getElementById("pd-size-palette");
            if (btn.classList.contains("btn-add-to-cart") && (colorPalette || sizePalette)) {
                const selectedVariant = document.getElementById("selected-variant-id")?.value;
                if (!selectedVariant) {
                    const message = colorPalette ? "لطفاً یک رنگ را انتخاب کنید" : "لطفاً یک سایز را انتخاب کنید";
                    showToast(message, "warn");
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


function clearFilters() {
    window.location.href = window.location.pathname;
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}
function updateCartBadge(count) {
    document.querySelectorAll(".header__icon-btn--cart").forEach((cartBtn) => {
        let badge = cartBtn.querySelector(".header__cart-badge");

        if (count > 0) {
            if (!badge) {
                badge = document.createElement("span");
                badge.className = "header__cart-badge";
                cartBtn.appendChild(badge);
            }
            badge.textContent = count;
        } else if (badge) {
            badge.remove();
        }
    });
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

        updateCartBadge(data.total_quantity);
        showToast("محصول به سبد خرید اضافه شد", "success");

    } catch (err) {
        console.error("خطا در افزودن محصول به سبد خرید:", err);
        showToast("خطا در افزودن به سبد خرید، دوباره تلاش کنید", "error");
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

// --- اسلایدر گالری تصاویر در صفحه جزئیات محصول ---
(function initProductGallery() {
    const gallery = document.getElementById("pd-gallery");
    if (!gallery) return;

    const images = Array.from(gallery.querySelectorAll(".pd-image"));
    const thumbs = Array.from(document.querySelectorAll("#pd-gallery-thumbs .thumb-item"));
    const leftBtn = document.getElementById("pd-gallery-left");
    const rightBtn = document.getElementById("pd-gallery-right");

    if (images.length <= 1) return;

    let currentIndex = 0;

    function showImage(index) {
        currentIndex = (index + images.length) % images.length;
        images.forEach((img, i) => img.classList.toggle("active", i === currentIndex));
        thumbs.forEach((thumb, i) => thumb.classList.toggle("active", i === currentIndex));
    }

    // چون سایت راست‌چین (RTL) هست، دکمه‌ی سمت چپ باید عکس بعدی و دکمه‌ی سمت راست باید عکس قبلی رو نشون بده
    leftBtn?.addEventListener("click", () => showImage(currentIndex + 1));
    rightBtn?.addEventListener("click", () => showImage(currentIndex - 1));

    thumbs.forEach((thumb) => {
        thumb.addEventListener("click", () => showImage(Number(thumb.dataset.index)));
    });
})();

// --- پالت انتخاب رنگ در صفحه جزئیات محصول ---
(function initColorPalette() {

    if (!isProductDetail) return;

    const palette = document.getElementById("pd-color-palette");
    if (!palette) return;

    const hiddenInput = document.getElementById("selected-variant-id");
    const nameEl = document.getElementById("pd-color-selected-name");

    palette.querySelectorAll(".color-swatch").forEach((swatch) => {
        swatch.addEventListener("click", () => {
            palette.querySelectorAll(".color-swatch").forEach((s) => s.classList.remove("active"));
            swatch.classList.add("active");
            hiddenInput.value = swatch.dataset.variantId;

            const colorName = swatch.dataset.colorName || "#" + swatch.dataset.colorCode;
            const colorLabel = swatch.dataset.colorNumber ? `${colorName} (کد ${swatch.dataset.colorNumber})` : colorName;

            if (nameEl) nameEl.textContent = colorLabel;
            updateSpecVariantValue(colorLabel, "spec-color-value");
            updatePriceDisplay(swatch);
            updateStockDisplay(swatch);
            updateVariantSpecs(swatch);
        });
    });
})();

(function initSizePalette() {

    if (!isProductDetail) return;

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
            updateStockDisplay(dot);
            updateVariantSpecs(dot);
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

// --- فیلتر موبایل (باتم‌شیت) در صفحه لیست محصولات ---
(function initMobileFilterSheet() {
    const sheet = document.getElementById("filter-sheet");
    const openBtn = document.getElementById("filter-open-btn");
    if (!sheet || !openBtn) return;

    const overlay = document.getElementById("filter-overlay");
    const closeBtn = document.getElementById("filter-sheet-close");
    const applyBtn = document.getElementById("filter-sheet-apply");
    const clearBtn = document.getElementById("filter-sheet-clear");
    const clearChip = document.getElementById("filter-clear-chip");
    const badge = document.getElementById("filter-count-badge");
    const minInput = sheet.querySelector('input[name="min_price"]');
    const maxInput = sheet.querySelector('input[name="max_price"]');
    const form = sheet.querySelector(".filter-form");
    const categoryLinks = Array.from(sheet.querySelectorAll(".category-list a"));
    const chips = Array.from(sheet.querySelectorAll(".filter-chip"));
    const mq = window.matchMedia("(max-width: 992px)");

    const DEFAULT_SORT = "new";
    const DEFAULT_PAGE_SIZE = "20";

    // overlay رو به body منتقل می‌کنیم تا هیچ والدی روی position:fixed اثر نذاره
    if (overlay) document.body.appendChild(overlay);

    // انتخاب‌های موقت کاربر داخل شیت (تا زمان زدن «اعمال فیلتر»)
    const draft = { category: "", sort: DEFAULT_SORT, page_size: DEFAULT_PAGE_SIZE };

    function categoryOf(link) {
        try {
            return new URL(link.href, window.location.origin).searchParams.get("category") || "";
        } catch (e) {
            return "";
        }
    }

    function loadDraftFromUrl() {
        const params = new URLSearchParams(window.location.search);
        draft.category = params.get("category") || "";
        draft.sort = params.get("filter-by") || DEFAULT_SORT;
        draft.page_size = params.get("page_size") || DEFAULT_PAGE_SIZE;
        if (minInput) minInput.value = params.get("min_price") || "";
        if (maxInput) maxInput.value = params.get("max_price") || "";
    }

    function renderDraft() {
        categoryLinks.forEach((link) => {
            link.classList.toggle("is-selected", draft.category !== "" && categoryOf(link) === draft.category);
        });
        chips.forEach((chip) => {
            const group = chip.closest("[data-chip-group]").dataset.chipGroup;
            chip.classList.toggle("is-active", draft[group] === chip.dataset.value);
        });
    }

    function renderBar() {
        const params = new URLSearchParams(window.location.search);
        let count = 0;
        if (params.get("category")) count++;
        if (params.get("min_price") || params.get("max_price")) count++;
        const sort = params.get("filter-by");
        if (sort && sort !== DEFAULT_SORT) count++;

        if (badge) {
            badge.hidden = count === 0;
            badge.textContent = count.toLocaleString("fa-IR");
        }
        if (clearChip) clearChip.hidden = count === 0;
    }

    function openSheet() {
        loadDraftFromUrl();
        renderDraft();
        sheet.classList.add("is-open");
        overlay?.classList.add("is-open");
        document.body.classList.add("filter-sheet-open");
        openBtn.setAttribute("aria-expanded", "true");
        closeBtn?.focus();
    }

    function closeSheet() {
        sheet.classList.remove("is-open");
        overlay?.classList.remove("is-open");
        document.body.classList.remove("filter-sheet-open");
        openBtn.setAttribute("aria-expanded", "false");
    }

    function navigate(params) {
        params.delete("page");
        const qs = params.toString();
        window.location.href = qs ? `${window.location.pathname}?${qs}` : window.location.pathname;
    }

    function applyFilters() {
        const params = new URLSearchParams(window.location.search);

        if (draft.category) params.set("category", draft.category);
        else params.delete("category");

        let min = minInput ? parseInt(minInput.value, 10) : NaN;
        let max = maxInput ? parseInt(maxInput.value, 10) : NaN;
        if (!isNaN(min) && !isNaN(max) && min > max) [min, max] = [max, min];
        if (!isNaN(min) && min >= 0) params.set("min_price", min);
        else params.delete("min_price");
        if (!isNaN(max) && max >= 0) params.set("max_price", max);
        else params.delete("max_price");

        if (draft.sort && draft.sort !== DEFAULT_SORT) params.set("filter-by", draft.sort);
        else params.delete("filter-by");

        if (draft.page_size && draft.page_size !== DEFAULT_PAGE_SIZE) params.set("page_size", draft.page_size);
        else params.delete("page_size");

        navigate(params);
    }

    // حذف فیلترها (جستجوی متنی q حفظ می‌شه، چون فیلتر حساب نمی‌شه)
    function clearFilters_() {
        const params = new URLSearchParams(window.location.search);
        ["category", "brand", "min_price", "max_price", "filter-by", "page_size", "special_products"].forEach((k) =>
            params.delete(k),
        );
        navigate(params);
    }

    openBtn.addEventListener("click", openSheet);
    closeBtn?.addEventListener("click", closeSheet);
    overlay?.addEventListener("click", closeSheet);
    applyBtn?.addEventListener("click", applyFilters);
    clearBtn?.addEventListener("click", clearFilters_);
    clearChip?.addEventListener("click", clearFilters_);

    // کلیک روی دسته‌بندی: فقط توی حالت موبایل انتخاب می‌شه (دسکتاپ مثل قبل لینک عادیه)
    categoryLinks.forEach((link) => {
        link.addEventListener("click", (e) => {
            if (!mq.matches) return;
            e.preventDefault();
            const id = categoryOf(link);
            draft.category = draft.category === id ? "" : id;
            renderDraft();
        });
    });

    chips.forEach((chip) => {
        chip.addEventListener("click", () => {
            const group = chip.closest("[data-chip-group]").dataset.chipGroup;
            draft[group] = chip.dataset.value;
            renderDraft();
        });
    });

    // Enter توی فیلد قیمت (موبایل) = اعمال همه‌ی فیلترها
    form?.addEventListener("submit", (e) => {
        if (!mq.matches) return;
        e.preventDefault();
        applyFilters();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && sheet.classList.contains("is-open")) closeSheet();
    });

    // اگه صفحه به دسکتاپ تغییر سایز داد، شیت بسته بشه
    mq.addEventListener?.("change", (e) => {
        if (!e.matches) closeSheet();
    });

    loadDraftFromUrl();
    renderDraft();
    renderBar();
})();

// --- نمایش پیام کوتاه (از toast.js استفاده می‌کنه) ---
function showToast(message, type) {
    if (typeof window.siteToast === "function") {
        window.siteToast(message, type || "warn");
        return;
    }
    alert(message);
}