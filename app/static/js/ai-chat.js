(function () {
  // support both a floating panel (embedded) and a dedicated AI page
  const fab = document.getElementById('globalAiFab');
  const panel = document.getElementById('globalAiPanel') || document.getElementById('aiPagePanel');
  const closeBtn = document.getElementById('globalAiClose') || document.getElementById('aiPageClose');
  const body = document.getElementById('globalAiBody') || document.getElementById('aiPageBody');
  const input = document.getElementById('globalAiInput') || document.getElementById('aiPageInput');
  const send = document.getElementById('globalAiSend') || document.getElementById('aiPageSend');

  if (!panel || !body || !input || !send) return;

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  function escapeHtml(value) {
    return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  function formatAiContent(text) {
    if (!text) return '';
    const escaped = escapeHtml(text).replace(/\r\n/g, '\n');
    return escaped
      .split(/\n{2,}/)
      .map((block) => {
        if (/^(?:[-*+] .+(?:\n(?:[-*+] .+))*)$/.test(block.trim())) {
          const items = block
            .trim()
            .split(/\n+/)
            .map((line) => `<li>${line.replace(/^[*-+] /, '')}</li>`)
            .join('');
          return `<ul>${items}</ul>`;
        }
        return `<p>${block.replace(/\n/g, '<br>')}</p>`;
      })
      .join('');
  }

  function createBubble(role, text, timestamp) {
    const isUser = role === 'user';
    const classes = isUser ? 'ai-msg me' : 'ai-msg bot';
    const ts = timestamp ? `<div class="ai-ts">${escapeHtml(timestamp)}</div>` : '';
    return `<div class="${classes}"><div class="ai-bubble">${formatAiContent(text)}</div>${ts}</div>`;
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'page-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => toast.classList.remove('visible'), 4200);
    toast.addEventListener('transitionend', () => toast.remove());
  }

  function autoGrow() {
    input.style.height = 'auto';
    input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
  }

  async function loadHistory() {
    try {
      const response = await fetch('/ai/chat/history', { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || 'Unable to load chat history');
      }

      const rows = data.messages || [];
      if (!rows.length) {
        body.innerHTML = createBubble('assistant', 'I am ready. Tell me your topic, deadline, level, service type, and word count, and I will guide you step by step.');
      } else {
        body.innerHTML = rows.map((message) => createBubble(message.role, message.content, message.timestamp)).join('');
      }
      body.scrollTop = body.scrollHeight;
    } catch (error) {
      showToast('Unable to load AI chat history.');
    }
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    send.disabled = true;
    send.textContent = 'Sending...';

    try {
      const response = await fetch('/ai/chat/send', {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        body: JSON.stringify({ message })
      });
      const data = await response.json();

      if (!response.ok || !data.ok) {
        throw new Error(data.error || 'Unable to send message');
      }

      input.value = '';
      autoGrow();
      await loadHistory();
      send.disabled = false;
      send.textContent = 'Send';
    } catch (error) {
      showToast('Unable to connect to the server.');
      send.disabled = false;
      send.textContent = 'Send';
    }
  }

  function openPanel() {
    panel.classList.remove('d-none');
    loadHistory();
  }

  function closePanel() {
    panel.classList.add('d-none');
  }

  if (fab) {
    fab.addEventListener('click', () => {
      if (panel.classList.contains('d-none')) {
        openPanel();
      } else {
        closePanel();
      }
    });
  }

  if (closeBtn) closeBtn.addEventListener('click', closePanel);

  document.addEventListener('click', (event) => {
    const clickedInside = panel.contains(event.target);
    const clickedFab = fab ? fab.contains(event.target) : false;
    if (!panel.classList.contains('d-none') && !clickedInside && !clickedFab) {
      closePanel();
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !panel.classList.contains('d-none')) {
      closePanel();
    }
  });

  input.addEventListener('input', autoGrow);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });

  autoGrow();
})();
