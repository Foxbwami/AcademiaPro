(function () {
  const panel = document.getElementById('aiPagePanel');
  const body = document.getElementById('aiPageBody');
  const input = document.getElementById('aiPageInput');
  const send = document.getElementById('aiPageSend');
  const closeBtn = document.getElementById('aiPageClose');
  const newChatBtn = document.getElementById('aiNewChat');
  const threadList = document.getElementById('aiThreadList');
  const fileInput = document.getElementById('aiFileInput');
  const attachmentTray = document.getElementById('aiAttachmentTray');
  const voiceBtn = document.getElementById('aiVoiceBtn');
  const modelSelect = document.getElementById('aiModelSelect');
  const tempRange = document.getElementById('aiTempRange');
  const tempValue = document.getElementById('aiTempValue');
  const systemPrompt = document.getElementById('aiSystemPrompt');
  const saveSettings = document.getElementById('aiSaveSettings');
  const regenerateBtn = document.getElementById('aiRegenerate');
  const stopBtn = document.getElementById('aiStop');
  const threadSearch = document.getElementById('aiThreadSearch');
  const sidebar = document.getElementById('aiSidebar');
  const sidebarToggle = document.getElementById('aiSidebarToggle');
  const sidebarClose = document.getElementById('aiSidebarClose');
  const sidebarScrim = document.getElementById('aiSidebarScrim');
  const themeSelect = document.getElementById('aiThemeSelect');
  const sidebarTheme = document.getElementById('aiSidebarTheme');

  if (!panel || !body || !input || !send) return;

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  let activeThreadId = null;
  let attachments = [];
  let recognition = null;
  let isRecording = false;
  let allThreads = [];

  function escapeHtml(value) {
    return String(value || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
  }

  function inlineFormat(text) {
    return escapeHtml(text)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  }

  function formatAiContent(text) {
    if (!text) return '';
    const normalized = String(text).replace(/\r\n/g, '\n').trim();
    const blocks = normalized.split(/\n{2,}/);
    return blocks.map((block) => {
      const trimmed = block.trim();
      if (/^```/.test(trimmed)) {
        return `<pre><code>${escapeHtml(trimmed.replace(/^```\w*\n?/, '').replace(/```$/, ''))}</code></pre>`;
      }
      if (/^#{1,3}\s+/.test(trimmed)) {
        return `<h3>${inlineFormat(trimmed.replace(/^#{1,3}\s+/, ''))}</h3>`;
      }
      if (/^(?:[-*+]\s+.+)(?:\n[-*+]\s+.+)*$/.test(trimmed)) {
        const items = trimmed.split(/\n+/).map((line) => `<li>${inlineFormat(line.replace(/^[-*+]\s+/, ''))}</li>`).join('');
        return `<ul>${items}</ul>`;
      }
      if (/^(?:\d+\.\s+.+)(?:\n\d+\.\s+.+)*$/.test(trimmed)) {
        const items = trimmed.split(/\n+/).map((line) => `<li>${inlineFormat(line.replace(/^\d+\.\s+/, ''))}</li>`).join('');
        return `<ol>${items}</ol>`;
      }
      return `<p>${inlineFormat(trimmed).replace(/\n/g, '<br>')}</p>`;
    }).join('');
  }

  function emptyState() {
    return `
      <div class="ai-empty-state">
        <h3>How can I help today?</h3>
        <p>Try uploading a brief, asking for an outline, or requesting pricing guidance.</p>
        <div class="ai-suggestion-grid">
          <button class="ai-suggestion" type="button">Help me prepare an order brief</button>
          <button class="ai-suggestion" type="button">Summarize my uploaded file</button>
          <button class="ai-suggestion" type="button">Create a step-by-step study plan</button>
        </div>
      </div>`;
  }

  function createBubble(role, text, timestamp) {
    const isUser = role === 'user';
    const icon = isUser ? 'U' : '<i class="bi bi-stars" aria-hidden="true"></i>';
    const ts = timestamp ? `<div class="ai-ts">${escapeHtml(timestamp)}</div>` : '';
    return `<div class="ai-msg ${isUser ? 'me' : 'bot'}"><div class="ai-avatar">${icon}</div><div><div class="ai-bubble">${formatAiContent(text)}</div>${ts}</div></div>`;
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'page-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => toast.classList.remove('visible'), 3600);
    toast.addEventListener('transitionend', () => toast.remove());
  }

  function autoGrow() {
    input.style.height = 'auto';
    input.style.height = `${Math.min(input.scrollHeight, 170)}px`;
  }

  function renderAttachments() {
    if (!attachmentTray) return;
    attachmentTray.innerHTML = attachments.map((file, index) => `
      <span class="ai-attachment-pill"><i class="bi bi-file-earmark-text" aria-hidden="true"></i>${escapeHtml(file.name)} <button type="button" data-remove-file="${index}" class="btn-close" aria-label="Remove file"></button></span>
    `).join('');
    attachmentTray.classList.toggle('has-files', attachments.length > 0);
  }

  function renderThreads(threads) {
    if (!threadList) return;
    threadList.innerHTML = threads.length ? threads.map((thread) => `
      <button class="ai-thread-item ${thread.id === activeThreadId ? 'active' : ''}" type="button" data-thread-id="${escapeHtml(thread.id)}">
        <span class="ai-thread-title">${escapeHtml(thread.title)}</span>
        <span class="ai-thread-meta">${escapeHtml(thread.timestamp || 'Recent')}</span>
      </button>
    `).join('') : '<div class="ai-thread-empty">No chat history yet.</div>';
  }

  function filterThreads() {
    const query = (threadSearch?.value || '').trim().toLowerCase();
    const filtered = query ? allThreads.filter((thread) => String(thread.title || '').toLowerCase().includes(query)) : allThreads;
    renderThreads(filtered);
  }

  function setSidebar(open) {
    if (!sidebar || !sidebarToggle || !sidebarScrim) return;
    sidebar.classList.toggle('is-open', open);
    sidebarScrim.classList.toggle('is-active', open);
    sidebarToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  function applyTheme(theme) {
    const nextTheme = theme || 'system';
    document.body.classList.toggle('ai-theme-dark', nextTheme === 'dark');
    document.body.classList.toggle('ai-theme-light', nextTheme === 'light');
    if (themeSelect) themeSelect.value = nextTheme;
  }

  async function loadThreads() {
    if (!threadList) return;
    try {
      const response = await fetch('/ai/chat/threads', { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error('Thread load failed');
      activeThreadId = data.active_thread_id || activeThreadId;
      allThreads = data.threads || [];
      filterThreads();
    } catch (_error) {
      threadList.innerHTML = '<div class="ai-thread-error">Unable to load history.</div>';
    }
  }

  async function loadHistory(threadId) {
    try {
      const url = threadId ? `/ai/chat/history?thread_id=${encodeURIComponent(threadId)}` : '/ai/chat/history';
      const response = await fetch(url, { cache: 'no-store' });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || 'Unable to load chat history');
      activeThreadId = data.thread_id || activeThreadId;
      const rows = data.messages || [];
      body.innerHTML = rows.length ? rows.map((message) => createBubble(message.role, message.content, message.timestamp)).join('') : emptyState();
      body.scrollTop = body.scrollHeight;
      await loadThreads();
    } catch (_error) {
      showToast('Unable to load AI chat history.');
    }
  }

  function loadPreferences() {
    try {
      const prefs = JSON.parse(localStorage.getItem('ai_prefs') || '{}');
      if (modelSelect && prefs.model) modelSelect.value = prefs.model;
      if (tempRange && typeof prefs.temperature !== 'undefined') { tempRange.value = prefs.temperature; if (tempValue) tempValue.textContent = prefs.temperature; }
      if (systemPrompt && prefs.system_prompt) systemPrompt.value = prefs.system_prompt;
      applyTheme(prefs.theme || 'system');
    } catch (e) {
      applyTheme('system');
    }
  }

  async function startNewChat() {
    const response = await fetch('/ai/chat/new', { method: 'POST', headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {} });
    const data = await response.json();
    if (response.ok && data.ok) {
      activeThreadId = data.thread_id;
      attachments = [];
      renderAttachments();
      input.value = '';
      autoGrow();
      await loadHistory(activeThreadId);
    }
  }

  async function uploadFiles(files) {
    if (!files.length) return;
    const form = new FormData();
    Array.from(files).slice(0, 5).forEach((file) => form.append('files', file));
    if (activeThreadId) form.append('thread_id', activeThreadId);
    showToast('Reading uploaded file...');
    const response = await fetch('/ai/chat/upload', { method: 'POST', body: form, headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {} });
    const data = await response.json();
    if (!response.ok || !data.ok) {
      showToast(data.error || 'Unable to read file.');
      return;
    }
    attachments = attachments.concat(data.files || []).slice(0, 5);
    renderAttachments();
    showToast('File ready. Ask what you want me to do with it.');
  }

  async function sendMessage() {
    const message = input.value.trim();
    if (!message && !attachments.length) return;
    send.disabled = true;
    body.insertAdjacentHTML('beforeend', createBubble('user', message || 'Uploaded file for review'));
    body.scrollTop = body.scrollHeight;
    const pending = document.createElement('div');
    pending.className = 'ai-msg bot';
    pending.innerHTML = '<div class="ai-avatar"><i class="bi bi-stars" aria-hidden="true"></i></div><div><div class="ai-bubble"><p>Thinking through this carefully…</p></div></div>';
    body.appendChild(pending);
    body.scrollTop = body.scrollHeight;
    try {
      const payload = { message, attachments, thread_id: activeThreadId };
      if (modelSelect) payload.model = modelSelect.value;
      if (tempRange) payload.temperature = Number(tempRange.value);
      if (systemPrompt) payload.system_prompt = systemPrompt.value;
      const response = await fetch('/ai/chat/send', {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.error || 'Unable to send message');
      activeThreadId = data.thread_id || activeThreadId;
      input.value = '';
      attachments = [];
      renderAttachments();
      autoGrow();
      await loadHistory(activeThreadId);
    } catch (_error) {
      pending.remove();
      showToast('Unable to connect to the AI service.');
    } finally {
      send.disabled = false;
    }
  }

  async function regenerateLast() {
    if (!activeThreadId) return showToast('No conversation to regenerate.');
    try {
      const response = await fetch('/ai/chat/regenerate', {
        method: 'POST',
        headers: Object.assign({ 'Content-Type': 'application/json' }, csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
        body: JSON.stringify({ thread_id: activeThreadId })
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error('Regenerate failed');
      await loadHistory(activeThreadId);
    } catch (_e) {
      showToast('Unable to regenerate response.');
    }
  }

  async function stopGeneration() {
    if (!activeThreadId) return;
    try {
      await fetch('/ai/chat/stop', { method: 'POST', headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {}, body: JSON.stringify({ thread_id: activeThreadId }) });
      showToast('Stop request sent.');
    } catch (_e) {
      showToast('Unable to stop generation.');
    }
  }

  function setupVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!voiceBtn || !SpeechRecognition) {
      if (voiceBtn) voiceBtn.addEventListener('click', () => showToast('Voice input is not supported in this browser.'));
      return;
    }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results).map((result) => result[0].transcript).join(' ');
      input.value = `${input.value.replace(/\s*$/, '')} ${transcript}`.trim();
      autoGrow();
    };
    recognition.onend = () => {
      isRecording = false;
      voiceBtn.classList.remove('recording');
    };
    voiceBtn.addEventListener('click', () => {
      if (isRecording) {
        recognition.stop();
        return;
      }
      isRecording = true;
      voiceBtn.classList.add('recording');
      recognition.start();
    });
  }

  send.addEventListener('click', sendMessage);
  input.addEventListener('input', autoGrow);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
  if (newChatBtn) newChatBtn.addEventListener('click', startNewChat);
  if (closeBtn) closeBtn.addEventListener('click', () => {
    body.innerHTML = emptyState();
  });
  if (fileInput) fileInput.addEventListener('change', (event) => uploadFiles(event.target.files));
  if (attachmentTray) attachmentTray.addEventListener('click', (event) => {
    const index = event.target.getAttribute('data-remove-file');
    if (index !== null) {
      attachments.splice(Number(index), 1);
      renderAttachments();
    }
  });
  if (threadList) threadList.addEventListener('click', (event) => {
    const button = event.target.closest('[data-thread-id]');
    if (button) {
      loadHistory(button.getAttribute('data-thread-id'));
      setSidebar(false);
    }
  });
  body.addEventListener('click', (event) => {
    const suggestion = event.target.closest('.ai-suggestion');
    if (suggestion) {
      input.value = suggestion.textContent.trim();
      autoGrow();
      input.focus();
    }
  });

  setupVoice();
  autoGrow();
  loadPreferences();
  loadHistory();
  try { input.focus(); } catch (e) {}
  if (saveSettings) saveSettings.addEventListener('click', () => {
    const prefs = {
      model: modelSelect?.value || 'gpt-4',
      temperature: Number(tempRange?.value || 0.2),
      system_prompt: systemPrompt?.value || '',
      theme: themeSelect?.value || 'system'
    };
    try { localStorage.setItem('ai_prefs', JSON.stringify(prefs)); showToast('Preferences saved.'); } catch (e) { showToast('Unable to save preferences.'); }
  });
  if (regenerateBtn) regenerateBtn.addEventListener('click', regenerateLast);
  if (stopBtn) stopBtn.addEventListener('click', stopGeneration);
  if (tempRange) tempRange.addEventListener('input', () => { if (tempValue) tempValue.textContent = tempRange.value; });
  if (threadSearch) threadSearch.addEventListener('input', filterThreads);
  if (sidebarToggle) sidebarToggle.addEventListener('click', () => setSidebar(true));
  if (sidebarClose) sidebarClose.addEventListener('click', () => setSidebar(false));
  if (sidebarScrim) sidebarScrim.addEventListener('click', () => setSidebar(false));
  if (themeSelect) themeSelect.addEventListener('change', () => applyTheme(themeSelect.value));
  if (sidebarTheme) sidebarTheme.addEventListener('click', () => {
    const current = themeSelect?.value || 'system';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setSidebar(false);
  });
})();
