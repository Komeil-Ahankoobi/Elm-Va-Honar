"use strict";

/* ----------------------------------------------------------
       PASSWORD TOGGLES (password1 + password2)
    ---------------------------------------------------------- */
function initPwdToggle(toggleId, inputId, iconId) {
    const toggle = document.getElementById(toggleId);
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!toggle || !input) return;

    let visible = false;

    toggle.addEventListener("click", () => {
        visible = !visible;
        input.type = visible ? "text" : "password";
        toggle.setAttribute("aria-label", visible ? "مخفی کردن رمز عبور" : "نمایش رمز عبور");
        icon.innerHTML = visible
            ? `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/><line x1="2" y1="2" x2="14" y2="14" stroke-linecap="round"/>`
            : `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/>`;
    });
}

initPwdToggle("pwd-toggle-1", "password1", "eye-icon-1");
initPwdToggle("pwd-toggle-2", "password2", "eye-icon-2");

/* ----------------------------------------------------------
       FORM VALIDATION
    ---------------------------------------------------------- */
(function initForm() {
    const form = document.getElementById("register-form");
    if (!form) return;

    const fields = {
        first_name: document.getElementById("first_name"),
        last_name: document.getElementById("last_name"),
        phone_number: document.getElementById("phone_number"),
        username: document.getElementById("username"),
        password1: document.getElementById("password1"),
        password2: document.getElementById("password2"),
        email: document.getElementById("email"),
    };
    const errors = {
        first_name: document.getElementById("first_name-error"),
        last_name: document.getElementById("last_name-error"),
        phone_number: document.getElementById("phone_number-error"),
        username: document.getElementById("username-error"),
        password1: document.getElementById("password1-error"),
        password2: document.getElementById("password2-error"),
        email: document.getElementById("email-error"),
    };

    function setError(key, show) {
        const input = fields[key];
        const errorEl = errors[key];
        if (!input || !errorEl) return;
        input.classList.toggle("error", show);
        errorEl.classList.toggle("visible", show);
        input.setAttribute("aria-invalid", show ? "true" : "false");
    }

    function validateEmail(val) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim());
    }

    function validatePhone(val) {
        return /^09\d{9}$/.test(val.trim());
    }

    // Live validation on blur for required text fields
    ["first_name", "last_name", "username"].forEach((key) => {
        fields[key].addEventListener("blur", () => {
            setError(key, fields[key].value.trim().length === 0);
        });
    });

    fields.phone_number.addEventListener("blur", () => {
        if (fields.phone_number.value) setError("phone_number", !validatePhone(fields.phone_number.value));
    });

    fields.email.addEventListener("blur", () => {
        if (fields.email.value) setError("email", !validateEmail(fields.email.value));
    });

    fields.password2.addEventListener("blur", () => {
        if (fields.password2.value) setError("password2", fields.password2.value !== fields.password1.value);
    });

    form.addEventListener("submit", (e) => {
        let valid = true;

        ["first_name", "last_name", "username"].forEach((key) => {
            const ok = fields[key].value.trim().length > 0;
            setError(key, !ok);
            if (!ok) valid = false;
        });

        const phoneOk = validatePhone(fields.phone_number.value);
        setError("phone_number", !phoneOk);
        if (!phoneOk) valid = false;

        const pwd1Ok = fields.password1.value.length > 0;
        setError("password1", !pwd1Ok);
        if (!pwd1Ok) valid = false;

        const pwd2Ok = fields.password2.value === fields.password1.value && fields.password2.value.length > 0;
        setError("password2", !pwd2Ok);
        if (!pwd2Ok) valid = false;

        if (fields.email.value) {
            const emailOk = validateEmail(fields.email.value);
            setError("email", !emailOk);
            if (!emailOk) valid = false;
        }

        if (!valid) {
            e.preventDefault();
            return;
        }

        const btn = document.getElementById("signup-btn");
        if (btn) {
            btn.classList.add("loading");
            btn.disabled = true;
        }
        // Form submits normally to the server from here
    });
})();
