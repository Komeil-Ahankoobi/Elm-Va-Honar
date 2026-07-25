"use strict";

const cartItemsEl = document.getElementById("cart-items");

if (cartItemsEl) {
    const fmt = (n) => new Intl.NumberFormat("en-US").format(n) + " تومان";

    const emptyEl = document.getElementById("cart-empty");
    const toastEl = document.getElementById("toast");

    function showToast(msg) {
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
        const items = [...cartItemsEl.querySelectorAll(".cart-item")];
        const isEmpty = items.length === 0;
        emptyEl.classList.toggle("show", isEmpty);

        const checkoutBtn = document.getElementById("checkout-btn");
        checkoutBtn.disabled = isEmpty;
        checkoutBtn.style.opacity = isEmpty ? "0.5" : "1";
        checkoutBtn.style.cursor = isEmpty ? "not-allowed" : "pointer";
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

        const item = btn.closest(".cart-item");
        const action = btn.dataset.action;
        const productId = item.dataset.id;

        if (action === "inc" || action === "dec") {
            const data = await updateQuantity(productId, action);
            if (!data) return;

            // آپدیت تعداد همین آیتم
            item.querySelector(".qty-val").textContent = data.quantity;

            // آپدیت قیمت کل همین آیتم
            item.querySelector(".item-prices").textContent = fmt(data.item_total_price);

            // آپدیت جمع کل سبد (هم subtotal هم total) و شمارنده navbar
            document.getElementById("sum-subtotal").textContent = fmt(data.cart_total_price);
            document.getElementById("sum-total").textContent = fmt(data.cart_total_price);
            document.getElementById("cart-count").textContent = `سبد (${data.total_quantity})`;

        } else if (action === "remove") {
            const name = item.querySelector(".item-name").textContent;

            const data = await deleteProduct(productId);
            if (!data) return;

            item.classList.add("removing");
            setTimeout(() => {
                item.remove();
                updateEmptyState();

                document.getElementById("sum-subtotal").textContent = fmt(data.cart_total_price);
                document.getElementById("sum-total").textContent = fmt(data.cart_total_price);
                document.getElementById("cart-count").textContent = `سبد (${data.total_quantity})`;

                showToast(`"${name}" از سبد حذف شد`);
            }, 280);
        }
    });

    // Checkout
    document.getElementById("checkout-btn").addEventListener("click", () => {
        if (cartItemsEl.querySelectorAll(".cart-item").length === 0) return;
        showToast("در حال انتقال به درگاه پرداخت…");
    });

    updateEmptyState();
}