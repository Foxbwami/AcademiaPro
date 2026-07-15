(function () {
  const siteHeader = document.querySelector('.site-header');
  if (!siteHeader) return;

  const serviceToggle = document.getElementById('servicesDropdownBtn');
  if (serviceToggle) {
    serviceToggle.closest('.nav-dropdown')?.classList.add('services-nav-item');
  }

  let lastScrollY = window.scrollY || window.pageYOffset || 0;
  let ticking = false;

  function updateHeader() {
    const currentScrollY = window.scrollY || window.pageYOffset || 0;
    const scrollingDown = currentScrollY > lastScrollY && currentScrollY > 90;
    const scrollingUp = currentScrollY < lastScrollY;

    siteHeader.classList.toggle('scrolled', currentScrollY > 40);
    siteHeader.classList.toggle('scrolling-down', scrollingDown);

    if (scrollingUp || currentScrollY <= 90) {
      siteHeader.classList.remove('scrolling-down');
    }

    lastScrollY = Math.max(currentScrollY, 0);
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(updateHeader);
      ticking = true;
    }
  }, { passive: true });

  updateHeader();
})();
