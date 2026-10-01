"use strict";

/*
 * رفتار مشترک کارت‌های محصول (صفحه اصلی، جزئیات بلاگ و ...)
 *  - کلیک روی هرجای کارت            ← صفحه جزئیات محصول
 *  - «انتخاب گزینه‌ها» (لینک)        ← صفحه جزئیات محصول
 *  - «افزودن به سبد خرید» (دکمه)     ← افزودن به سبد، بدون رفتن به جزئیات
 *
 * صفحه‌هایی که shop.js رو لود می‌کنن (shop و product-detail) همین کارها رو
 * خودشون انجام می‌دن؛ پس اینجا چیزی bind نمی‌کنیم تا handler دوبل نشه.
 */
(function () {
    if (document.querySelector('script[src*="shop.js"]')) return;
    if (window.__productCardsInit) return;
    window.__productCardsInit = true;

    function toast(message, type) {
        if (typeof window.siteToast === "function") window.siteToast(message, type);
        else alert(message);
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

    async function addToCart(btn) {
        if (btn.dataset.loading === "1") return;
        btn.dataset.loading = "1";

        try {
            const response = await fetch(btn.dataset.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({ product_id: btn.dataset.productId, variant_id: null }),
            });

            if (!response.ok) throw new Error(`status ${response.status}`);

            const data = await response.json();
            updateCartBadge(data.total_quantity);
            toast("محصول به سبد خرید اضافه شد", "success");
        } catch (err) {
            console.error("خطا در افزودن محصول به سبد خرید:", err);
            toast("خطا در افزودن به سبد خرید، دوباره تلاش کنید", "error");
        } finally {
            btn.dataset.loading = "0";
        }
    }

    document.addEventListener("click", function (e) {
        // ۱) دکمه‌ی افزودن به سبد (فقط <button> که data-url داره)
        const cartBtn = e.target.closest("button.btn-add-cart");
        if (cartBtn) {
            e.preventDefault();
            if (cartBtn.disabled || cartBtn.classList.contains("is-disabled")) {
                toast("این محصول در حال حاضر ناموجود است", "warn");
                return;
            }
            if (cartBtn.dataset.url) addToCart(cartBtn);
            return;
        }

        // ۲) هر لینک داخل کارت (مثل «انتخاب گزینه‌ها») خودش ناوبری می‌کنه
        if (e.target.closest("a, button")) return;

        // ۳) کلیک روی بقیه‌ی کارت ← صفحه جزئیات
        const card = e.target.closest(".product-card[data-href]");
        if (card) window.location.href = card.dataset.href;
    });
})();