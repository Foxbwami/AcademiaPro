(function () {
  const slides = document.querySelectorAll('.testimonial-slide');
  const prevBtn = document.querySelector('.testimonial-prev');
  const nextBtn = document.querySelector('.testimonial-next');
  const dotsContainer = document.getElementById('testimonialDots');
  if (!slides.length || !dotsContainer) return;

  let current = 0;
  let interval = null;

  slides.forEach((slide, index) => {
    const dot = document.createElement('button');
    dot.type = 'button';
    dot.className = 'testimonial-dot' + (index === 0 ? ' active' : '');
    dot.setAttribute('aria-label', `Show testimonial ${index + 1}`);
    dot.addEventListener('click', () => showSlide(index));
    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll('.testimonial-dot');

  function updateSlides() {
    slides.forEach((slide, index) => {
      slide.classList.toggle('active', index === current);
    });
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === current);
    });
    // Update ARIA live region with brief announcement
    const live = document.getElementById('testimonialLive');
    if (live) {
      const slide = slides[current];
      const name = slide.querySelector('.testimonial-name')?.textContent?.trim() || '';
      const text = slide.querySelector('.testimonial-text')?.textContent?.trim() || '';
      const short = text.length > 120 ? text.slice(0, 117) + '…' : text;
      live.textContent = `Testimonial ${current + 1} of ${slides.length} by ${name}: ${short}`;
    }
  }

  function showSlide(index) {
    current = (index + slides.length) % slides.length;
    updateSlides();
  }

  function nextSlide() {
    showSlide(current + 1);
  }

  function prevSlide() {
    showSlide(current - 1);
  }

  function startAutoSlide() {
    if (interval) clearInterval(interval);
    interval = setInterval(nextSlide, 5000);
  }

  function handleVisibilityChange() {
    if (document.hidden) {
      clearInterval(interval);
      interval = null;
    } else {
      startAutoSlide();
    }
  }

  if (nextBtn) nextBtn.addEventListener('click', nextSlide);
  if (prevBtn) prevBtn.addEventListener('click', prevSlide);
  if (nextBtn) nextBtn.addEventListener('click', startAutoSlide);
  if (prevBtn) prevBtn.addEventListener('click', startAutoSlide);
  dots.forEach((dot) => dot.addEventListener('click', startAutoSlide));

  document.addEventListener('visibilitychange', handleVisibilityChange);
  updateSlides();
  startAutoSlide();

  // Pause on hover
  const carouselShell = document.querySelector('.testimonial-carousel-shell');
  if (carouselShell) {
    carouselShell.addEventListener('mouseenter', () => { if (interval) clearInterval(interval); });
    carouselShell.addEventListener('mouseleave', () => { startAutoSlide(); });
  }

  // Touch / swipe support for mobile
  let touchStartX = 0;
  let touchEndX = 0;
  const minSwipeDistance = 40;

  function handleTouchStart(e) {
    touchStartX = e.changedTouches ? e.changedTouches[0].screenX : e.screenX;
  }

  function handleTouchMove(e) {
    touchEndX = e.changedTouches ? e.changedTouches[0].screenX : e.screenX;
  }

  function handleTouchEnd() {
    const dist = touchEndX - touchStartX;
    if (Math.abs(dist) > minSwipeDistance) {
      if (dist < 0) {
        nextSlide();
      } else {
        prevSlide();
      }
      startAutoSlide();
    }
    touchStartX = 0; touchEndX = 0;
  }

  if (carouselShell) {
    carouselShell.addEventListener('touchstart', handleTouchStart, {passive: true});
    carouselShell.addEventListener('touchmove', handleTouchMove, {passive: true});
    carouselShell.addEventListener('touchend', handleTouchEnd);
  }

  // Keyboard accessibility: allow arrow keys to change slides when carousel is focused
  if (carouselShell) {
    carouselShell.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); nextSlide(); startAutoSlide(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); prevSlide(); startAutoSlide(); }
      if (e.key === 'Home') { e.preventDefault(); showSlide(0); startAutoSlide(); }
      if (e.key === 'End') { e.preventDefault(); showSlide(slides.length - 1); startAutoSlide(); }
    });
  }
})();
