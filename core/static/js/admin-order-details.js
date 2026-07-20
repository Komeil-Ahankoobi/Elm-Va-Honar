// You can add interactivity here later (status change modal, print function, etc.)
function viewInvoice(orderId) {
    console.log(orderId);

    window.location.href = `admin-invoice.html`;
}

document.addEventListener("DOMContentLoaded", () => {
    console.log("Order Details page loaded successfully.");

    // Example: Print button functionality
    const printBtn = document.querySelector('button[onclick*="print"]');
    if (printBtn) {
        printBtn.addEventListener("click", () => {
            window.print();
        });
    }
});
