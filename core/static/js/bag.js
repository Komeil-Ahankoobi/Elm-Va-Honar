"use strict";

const cartItemsEl = document.getElementById("cart-items");

if (cartItemsEl) {
    const fmt = (n) => new Intl.NumberFormat("en-US").format(n) + " تومان";

    const emptyEl = document.getElementById("cart-empty");
    const toastEl = document.getElementById("toast");

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

        if (emptyEl) {
            emptyEl.style.display = isEmpty ? "flex" : "none";
        }

        const checkoutBtn = document.getElementById("checkout-btn");
        if (checkoutBtn) {
            checkoutBtn.disabled = isEmpty;
            checkoutBtn.style.opacity = isEmpty ? "0.5" : "1";
            checkoutBtn.style.cursor = isEmpty ? "not-allowed" : "pointer";
        }
    }

    // درخواست افزایش/کاهش تعداد به سمت جنگو
    async function updateQuantity(productId, action) {
        const response = await fetch("/cart/session/update-quantity/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                product_id: productId,
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
    async function deleteProduct(productId) {
        const response = await fetch("/cart/session/delete-product/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                product_id: productId,
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

        const item = btn.closest(".cart-row");
        if (!item) return;

        const action = btn.dataset.action;
        const productId = item.dataset.id;

        if (action === "inc" || action === "dec") {
            const data = await updateQuantity(productId, action);
            if (!data) return;

            // آپدیت تعداد همین آیتم
            const qtyEl = item.querySelector(".qty-val");
            if (qtyEl) qtyEl.textContent = data.quantity;

            // آپدیت قیمت کل همین آیتم
            const totalEl = item.querySelector(".cart-row-total");
            if (totalEl) totalEl.textContent = fmt(data.item_total_price);

            // آپدیت جمع کل سبد (هم subtotal هم total) و شمارنده navbar
            const subtotalEl = document.getElementById("sum-subtotal");
            const totalSumEl = document.getElementById("sum-total");
            const cartCountEl = document.getElementById("cart-count");

            if (subtotalEl) subtotalEl.textContent = fmt(data.cart_total_price);
            if (totalSumEl) totalSumEl.textContent = fmt(data.cart_total_price);
            if (cartCountEl) cartCountEl.textContent = `سبد (${data.total_quantity})`;

        } else if (action === "remove") {
            const nameEl = item.querySelector(".cart-row-name");
            const name = nameEl ? nameEl.textContent : "";

            const data = await deleteProduct(productId);
            if (!data) return;

            item.classList.add("removing");
            setTimeout(() => {
                item.remove();
                updateEmptyState();

                const subtotalEl = document.getElementById("sum-subtotal");
                const totalSumEl = document.getElementById("sum-total");
                const cartCountEl = document.querySelector(".cart-count");

                if (subtotalEl) subtotalEl.textContent = fmt(data.cart_total_price);
                if (totalSumEl) totalSumEl.textContent = fmt(data.cart_total_price);
                if (cartCountEl) cartCountEl.textContent = `${data.total_quantity}`;

                showToast(`"${name}" از سبد حذف شد`);
            }, 280);
        }
    });

    // Checkout
    const checkoutBtn = document.getElementById("checkout-btn");
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", () => {
            if (cartItemsEl.querySelectorAll(".cart-row").length === 0) return;
            showToast("در حال انتقال به درگاه پرداخت…");
        });
    }

    updateEmptyState();
}