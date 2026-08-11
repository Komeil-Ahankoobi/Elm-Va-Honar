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

    const paramsName = selectedElemnt.name;
    const paramsValue = selectedElemnt.value;

    params.set(paramsName, paramsValue);

    const newUrl = `${url.pathname}?${params.toString()}`;
    window.location.href = newUrl;
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

document.addEventListener("click", function (e) {
    const card = e.target.closest(".product-card[data-href], .related-card[data-href]");
    if (!card) return;

    if (
        e.target.closest(
            ".wishlist-btn, .wishlist-icon-btn, .btn-wishlist, .btn-add-cart, .btn-add-to-cart, .btn-card-add",
        )
    ) {
        return;
    }

    window.location.href = card.dataset.href;
});

document.addEventListener('DOMContentLoaded', () => {
  const supportBtn = document.querySelector('.support-widget__btn');
  const footer = document.querySelector('footer'); // اگر تگ فوتر شما اسم دیگری دارد، اینجا جایگزین کنید

  if (supportBtn && footer) {
    supportBtn.addEventListener('click', (e) => {
      e.preventDefault(); // جلوگیری از رفتار پیش‌فرض لینک (#)
      footer.scrollIntoView({
        behavior: 'smooth'
      });
    });
  }
});