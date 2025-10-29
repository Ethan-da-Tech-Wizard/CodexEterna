const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const imageInput = document.getElementById('imageUpload');
const uploadStatus = document.getElementById('uploadStatus');

const API = 'http://localhost:8000';

let sessionId = localStorage.getItem('mirandaSessionId');
if (!sessionId) {
  sessionId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}`;
  localStorage.setItem('mirandaSessionId', sessionId);
}

function appendMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.textContent = text;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Optional: thumb previews for uploaded images
function showThumbs(files) {
  const wrap = document.createElement('div');
  wrap.style.display = 'flex';
  wrap.style.gap = '6px';
  wrap.style.flexWrap = 'wrap';
  for (const f of files) {
    const url = URL.createObjectURL(f);
    const img = document.createElement('img');
    img.src = url;
    img.style.width = '72px';
    img.style.height = '72px';
    img.style.objectFit = 'cover';
    img.style.borderRadius = '6px';
    wrap.appendChild(img);
  }
  chatWindow.appendChild(wrap);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadHistory() {
  try {
    const r = await fetch(`${API}/history?session_id=${encodeURIComponent(sessionId)}`);
    if (!r.ok) return;
    const data = await r.json();
    const h = Array.isArray(data.history) ? data.history : [];
    chatWindow.innerHTML = '';
    for (const m of h) {
      const role = m.role === 'assistant' ? 'bot' : (m.role === 'user' ? 'user' : 'bot');
      appendMessage(role, m.content);
    }
  } catch {}
}

imageInput.addEventListener('change', async () => {
  const files = imageInput.files;
  if (!files || files.length === 0) return;

  showThumbs(files);

  const form = new FormData();
  form.append('session_id', sessionId);
  for (const f of files) form.append('files', f);

  try {
    const res = await fetch(`${API}/upload_image`, { method: 'POST', body: form });
    if (!res.ok) { uploadStatus.textContent = `Upload failed: ${res.status}`; return; }
    const data = await res.json();
    uploadStatus.textContent = data.message || 'Uploaded.';
    await loadHistory();
  } catch (e) {
    uploadStatus.textContent = `Upload error: ${e.message}`;
  } finally {
    imageInput.value = '';
  }
});

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage('user', message);
  userInput.value = '';

  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId })
    });
    if (!res.ok) { appendMessage('bot', `Server error: ${res.status}`); return; }
    const data = await res.json();
    appendMessage('bot', data.response || '[No response]');
  } catch (e) {
    appendMessage('bot', `Network error: ${e.message}`);
  }
});

loadHistory();
