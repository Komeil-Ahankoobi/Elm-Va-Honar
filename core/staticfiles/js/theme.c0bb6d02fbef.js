/* ============================================================
   THEME.JS — Dark / Light mode toggle
   The initial theme is already applied by a tiny inline snippet
   in <head> (before CSS loads, to avoid a flash). This file just
   wires up every .theme-toggle button on the page so the user can
   flip the theme, and remembers the choice in localStorage.
   ============================================================ */
(function () {
  "use strict";

  var STORAGE_KEY = "pq-theme";

  function getCurrentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
      btn.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      );
    });
  }

  function toggleTheme() {
    var next = getCurrentTheme() === "dark" ? "light" : "dark";
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (e) {
      /* localStorage unavailable (private mode, etc.) — theme just won't persist */
    }
    applyTheme(next);
  }

  document.addEventListener("DOMContentLoaded", function () {
    // Sync button state/labels with whatever the inline head script already set.
    applyTheme(getCurrentTheme());

    document.querySelectorAll(".theme-toggle").forEach(function (btn) {
      btn.addEventListener("click", toggleTheme);
    });

    // Keep in sync if the user changes OS-level theme and hasn't picked manually.
    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
        var saved = null;
        try {
          saved = localStorage.getItem(STORAGE_KEY);
        } catch (err) {}
        if (!saved) {
          applyTheme(e.matches ? "dark" : "light");
        }
      });
    }
  });
})();
