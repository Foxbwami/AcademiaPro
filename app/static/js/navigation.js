(function () {
  const siteHeader = document.querySelector('.site-header');
  if (!siteHeader) return;

  const serviceToggle = document.getElementById('servicesDropdownBtn');
  if (serviceToggle) {
    serviceToggle.closest('.nav-dropdown')?.classList.add('services-nav-item');
  }

  let ticking = false;

  function updateHeader() {
    const currentScrollY = window.scrollY || window.pageYOffset || 0;
    siteHeader.classList.toggle('scrolled', currentScrollY > 40);
    siteHeader.classList.remove('scrolling-down');
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
