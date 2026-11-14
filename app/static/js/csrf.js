(function () {
  const originalFetch = window.fetch.bind(window);
  window.fetch = function (input, init) {
    const options = Object.assign({}, init || {});
    const method = String(options.method || (input && input.method) || "GET").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
      const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
      if (token) {
        const headers = new Headers(options.headers || (input && input.headers) || {});
        if (!headers.has("X-CSRFToken")) headers.set("X-CSRFToken", token);
        options.headers = headers;
      }
    }
    return originalFetch(input, options);
  };
})();
