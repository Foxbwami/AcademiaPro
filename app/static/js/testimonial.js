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
    interval = setInterval(nextSlide, 1000);
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
})();
