async function validateCopon() {
    const inputBtn = document.querySelector(".promo-input");
    const btn = document.querySelector(".promo-apply");

    if (!inputBtn || !btn) return;

    try {
        const response = await fetch(btn.dataset.url, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": btn.dataset.csrf,
            },
            body: new URLSearchParams({
                code: inputBtn.value.trim(),
            }),
        });

        let data;
        try {
            data = await response.json();
        } catch {
            throw new Error("پاسخ نامعتبر از سرور دریافت شد");
        }

        if (!response.ok) {
            throw new Error(data.message || "خطایی رخ داد");
        }

        inputBtn.setCustomValidity("");

        if (typeof Toastify === "function") {
            Toastify({
                text: data.message,
                className: "info",
                style: { background: "green" },
            }).showToast();
        } else {
            alert(data.message);
        }

        applyDiscount(data.total_price, data.total_tax);
    } catch (error) {
        if (typeof Toastify === "function") {
            Toastify({
                text: error.message || "خطایی رخ داد",
                className: "error",
                style: { background: "red" },
            }).showToast();
        } else {
            alert(error.message || "خطایی رخ داد");
        }
    }
}

function applyDiscount(total_price, total_tax) {
    const summaryRows = document.querySelectorAll(".summary-box .summary-row .value");
    const totalPayElement = document.querySelector(".summary-total .total-price");

    if (summaryRows.length >= 2) {
        if (total_tax !== undefined && total_tax !== null) {
            summaryRows[1].innerHTML = total_tax;
            formatPriceInToman(summaryRows[1]);
        }
    }

    if (totalPayElement && total_price !== undefined && total_price !== null) {
        totalPayElement.innerHTML = total_price;
        formatPriceInToman(totalPayElement);
    }
}

function formatPriceInToman(element) {
    if (!element) return;
    let rawPrice = parseFloat(element.innerText.replace(/[^0-9.]/g, ""));
    if (isNaN(rawPrice)) return;

    let formatter = new Intl.NumberFormat("fa-IR");
    let formattedPrice = formatter.format(rawPrice);
    element.innerText = `${formattedPrice} تومان`;
}

document.addEventListener("DOMContentLoaded", function () {
    let priceElements = document.querySelectorAll(".formatted-price");
    priceElements.forEach((element) => formatPriceInToman(element));

    const promoBtn = document.querySelector(".promo-apply");
    if (promoBtn) {
        promoBtn.addEventListener("click", function (e) {
            e.preventDefault();
            validateCopon();
        });
    }

    const addressRadios = document.querySelectorAll('input[name="address_id"]');

    function clearAddressValidity() {
        addressRadios.forEach((radio) => radio.setCustomValidity(""));
    }

    addressRadios.forEach((radio) => {
        radio.addEventListener("invalid", function () {
            if (!this.checked && !document.querySelector('input[name="address_id"]:checked')) {
                this.setCustomValidity("لطفاً یکی از آدرس‌ها را انتخاب کنید");
            } else {
                this.setCustomValidity("");
            }
        });
        radio.addEventListener("change", clearAddressValidity);
    });

    const addressCards = document.querySelectorAll(".address-card");
    addressCards.forEach((card) => {
        card.addEventListener("click", function () {
            addressCards.forEach((c) => c.classList.remove("selected"));
            this.classList.add("selected");
            const radio = this.querySelector('input[type="radio"]');
            if (radio && !radio.checked) {
                radio.checked = true;
                radio.dispatchEvent(new Event("change", { bubbles: true }));
            }
            clearAddressValidity();
        });
    });

    const preSelected = document.querySelector(".address-card.selected input[type='radio']");
    if (preSelected) {
        preSelected.checked = true;
        clearAddressValidity();
    }
});
