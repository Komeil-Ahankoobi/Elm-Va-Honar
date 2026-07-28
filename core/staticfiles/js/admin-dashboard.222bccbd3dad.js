// Draw bar chart
const data = [
    { label: "مهر", value: 58, type: "accent" },
    { label: "آبان", value: 72, type: "" },
    { label: "آذر", value: 65, type: "" },
    { label: "دی", value: 84, type: "" },
    { label: "بهمن", value: 91, type: "" },
    { label: "اسفند", value: 78, type: "gold" },
];

const max = Math.max(...data.map((d) => d.value));
const chart = document.getElementById("chart");

data.forEach((d) => {
    const pct = (d.value / max) * 100;
    const group = document.createElement("div");
    group.className = "bar-group";
    group.innerHTML = `
      <div class="bar-wrap" style="height:160px">
        <div class="bar-fill ${d.type}" style="height:${pct}%"></div>
      </div>
      <div class="bar-label">${d.label}<br><small style="font-size:0.6rem;color:#8a8494">${d.value}م</small></div>
    `;
    chart.appendChild(group);
});

(function () {
    var sidebar = document.getElementById("sidebar");
    var toggle = document.getElementById("menuToggle");
    var overlay = document.getElementById("sidebarOverlay");

    if (!sidebar || !toggle || !overlay) return;

    function openSidebar() {
        sidebar.classList.add("open");
        overlay.classList.add("active");
        toggle.setAttribute("aria-expanded", "true");
    }

    function closeSidebar() {
        sidebar.classList.remove("open");
        overlay.classList.remove("active");
        toggle.setAttribute("aria-expanded", "false");
    }

    toggle.addEventListener("click", function () {
        if (sidebar.classList.contains("open")) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    overlay.addEventListener("click", closeSidebar);

    var links = sidebar.querySelectorAll(".sidebar-link");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", closeSidebar);
    }

    window.addEventListener("resize", function () {
        if (window.innerWidth > 900) {
            closeSidebar();
        }
    });
})();
