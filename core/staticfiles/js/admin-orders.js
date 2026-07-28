function viewOrder(orderId) {
    window.location.href = `admin-order-details.html`;
}

// Keep your previous filter and search functions
function filterOrders() {
    // For now, just a simple alert (you can enhance it later)
    alert("فیلتر اعمال شد (در نسخه پیشرفته جدول به‌روزرسانی می‌شود)");
}

function resetFilters() {
    document.getElementById("searchInput").value = "";
    document.getElementById("statusFilter").value = "";
    alert("فیلترها پاک شدند");
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    searchInput.addEventListener("input", () => {
        console.log("جستجو:", searchInput.value);
    });
});
