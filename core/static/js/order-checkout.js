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

        applyDiscount(data.total_price, data.post_price);
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




// ================= ADD ADDRESS MODAL =================
(function () {
    const overlay = document.getElementById("add-address-modal-overlay");
    const trigger = document.getElementById("add-address-trigger");
    const closeBtn = document.getElementById("add-address-modal-close");
    const cancelBtn = document.getElementById("add-address-modal-cancel");
    const form = document.getElementById("add-address-form");
    const submitBtn = document.getElementById("add-address-modal-submit");
    const alertBox = document.getElementById("add-address-modal-alert");
    const cardsContainer = document.getElementById("address-cards-container");
    const noAddressMsg = document.getElementById("no-address-message");

    if (!overlay || !trigger || !form) return;

    function openModal() {
        clearErrors();
        overlay.classList.add("is-open");
        document.body.classList.add("modal-open");
        const firstInput = form.querySelector("#modal_address");
        if (firstInput) firstInput.focus();
    }

    function closeModal() {
        overlay.classList.remove("is-open");
        document.body.classList.remove("modal-open");
        form.reset();
        clearErrors();
    }

    function clearErrors() {
        alertBox.style.display = "none";
        alertBox.textContent = "";
        form.querySelectorAll(".field-error").forEach((el) => (el.textContent = ""));
        form.querySelectorAll("input, textarea").forEach((el) => el.classList.remove("input-error"));
    }

    function showFieldErrors(errors) {
        Object.keys(errors).forEach((field) => {
            const errEl = form.querySelector(`[data-error-for="${field}"]`);
            const inputEl = form.querySelector(`[name="${field}"]`);
            if (errEl) {
                errEl.textContent = errors[field].map((e) => e.message || e).join(" - ");
            }
            if (inputEl) {
                inputEl.classList.add("input-error");
            }
        });
    }

    function setLoading(isLoading) {
        submitBtn.disabled = isLoading;
        submitBtn.querySelector(".btn-text").style.display = isLoading ? "none" : "inline";
        submitBtn.querySelector(".btn-spinner").style.display = isLoading ? "inline-block" : "none";
    }

    function buildAddressCard(address, isFirst) {
        const label = document.createElement("label");
        label.className = "address-card" + (isFirst ? " selected" : "");
        label.style.cursor = "pointer";
        label.style.display = "block";

        label.innerHTML = `
            <div class="address-header">
                <div class="address-title-group">
                    <span class="address-title">آدرس ${address.state} - ${address.city}</span>
                    ${isFirst ? '<span class="badge-default">پیش‌فرض</span>' : ""}
                </div>
            </div>
            <div class="address-details">
                <div>${escapeHtml(address.address)}</div>
                <div>کدپستی: ${escapeHtml(address.zip_code)}</div>
            </div>
            <div class="address-radio" style="margin-top: 10px">
                <input type="radio" name="address_id" value="${address.id}" required />
            </div>
        `;
        return label;
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    function addNewAddressToList(address) {
        if (noAddressMsg) noAddressMsg.remove();

        const existingCards = cardsContainer.querySelectorAll(".address-card");
        const isFirst = existingCards.length === 0;

        const newCard = buildAddressCard(address, isFirst);
        cardsContainer.appendChild(newCard);

        // انتخاب خودکار آدرس تازه‌ساخته‌شده
        existingCards.forEach((card) => card.classList.remove("selected"));
        newCard.classList.add("selected");
        newCard.querySelector('input[type="radio"]').checked = true;
    }

    trigger.addEventListener("click", openModal);
    closeBtn.addEventListener("click", closeModal);
    cancelBtn.addEventListener("click", closeModal);

    overlay.addEventListener("click", function (e) {
        if (e.target === overlay) closeModal();
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && overlay.classList.contains("is-open")) {
            closeModal();
        }
    });

    // انتخاب هر کارت آدرس (چه قدیمی چه جدید) با کلیک
    cardsContainer.addEventListener("click", function (e) {
        const card = e.target.closest(".address-card");
        if (!card) return;
        cardsContainer.querySelectorAll(".address-card").forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        clearErrors();
        setLoading(true);

        const url = form.dataset.url;
        const csrf = form.dataset.csrf;
        const formData = new FormData(form);

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrf,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        })
            .then((res) => res.json().then((data) => ({ status: res.status, data })))
            .then(({ status, data }) => {
                setLoading(false);

                if (status === 200 && data.success) {
                    addNewAddressToList(data.address);
                    closeModal();
                } else if (data.errors) {
                    showFieldErrors(data.errors);
                } else {
                    alertBox.textContent = data.message || "خطایی رخ داد، دوباره تلاش کنید.";
                    alertBox.style.display = "block";
                }
            })
            .catch(() => {
                setLoading(false);
                alertBox.textContent = "ارتباط با سرور برقرار نشد. دوباره تلاش کنید.";
                alertBox.style.display = "block";
            });
    });
})();
