"use strict";

/* ----------------------------------------------------------
       STEP MANAGER
    ---------------------------------------------------------- */
const steps = {
    dots: [
        document.getElementById("step-1-dot"),
        document.getElementById("step-2-dot"),
        document.getElementById("step-3-dot"),
    ],
    panels: [document.getElementById("step-1"), document.getElementById("step-2")],
    current: 1,

    go(n) {
        // Deactivate all
        this.panels.forEach((p) => p.classList.remove("active"));
        this.dots.forEach((d) => {
            d.classList.remove("active");
        });

        // Mark completed dots
        this.dots.forEach((d, i) => {
            if (i + 1 < n) d.classList.add("completed");
            else d.classList.remove("completed");
        });

        // Activate current
        this.dots[n - 1]?.classList.add("active");
        this.panels[n - 1]?.classList.add("active");
        this.current = n;
    },
};

/* ----------------------------------------------------------
       VALIDATION HELPERS
    ---------------------------------------------------------- */
function setError(input, errorEl, show) {
    input.classList.toggle("error", show);
    input.classList.toggle("valid", !show && input.value.length > 0);
    if (errorEl) errorEl.classList.toggle("visible", show);
    input.setAttribute("aria-invalid", show ? "true" : "false");
}

function validateEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());
}

/* ----------------------------------------------------------
       PASSWORD TOGGLES
    ---------------------------------------------------------- */
function initPwdToggle(btnId, inputId, iconId) {
    const btn = document.getElementById(btnId);
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!btn || !input) return;
    let vis = false;
    btn.addEventListener("click", () => {
        vis = !vis;
        input.type = vis ? "text" : "password";
        btn.setAttribute("aria-label", vis ? "مخفی کردن رمز عبور" : "نمایش رمز عبور");
        icon.innerHTML = vis
            ? `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/><line x1="2" y1="2" x2="14" y2="14" stroke-linecap="round"/>`
            : `<path d="M1 8s2.5-5 7-5 7 5 7 5-2.5 5-7 5-7-5-7-5z"/><circle cx="8" cy="8" r="2"/>`;
    });
}

initPwdToggle("pwd-toggle1", "pwd1", "eye1");
initPwdToggle("pwd-toggle2", "pwd2", "eye2");

/* ----------------------------------------------------------
       PASSWORD STRENGTH METER
    ---------------------------------------------------------- */
(function initStrength() {
    const input = document.getElementById("pwd1");
    const segs = [1, 2, 3, 4].map((n) => document.getElementById("seg" + n));
    const label = document.getElementById("pwd-strength-label");
    if (!input) return;

    function score(v) {
        let s = 0;
        if (v.length >= 8) s++;
        if (/[A-Z]/.test(v)) s++;
        if (/[0-9]/.test(v)) s++;
        if (/[^A-Za-z0-9]/.test(v)) s++;
        return s;
    }

    const levels = [
        { cls: "weak", text: "خیلی ضعیف" },
        { cls: "weak", text: "ضعیف" },
        { cls: "medium", text: "متوسط" },
        { cls: "strong", text: "قوی" },
        { cls: "strong", text: "عالی" },
    ];

    input.addEventListener("input", () => {
        const s = input.value.length === 0 ? -1 : score(input.value);
        segs.forEach((seg, i) => {
            seg.className = "pwd-bar-seg";
            if (s >= 0 && i <= s - 1) seg.classList.add(levels[Math.min(s, 4)].cls);
        });
        label.textContent = s < 0 ? "رمز عبور را وارد کنید" : levels[Math.min(s, 4)].text;
        label.style.color = s < 0 ? "" : s <= 1 ? "#E74C3C" : s === 2 ? "#F39C12" : "#27AE60";
    });
})();

/* ----------------------------------------------------------
       LIVE VALIDATION — step 1 fields
    ---------------------------------------------------------- */
const fn = document.getElementById("firstname");
const ln = document.getElementById("lastname");
const em1 = document.getElementById("email1");

fn.addEventListener("blur", () => setError(fn, document.getElementById("firstname-error"), fn.value.trim().length < 1));
fn.addEventListener("input", () => {
    if (fn.classList.contains("error"))
        setError(fn, document.getElementById("firstname-error"), fn.value.trim().length < 1);
});

ln.addEventListener("blur", () => setError(ln, document.getElementById("lastname-error"), ln.value.trim().length < 1));
ln.addEventListener("input", () => {
    if (ln.classList.contains("error"))
        setError(ln, document.getElementById("lastname-error"), ln.value.trim().length < 1);
});

em1.addEventListener("blur", () => {
    if (em1.value) setError(em1, document.getElementById("email1-error"), !validateEmail(em1.value));
});
em1.addEventListener("input", () => {
    if (em1.classList.contains("error"))
        setError(em1, document.getElementById("email1-error"), !validateEmail(em1.value));
});

/* ----------------------------------------------------------
       STEP 1 → STEP 2
    ---------------------------------------------------------- */
document.getElementById("step1-next").addEventListener("click", () => {
    const fnOk = fn.value.trim().length > 0;
    const lnOk = ln.value.trim().length > 0;
    const emOk = validateEmail(em1.value);

    setError(fn, document.getElementById("firstname-error"), !fnOk);
    setError(ln, document.getElementById("lastname-error"), !lnOk);
    setError(em1, document.getElementById("email1-error"), !emOk);

    if (fnOk && lnOk && emOk) steps.go(2);
});

/* ----------------------------------------------------------
       STEP 2 BACK
    ---------------------------------------------------------- */
document.getElementById("step2-back").addEventListener("click", () => steps.go(1));

/* ----------------------------------------------------------
       STEP 2 → SUCCESS
    ---------------------------------------------------------- */
document.getElementById("step2-next").addEventListener("click", () => {
    const p1 = document.getElementById("pwd1");
    const p2 = document.getElementById("pwd2");
    const tc = document.getElementById("terms");
    const te = document.getElementById("terms-error");

    const p1Ok = p1.value.length >= 8;
    const p2Ok = p2.value === p1.value && p2.value.length > 0;
    const termsOk = tc.checked;

    setError(p1, document.getElementById("pwd1-error"), !p1Ok);
    setError(p2, document.getElementById("pwd2-error"), !p2Ok);
    te.classList.toggle("visible", !termsOk);

    if (!p1Ok || !p2Ok || !termsOk) return;

    const btn = document.getElementById("step2-next");
    btn.classList.add("loading");
    btn.disabled = true;

    // Mark step 3 in progress
    steps.dots[2].classList.add("active");

    setTimeout(() => {
        // Hide form, show success
        document.getElementById("step-2").classList.remove("active");
        document.querySelector(".step-indicator").style.display = "none";
        document.querySelector(".signup-eyebrow").style.display = "none";
        document.querySelector(".signup-gold-rule").style.display = "none";
        document.querySelector(".signup-title").style.display = "none";
        document.querySelector(".signup-subtitle").style.display = "none";

        steps.dots.forEach((d) => {
            d.classList.remove("active");
            d.classList.add("completed");
        });

        document.getElementById("success-state").classList.add("visible");
    }, 1800);
});
