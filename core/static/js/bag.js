"use strict";

const fmt = (n) => "£" + n.toFixed(2).replace(/\.00$/, "");

const cartItemsEl = document.getElementById("cart-items");
const emptyEl = document.getElementById("cart-empty");
const toastEl = document.getElementById("toast");

let discountActive = false;
const DISCOUNT_RATE = 0.1;
const VALID_CODE = "QUILL10";

function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toastEl.classList.remove("show"), 2200);
}

function recalc() {
    const items = [...cartItemsEl.querySelectorAll(".cart-item")];
    let subtotal = 0;

    items.forEach((item) => {
        const price = parseFloat(item.dataset.price);
        const qty = parseInt(item.querySelector(".qty-val").textContent);
        const lineTotal = price * qty;
        item.querySelector(".item-price").textContent = fmt(lineTotal);
        subtotal += lineTotal;
    });

    document.getElementById("sum-subtotal").textContent = fmt(subtotal);

    let discount = 0;
    const discountRow = document.getElementById("discount-row");
    if (discountActive && subtotal > 0) {
        discount = subtotal * DISCOUNT_RATE;
        document.getElementById("sum-discount").textContent = "−" + fmt(discount);
        discountRow.style.display = "flex";
    } else {
        discountRow.style.display = "none";
    }

    const total = Math.max(subtotal - discount, 0);
    document.getElementById("sum-total").textContent = fmt(total);

    const checkoutBtn = document.getElementById("checkout-btn");
    const isEmpty = items.length === 0;
    emptyEl.classList.toggle("show", isEmpty);
    checkoutBtn.disabled = isEmpty;
    checkoutBtn.style.opacity = isEmpty ? "0.5" : "1";
    checkoutBtn.style.cursor = isEmpty ? "not-allowed" : "pointer";
}

cartItemsEl.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const item = btn.closest(".cart-item");
    const action = btn.dataset.action;
    const qtyEl = item.querySelector(".qty-val");
    let qty = parseInt(qtyEl.textContent);

    if (action === "inc") {
        qty = Math.min(qty + 1, 99);
        qtyEl.textContent = qty;
        recalc();
    } else if (action === "dec") {
        qty = Math.max(qty - 1, 1);
        qtyEl.textContent = qty;
        recalc();
    } else if (action === "remove") {
        const name = item.querySelector(".item-name").textContent;
        item.classList.add("removing");
        setTimeout(() => {
            item.remove();
            recalc();
            showToast(`Removed "${name}" from your bag`);
        }, 280);
    }
});

// Promo code
const promoInput = document.getElementById("promo-input");
const promoApply = document.getElementById("promo-apply");
const promoRow = document.getElementById("promo-row");
const promoApplied = document.getElementById("promo-applied");
const promoRemove = document.getElementById("promo-remove");

promoApply.addEventListener("click", () => {
    const code = promoInput.value.trim().toUpperCase();
    if (code === VALID_CODE) {
        discountActive = true;
        promoRow.style.display = "none";
        promoApplied.classList.add("show");
        recalc();
        showToast("Promo code applied — 10% off");
    } else if (code.length === 0) {
        showToast("Please enter a code");
    } else {
        showToast("That code is not valid");
    }
});

promoRemove.addEventListener("click", () => {
    discountActive = false;
    promoApplied.classList.remove("show");
    promoRow.style.display = "flex";
    promoInput.value = "";
    recalc();
});

// Gift note toggle
const giftToggle = document.getElementById("gift-toggle");
const giftNoteWrap = document.getElementById("gift-note-toggle");
giftNoteWrap.addEventListener("click", () => {
    giftToggle.classList.toggle("on");
});

// Checkout
document.getElementById("checkout-btn").addEventListener("click", () => {
    if (cartItemsEl.querySelectorAll(".cart-item").length === 0) return;
    showToast("Heading to secure checkout…");
});

// Suggested products → add to bag
document.querySelectorAll('[data-action="add-suggestion"]').forEach((btn) => {
    btn.addEventListener("click", () => {
        const card = btn.closest(".also-card");
        const id = card.dataset.id;
        const price = card.dataset.price;
        const name = card.dataset.name;
        const category = card.dataset.category;
        const img = card.dataset.img;

        // If already in cart, just bump quantity
        const existing = cartItemsEl.querySelector(`[data-id="${id}"]`);
        if (existing) {
            const qtyEl = existing.querySelector(".qty-val");
            qtyEl.textContent = parseInt(qtyEl.textContent) + 1;
        } else {
            const article = document.createElement("article");
            article.className = "cart-item";
            article.dataset.id = id;
            article.dataset.price = price;
            article.style.opacity = "0";
            article.style.transform = "translateY(10px)";
            article.innerHTML = `
            <div class="item-img-wrap"><img src="${img}" alt="${name}" /></div>
            <div class="item-body">
              <span class="item-category">${category}</span>
              <h3 class="item-name">${name}</h3>
              <span class="item-variant">Standard</span>
              <div class="item-controls">
                <div class="qty-stepper">
                  <button class="qty-btn" data-action="dec">−</button>
                  <span class="qty-val">1</span>
                  <button class="qty-btn" data-action="inc">+</button>
                </div>
                <span class="remove-link" data-action="remove">Remove</span>
              </div>
            </div>
            <div class="item-price-col">
              <span class="item-price">£${price}</span>
              <span class="item-unit-price">£${price} each</span>
            </div>`;
            cartItemsEl.appendChild(article);
            requestAnimationFrame(() => {
                article.style.transition = "opacity 0.4s ease, transform 0.4s ease";
                article.style.opacity = "1";
                article.style.transform = "translateY(0)";
            });
        }
        recalc();
        showToast(`Added "${name}" to your bag`);
    });
});

recalc();
