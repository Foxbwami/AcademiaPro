(function () {
  const messageSection = document.querySelector('.admin-message-wrapper');
  const msgPanel = document.getElementById('guestMsgThread');
  const sendBtn = document.getElementById('guestMsgSendBtn');
  const messageForm = document.getElementById('guestMessageForm');
  const msgInput = document.getElementById('guestMsgInput');
  const msgEmail = document.getElementById('guestMsgEmail');
  const msgStatus = document.getElementById('guestMsgStatus');

  if (!msgPanel || !sendBtn || !msgInput || !msgStatus || !messageForm) return;

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  const messagesUrl = messageSection?.dataset.messagesUrl;
  const sendUrl = messageSection?.dataset.sendUrl;
  if (!messagesUrl || !sendUrl) return;

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'page-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => toast.classList.remove('visible'), 4200);
    toast.addEventListener('transitionend', () => toast.remove());
  }

  function escapeHtml(value) {
    return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  function renderMessages(messages) {
    if (!messages || !messages.length) {
      msgPanel.innerHTML = '<div class="small text-muted">Your conversation with the admin will appear here.</div>';
      return;
    }
    msgPanel.innerHTML = messages.map((message) => {
      const classes = message.from_admin ? 'guest-bubble bot' : 'guest-bubble me';
      const time = message.timestamp ? '<div class="small text-muted mt-1">' + escapeHtml(message.timestamp) + '</div>' : '';
      return '<div class="' + classes + '">' + escapeHtml(message.content) + time + '</div>';
    }).join('');
    msgPanel.scrollTop = msgPanel.scrollHeight;
  }

  async function refreshGuestMessages() {
    try {
      const response = await fetch(messagesUrl, { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || 'Unable to load messages');
      renderMessages(data.messages || []);
    } catch (error) {
      msgPanel.innerHTML = '<div class="small text-muted">Your message history is temporarily unavailable. You can still send a new message below.</div>';
    }
  }

  async function sendGuestMessage() {
    const message = msgInput.value.trim();
    const email = msgEmail?.value.trim() || '';
    if (!message) {
      msgStatus.textContent = 'Please enter a message before sending.';
      msgInput.focus();
      return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending…';
    msgStatus.textContent = '';

    try {
      const response = await fetch(sendUrl, {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        body: JSON.stringify({ email, message })
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || 'Unable to send message');
      msgInput.value = '';
      msgStatus.textContent = data.message || 'Your message has been sent.';
      await refreshGuestMessages();
    } catch (error) {
      msgStatus.textContent = error.message || 'Unable to send your message. Please try again.';
      showToast('Unable to send your message. Please try again.');
    } finally {
      sendBtn.disabled = false;
      sendBtn.textContent = 'Send Message →';
    }
  }

  messageForm.addEventListener('submit', (event) => {
    event.preventDefault();
    sendGuestMessage();
  });
  msgInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) sendGuestMessage();
  });
  refreshGuestMessages();
})();