document.querySelectorAll('.related-products-section').forEach(section => {
    const track = section.querySelector('.products-grid');
    const nextBtn = section.querySelector('.next-btn');
    const prevBtn = section.querySelector('.prev-btn');

    nextBtn?.addEventListener('click', () => {
        track.scrollBy({ left: -220, behavior: 'smooth' });
    });

    prevBtn?.addEventListener('click', () => {
        track.scrollBy({ left: 220, behavior: 'smooth' });
    });
});

function filterProducts(selectedElemnt) {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);

    params.set(selectedElemnt.name, selectedElemnt.value);

    window.location.href = `${url.pathname}?${params.toString()}`;
}

function clearFilters() {
    window.location.href = window.location.pathname;
}

(function initPagination() {
    const links = document.querySelectorAll(".pagination a.page-link");
    if (!links.length) return;

    links.forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const linkUrl = new URL(link.href, window.location.origin);
            const targetPage = linkUrl.searchParams.get("page");

            const currentParams = new URLSearchParams(window.location.search);
            if (targetPage) {
                currentParams.set("page", targetPage);
            }

            window.location.href = `${window.location.pathname}?${currentParams.toString()}`;
        });
    });
})();

document.addEventListener('DOMContentLoaded', () => {
    const supportBtn = document.querySelector('.support-widget__btn');
    const footer = document.querySelector('footer');

    if (supportBtn && footer) {
        supportBtn.addEventListener('click', (e) => {
            e.preventDefault();
            footer.scrollIntoView({ behavior: 'smooth' });
        });
    }
});

// کلیک روی کارت محصول و افزودن به سبد در product-cards.js هندل می‌شه.