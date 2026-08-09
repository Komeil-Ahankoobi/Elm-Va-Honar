"use strict";

const cartItemsEl = document.getElementById("cart-items");

// --- آپدیت بج تعداد آیکون سبد خرید در هدر (چه در صفحه اصلی، چه در بقیه صفحات) ---
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

if (cartItemsEl) {
    const numFmt = (n) => new Intl.NumberFormat("en-US").format(n);
    const fmt = (n) => `${numFmt(n)} تومان`;

    const emptyEl = document.getElementById("cart-empty");
    const toastEl = document.getElementById("toast");
    const checkoutBtn = document.getElementById("checkout-btn");

    function showToast(msg) {
        if (!toastEl) return;
        toastEl.textContent = msg;
        toastEl.classList.add("show");
        clearTimeout(showToast._t);
        showToast._t = setTimeout(() => toastEl.classList.remove("show"), 2200);
    }

    // خوندن CSRF token از کوکی مرورگر (روش استاندارد جنگو)
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }
    const csrftoken = getCookie("csrftoken");

    // آپدیت وضعیت خالی/پر بودن سبد و دکمه checkout
    function updateEmptyState() {
        const items = [...cartItemsEl.querySelectorAll(".cart-row")];
        const isEmpty = items.length === 0;

        cartItemsEl.style.display = isEmpty ? "none" : "table";

        if (emptyEl) {
            emptyEl.style.display = isEmpty ? "flex" : "none";
        }

        if (checkoutBtn) {
            checkoutBtn.classList.toggle("is-disabled", isEmpty);
        }
    }

    // درخواست افزایش/کاهش تعداد به سمت جنگو
    async function updateQuantity(productId, variantId, action) {
        const response = await fetch("/cart/session/update-quantity/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                product_id: productId,
                variant_id: variantId || null,
                action: action,
            }),
        });

        if (!response.ok) {
            showToast("مشکلی پیش اومد، دوباره تلاش کن");
            return null;
        }

        return await response.json();
    }

    // درخواست حذف کامل محصول به سمت جنگو
    async function deleteProduct(productId, variantId) {
        const response = await fetch("/cart/session/delete-product/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                product_id: productId,
                variant_id: variantId || null,
            }),
        });

        if (!response.ok) {
            showToast("مشکلی پیش اومد، دوباره تلاش کن");
            return null;
        }

        return await response.json();
    }

    cartItemsEl.addEventListener("click", async (e) => {
        const btn = e.target.closest("[data-action]");
        if (!btn) return;

        const row = btn.closest(".cart-row");
        if (!row) return;

        const action = btn.dataset.action;
        const productId = row.dataset.id;
        const variantId = row.dataset.variantId;

        if (action === "inc" || action === "dec") {
            const data = await updateQuantity(productId, variantId, action);
            if (!data) return;

            // آپدیت تعداد همین ردیف
            const qtyEl = row.querySelector(".qty-val");
            if (qtyEl) qtyEl.textContent = data.quantity;

            const quEl = document.getElementById("p-quantity");
            if (quEl) quEl.textContent = data.total_quantity + " عدد";

            const x = document.getElementById("qu-title");
            if (x) x.textContent = data.total_quantity + " محصول در سبد خرید شما وجود دارد.";

            // آپدیت قیمت مجموع همین ردیف (بدون "تومان" چون کنارش span واحد جدا داره)
            const totalEl = row.querySelector(".cart-row-total");
            if (totalEl) totalEl.textContent = numFmt(data.item_total_price);

            // آپدیت جمع کل سبد (subtotal و total) و شمارنده navbar
            const subtotalEl = document.getElementById("sum-subtotal");
            const totalSumEl = document.getElementById("sum-total");
            const cartCountEl = document.getElementById("cart-count");

            if (subtotalEl) subtotalEl.textContent = fmt(data.cart_total_price);
            if (totalSumEl) totalSumEl.textContent = fmt(data.cart_total_price);
            if (cartCountEl) cartCountEl.textContent = `سبد (${data.total_quantity})`;

            // آپدیت بج آیکون سبد خرید در هدر
            updateCartBadge(data.total_quantity);
        } else if (action === "remove") {
            const nameEl = row.querySelector(".cart-row-name");
            const name = nameEl ? nameEl.textContent.trim() : "";

            const data = await deleteProduct(productId, variantId);
            if (!data) return;

            row.classList.add("removing");
            setTimeout(() => {
                row.remove();
                updateEmptyState();

                const subtotalEl = document.getElementById("sum-subtotal");
                const totalSumEl = document.getElementById("sum-total");
                const cartCountEl = document.getElementById("cart-count");
                const quEl = document.getElementById("p-quantity");
                const x = document.getElementById("qu-title");

                if (subtotalEl) subtotalEl.textContent = fmt(data.cart_total_price);
                if (totalSumEl) totalSumEl.textContent = fmt(data.cart_total_price);
                if (cartCountEl) cartCountEl.textContent = `سبد (${data.total_quantity})`;
                if (quEl) quEl.textContent = data.total_quantity + " عدد";
                if (x) x.textContent = data.total_quantity + " محصول در سبد خرید شما وجود دارد.";

                // آپدیت بج آیکون سبد خرید در هدر
                updateCartBadge(data.total_quantity);

                showToast(`"${name}" از سبد حذف شد`);
            }, 280);
        }
    });

    // Checkout
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", (e) => {
            if (checkoutBtn.classList.contains("is-disabled")) {
                e.preventDefault();
            }
        });
    }

    updateEmptyState();
}