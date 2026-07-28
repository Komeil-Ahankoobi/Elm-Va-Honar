"use strict";

/* ----------------------------------------------------------
       PASSWORD TOGGLE
    ---------------------------------------------------------- */
(function initPwdToggle() {
    const toggle = document.getElementById("pwd-toggle");
    const input = document.getElementById("password");
    const icon = document.getElementById("eye-icon");
    if (!toggle || !input) return;

    let visible = false;

    toggle.addEventListener("click", () => {
        visible = !visible;
        input.type = visible ? "text" : "password";
        toggle.setAttribute("aria-label", visible ? "مخفی کردن رمز عبور" : "نمایش رمز عبور");
        // Switch icon between eye-open and eye-slash
        icon.innerHTML = visible
            ? `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/><line x1="2" y1="2" x2="14" y2="14" stroke-linecap="round"/>`
            : `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/>`;
    });
})();

/* ----------------------------------------------------------
       FORM VALIDATION + SUBMIT
    ---------------------------------------------------------- */
(function initForm() {
    const form = document.getElementById("login-form");
    const emailInput = document.getElementById("email");
    const pwdInput = document.getElementById("password");
    const emailError = document.getElementById("email-error");
    const pwdError = document.getElementById("password-error");
    const loginBtn = document.getElementById("login-btn");
    const loginCard = document.getElementById("login-card");
    const successState = document.getElementById("success-state");
    if (!form) return;

    function validateEmail(val) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim());
    }

    function setError(input, errorEl, show) {
        input.classList.toggle("error", show);
        errorEl.classList.toggle("visible", show);
        input.setAttribute("aria-invalid", show ? "true" : "false");
    }

    // Live validation on blur
    emailInput.addEventListener("blur", () => {
        if (emailInput.value) setError(emailInput, emailError, !validateEmail(emailInput.value));
    });
    emailInput.addEventListener("input", () => {
        if (emailInput.classList.contains("error")) setError(emailInput, emailError, !validateEmail(emailInput.value));
    });

    pwdInput.addEventListener("blur", () => {
        if (pwdInput.value) setError(pwdInput, pwdError, pwdInput.value.length < 1);
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        const emailOk = validateEmail(emailInput.value);
        const pwdOk = pwdInput.value.length > 0;

        setError(emailInput, emailError, !emailOk);
        setError(pwdInput, pwdError, !pwdOk);

        if (!emailOk || !pwdOk) return;

        // Simulate async login
        loginBtn.classList.add("loading");
        loginBtn.disabled = true;

        setTimeout(() => {
            loginBtn.classList.remove("loading");
            // Hide form, show success
            form.style.display = "none";
            document.querySelector(".form-divider")?.remove();
            document.querySelector(".btn-ghost")?.remove();
            document.querySelector(".login-register")?.remove();
            successState.classList.add("visible");
        }, 1800);
    });
})();
