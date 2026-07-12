(function () {
  const msgFab = document.getElementById('guestMsgFab');
  const msgPanel = document.getElementById('guestMsgPanel');
  const sendBtn = document.getElementById('guestMsgSendBtn');
  const msgInput = document.getElementById('guestMsgInput');
  const msgEmail = document.getElementById('guestMsgEmail');
  const msgStatus = document.getElementById('guestMsgStatus');
  const msgThread = document.getElementById('guestMsgThread');
  const closeButtons = document.querySelectorAll('[data-close]');

  if (!msgFab || !msgPanel || !sendBtn || !msgInput || !msgStatus || !msgThread) return;

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'page-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => toast.classList.remove('visible'), 4200);
    toast.addEventListener('transitionend', () => toast.remove());
  }

  function renderMessages(messages) {
    if (!messages || !messages.length) {
      msgThread.innerHTML = '<div class="small text-muted">Start a conversation with admin.</div>';
      return;
    }

    msgThread.innerHTML = messages.map((message) => {
      const classes = message.from_admin ? 'guest-bubble bot' : 'guest-bubble me';
      const time = message.timestamp ? `<div class="small text-muted mt-1">${escapeHtml(message.timestamp)}</div>` : '';
      return `<div class="${classes}">${escapeHtml(message.content)}${time}</div>`;
    }).join('');
    msgThread.scrollTop = msgThread.scrollHeight;
  }

  function escapeHtml(value) {
    return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  async function refreshGuestMessages() {
    try {
      const response = await fetch('{{ url_for("main.guest_chat_messages") }}', { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || 'Unable to load messages');
      }
      renderMessages(data.messages || []);
    } catch (error) {
      showToast('Unable to connect to the server.');
    }
  }

  async function sendGuestMessage() {
    const message = msgInput.value.trim();
    const email = msgEmail?.value.trim() || '';

    if (!message) {
      msgStatus.textContent = 'Message cannot be empty.';
      return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';
    msgStatus.textContent = '';

    try {
      const response = await fetch('{{ url_for("main.guest_chat_send") }}', {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        body: JSON.stringify({ email, message })
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || 'Unable to send message');
      }
      msgInput.value = '';
      msgStatus.textContent = data.message || 'Message sent.';
      await refreshGuestMessages();
    } catch (error) {
      msgStatus.textContent = 'Network error. Try again.';
      showToast('Unable to connect to the server.');
    } finally {
      sendBtn.disabled = false;
      sendBtn.textContent = 'Send Message';
    }
  }

  function openPanel() {
    msgPanel.classList.remove('d-none');
    refreshGuestMessages();
  }

  function closePanel() {
    msgPanel.classList.add('d-none');
  }

  msgFab.addEventListener('click', function () {
    if (msgPanel.classList.contains('d-none')) {
      openPanel();
    } else {
      closePanel();
    }
  });

  closeButtons.forEach((button) => {
    button.addEventListener('click', function () {
      const target = document.getElementById(button.getAttribute('data-close'));
      if (target) target.classList.add('d-none');
    });
  });

  document.addEventListener('click', function (event) {
    if (!msgPanel.classList.contains('d-none') && !msgPanel.contains(event.target) && !msgFab.contains(event.target)) {
      closePanel();
    }
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && !msgPanel.classList.contains('d-none')) {
      closePanel();
    }
  });

  sendBtn.addEventListener('click', sendGuestMessage);
})();
