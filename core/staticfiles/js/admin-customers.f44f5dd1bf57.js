function addNewCustomer() {
    alert("فرم ثبت مشتری جدید باز شد");
}

function viewCustomer(id) {
    window.location.href = `admin-customer-details.html`
}

function filterCustomers() {
    alert("فیلتر اعمال شد");
}

function resetFilters() {
    alert("فیلترها پاک شدند");
}

// Simple live search
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    searchInput.addEventListener("input", () => {
        console.log("جستجو:", searchInput.value);
    });
});
