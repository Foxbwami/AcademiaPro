(function () {
  const mobileMenuButton = document.getElementById('mobileMenuButton');
  const mobileDrawer = document.getElementById('mobileDrawer');
  const mobileDrawerOverlay = document.getElementById('mobileDrawerOverlay');
  const mobileDrawerClose = document.getElementById('mobileDrawerClose');

  if (!mobileMenuButton || !mobileDrawer || !mobileDrawerOverlay || !mobileDrawerClose) return;

  function getFocusableElements() {
    return Array.from(mobileDrawer.querySelectorAll('a, button, input, textarea, select, [tabindex]:not([tabindex="-1"])')).filter((el) => !el.hasAttribute('disabled'));
  }

  function trapFocus(event) {
    if (event.key !== 'Tab') return;
    const focusable = getFocusableElements();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey) {
      if (document.activeElement === first) {
        event.preventDefault();
        last.focus();
      }
    } else {
      if (document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  }

  function openDrawer() {
    mobileDrawer.classList.add('drawer-open');
    mobileDrawerOverlay.classList.add('drawer-active');
    mobileMenuButton.setAttribute('aria-expanded', 'true');
    mobileDrawerClose.focus();
    document.addEventListener('keydown', trapFocus, true);
  }

  function closeDrawer() {
    mobileDrawer.classList.remove('drawer-open');
    mobileDrawerOverlay.classList.remove('drawer-active');
    mobileMenuButton.setAttribute('aria-expanded', 'false');
    mobileMenuButton.focus();
    document.removeEventListener('keydown', trapFocus, true);
  }

  mobileMenuButton.addEventListener('click', openDrawer);
  mobileDrawerClose.addEventListener('click', closeDrawer);
  mobileDrawerOverlay.addEventListener('click', closeDrawer);

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && mobileDrawer.classList.contains('drawer-open')) {
      closeDrawer();
    }
  });
})();
