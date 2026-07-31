document.addEventListener("DOMContentLoaded", function () {
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebarOverlay");
    var openBtn = document.getElementById("sidebarToggle");
    var closeBtn = document.getElementById("sidebarClose");

    if (!sidebar || !overlay || !openBtn) return;

    function openDrawer() {
        sidebar.classList.add("open");
        overlay.classList.add("active");
        document.body.style.overflow = "hidden";
        openBtn.setAttribute("aria-expanded", "true");
    }

    function closeDrawer() {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
        document.body.style.overflow = "";
        openBtn.setAttribute("aria-expanded", "false");
    }

    openBtn.addEventListener("click", openDrawer);
    if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
    overlay.addEventListener("click", closeDrawer);

    // Close on Escape
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && sidebar.classList.contains("open")) {
            closeDrawer();
        }
    });

    // Close the drawer whenever a nav link is tapped (mobile UX)
    sidebar.querySelectorAll(".nav-item").forEach(function (link) {
        link.addEventListener("click", closeDrawer);
    });

    // If the viewport grows past the mobile breakpoint, make sure
    // the drawer state/inline styles don't linger.
    window.addEventListener("resize", function () {
        if (window.innerWidth > 960) {
            closeDrawer();
        }
    });
});
