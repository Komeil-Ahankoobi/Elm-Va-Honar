async function validateCopon(url, copon) {
    const inputBtn = document.querySelector(".promo-input");
    const btn = document.querySelector(".promo-apply");

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

        Toastify({
            text: data.message,
            className: "info",
            style: { background: "blue" },
        }).showToast();

        applyDiscount(data.total_price, data.total_tax);
        
    } catch (error) {
        Toastify({
            text: error.message || "خطایی رخ داد",
            className: "error",
            style: { background: "red" },
        }).showToast();
    }
}

function applyDiscount(total_price, total_tax) {
    document.querySelector(".total-price").innerHTML = total_price;
    document.querySelector(".total-tax").innerHTML = total_tax;
    document.querySelector(".summary-total-value").innerHTML = total_price;

    formatPriceInToman(document.querySelector(".total-price"));
    formatPriceInToman(document.querySelector(".summary-total-value"));
    formatPriceInToman(document.querySelector(".total-tax"));
}

function formatPriceInToman(element) {
    let rawPrice = parseFloat(element.innerText);
    let formatter = new Intl.NumberFormat("fa-IR");
    let formattedPrice = formatter.format(rawPrice);
    element.innerText = `${formattedPrice} تومان`;
}

document.addEventListener("DOMContentLoaded", function () {
    let priceElements = document.querySelectorAll(".formatted-price");
    priceElements.forEach((element) => formatPriceInToman(element));
});

document.querySelector(".promo-apply").addEventListener("click", function (e) {
    e.preventDefault();
    validateCopon();
});
