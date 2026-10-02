"use strict";
(function () {
    const COLORS = {
        background: "#beaf92", 
        text: "#1c1c1c",       
        success: "#2e7d4f",
        warn: "#c2621f",       
        error: "#b3261e",      
    };
    const DURATION = 3000; 

    const style = document.createElement("style");
    style.textContent = `
        .site-toast-wrap{position:fixed;top:20px;left:50%;transform:translateX(-50%);
            z-index:99999;display:flex;flex-direction:column;gap:10px;align-items:center;
            pointer-events:none;width:max-content;max-width:calc(100vw - 32px)}
        .site-toast{pointer-events:auto;display:flex;align-items:center;gap:10px;
            background:var(--site-toast-bg,${COLORS.background});color:var(--site-toast-text,${COLORS.text});
            border-right:4px solid var(--toast-accent);padding:12px 16px;border-radius:10px;
            box-shadow:0 8px 24px rgba(0,0,0,.35);font-size:14px;line-height:1.6;
            font-family:inherit;direction:rtl;opacity:0;transform:translateY(-12px);
            transition:opacity .25s ease,transform .25s ease}
        .site-toast.show{opacity:1;transform:translateY(0)}
        .site-toast__icon{flex:none;width:22px;height:22px;border-radius:50%;
            background:var(--toast-accent);color:#fff;display:flex;align-items:center;
            justify-content:center;font-size:13px;font-weight:700}
        .site-toast--success{--toast-accent:var(--site-toast-success,${COLORS.success})}
        .site-toast--warn{--toast-accent:var(--site-toast-warn,${COLORS.warn})}
        .site-toast--error{--toast-accent:var(--site-toast-error,${COLORS.error})}
    `;
    document.head.appendChild(style);

    const ICONS = { success: "✓", warn: "!", error: "✕" };
    let wrap = null;

    window.siteToast = function (message, type) {
        type = ICONS[type] ? type : "success";
        if (!wrap) {
            wrap = document.createElement("div");
            wrap.className = "site-toast-wrap";
            wrap.setAttribute("role", "status");
            wrap.setAttribute("aria-live", "polite");
            document.body.appendChild(wrap);
        }

        const el = document.createElement("div");
        el.className = `site-toast site-toast--${type}`;

        const icon = document.createElement("span");
        icon.className = "site-toast__icon";
        icon.textContent = ICONS[type];

        const text = document.createElement("span");
        text.textContent = message;

        el.appendChild(icon);
        el.appendChild(text);
        wrap.appendChild(el);

        requestAnimationFrame(() => el.classList.add("show"));
        setTimeout(() => {
            el.classList.remove("show");
            setTimeout(() => el.remove(), 300);
        }, DURATION);
    };
})();