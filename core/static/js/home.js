document.addEventListener("DOMContentLoaded", () => {
    /* ==========================================================================
       1. Functional Main Hero Slider
       ========================================================================== */
    const heroSlides = document.querySelectorAll(".hero__slide");
    const heroDots = document.querySelectorAll(".hero__dot");
    const heroPrevBtn = document.getElementById("heroPrev");
    const heroNextBtn = document.getElementById("heroNext");
    const heroContainer = document.getElementById("heroSlider");

    if (heroSlides.length > 0) {
        let currentHeroIndex = 0;
        let heroInterval;

        const updateHeroSlider = (index) => {
            heroSlides.forEach((slide, i) => {
                slide.classList.toggle("hero__slide--active", i === index);
            });
            heroDots.forEach((dot, i) => {
                dot.classList.toggle("hero__dot--active", i === index);
            });
            currentHeroIndex = index;
        };

        const nextHeroSlide = () => {
            const newIndex = (currentHeroIndex + 1) % heroSlides.length;
            updateHeroSlider(newIndex);
        };

        const prevHeroSlide = () => {
            const newIndex = (currentHeroIndex - 1 + heroSlides.length) % heroSlides.length;
            updateHeroSlider(newIndex);
        };

        const startHeroAutoPlay = () => {
            stopHeroAutoPlay();
            heroInterval = setInterval(nextHeroSlide, 4000);
        };

        const stopHeroAutoPlay = () => {
            if (heroInterval) clearInterval(heroInterval);
        };

        if (heroNextBtn) {
            heroNextBtn.addEventListener("click", () => {
                nextHeroSlide();
                startHeroAutoPlay();
            });
        }

        if (heroPrevBtn) {
            heroPrevBtn.addEventListener("click", () => {
                prevHeroSlide();
                startHeroAutoPlay();
            });
        }

        heroDots.forEach((dot) => {
            dot.addEventListener("click", (e) => {
                const index = parseInt(e.target.dataset.index, 10);
                if (!isNaN(index)) {
                    updateHeroSlider(index);
                    startHeroAutoPlay();
                }
            });
        });

        if (heroContainer) {
            heroContainer.addEventListener("mouseenter", stopHeroAutoPlay);
            heroContainer.addEventListener("mouseleave", startHeroAutoPlay);
        }

        // شروع پخش خودکار اسلایدر
        startHeroAutoPlay();
    }

    /* ==========================================================================
       2. Scroll Carousel Controllers (Categories & Special Offers)
       ========================================================================== */
    const setupCarouselScroll = (prevBtnId, nextBtnId, gridId) => {
        const prevBtn = document.getElementById(prevBtnId);
        const nextBtn = document.getElementById(nextBtnId);
        const grid = document.getElementById(gridId);

        if (!prevBtn || !nextBtn || !grid) return;

        // در چیدمان RTL جهت اسکرول برعکس می‌شود
        nextBtn.addEventListener("click", () => {
            grid.scrollBy({ left: -280, behavior: "smooth" });
        });

        prevBtn.addEventListener("click", () => {
            grid.scrollBy({ left: 280, behavior: "smooth" });
        });
    };

    // راه‌اندازی کاروسل دسته‌بندی‌ها و پیشنهادهای ویژه
    setupCarouselScroll("catPrev", "catNext", "catGrid");
    setupCarouselScroll("prodPrev", "prodNext", "prodGrid");

    /* ==========================================================================
       3. Mobile Navigation & Overlay Management
       ========================================================================== */
    const navToggle = document.getElementById("navToggle");
    const mainNav = document.getElementById("mainNav");
    const navOverlay = document.getElementById("navOverlay");
    const navClose = document.getElementById("navClose");

    const openNav = () => {
        if (mainNav) mainNav.classList.add("nav--open", "is-open");
        if (navOverlay) navOverlay.classList.add("nav__overlay--active", "is-active");
        if (navToggle) {
            navToggle.classList.add("header__hamburger--active");
            navToggle.setAttribute("aria-expanded", "true");
        }
        document.body.style.overflow = "hidden";
    };

    const closeNav = () => {
        if (mainNav) mainNav.classList.remove("nav--open", "is-open");
        if (navOverlay) navOverlay.classList.remove("nav__overlay--active", "is-active");
        if (navToggle) {
            navToggle.classList.remove("header__hamburger--active");
            navToggle.setAttribute("aria-expanded", "false");
        }
        document.body.style.overflow = "";
    };

    if (navToggle) {
        navToggle.addEventListener("click", () => {
            const isOpen =
                mainNav && (mainNav.classList.contains("nav--open") || mainNav.classList.contains("is-open"));
            if (isOpen) {
                closeNav();
            } else {
                openNav();
            }
        });
    }

    if (navClose) navClose.addEventListener("click", closeNav);
    if (navOverlay) navOverlay.addEventListener("click", closeNav);

    // بستن منو با دکمه Esc
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeNav();
    });

    // بستن منو هنگام تغییر سایز صفحه به دسکتاپ
    window.addEventListener("resize", () => {
        if (window.innerWidth > 768) closeNav();
    });
});
