(function () {
  const headerLinks = document.querySelector('.header-links');
  if (!headerLinks) return;

  headerLinks.querySelectorAll('a.nav-link').forEach((link) => {
    if (!link.hasAttribute('role')) {
      link.setAttribute('role', 'link');
    }
  });

  // Shrink header on scroll for premium sticky effect
  const siteHeader = document.querySelector('.site-header');
  if (siteHeader) {
    let lastScroll = 0;
    window.addEventListener('scroll', function () {
      const scY = window.scrollY || window.pageYOffset;
      if (scY > 80) {
        siteHeader.classList.add('scrolled');
      } else {
        siteHeader.classList.remove('scrolled');
      }
      lastScroll = scY;
    }, { passive: true });
  }
})();
