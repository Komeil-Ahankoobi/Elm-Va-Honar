function toggleSidebarMenu() {
    const sidebar = document.getElementById("appSidebar");
    const overlay = document.getElementById("sidebarOverlay");
    if (sidebar && overlay) {
        sidebar.classList.toggle("open");
        overlay.classList.toggle("active");
    }
}

function saveSettings(event) {
    event.preventDefault();
    alert("تغییرات با موفقیت ثبت شد.");
}
