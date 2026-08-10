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