const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');

let sessionId = localStorage.getItem('mirandaSessionId');
if (!sessionId) {
  sessionId = (crypto && crypto.randomUUID) ? crypto.randomUUID() : `${Date.now()}`;
  localStorage.setItem('mirandaSessionId', sessionId);
}

const imageInput = document.getElementById('imageUpload');
const uploadStatus = document.getElementById('uploadStatus');

imageInput.addEventListener('change', async () => {
  const files = imageInput.files;
  if (!files || files.length === 0) return;
  const formData = new FormData();
  formData.append('session_id', sessionId);
  for (const file of files) {
    formData.append('files', file);
  }
  try {
    const response = await fetch('http://localhost:8000/upload_image', {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      uploadStatus.textContent = `Upload failed: ${response.status}`;
      return;
    }
    const data = await response.json();
    if (data && data.message) {
      uploadStatus.textContent = data.message;
      appendMessage('bot', data.message);
    } else {
      uploadStatus.textContent = 'Uploaded but no response from server.';
    }
    imageInput.value = '';
  } catch (err) {
    uploadStatus.textContent = `Upload error: ${err.message}`;
  }
});

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage('user', message);
  userInput.value = '';
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    if (!response.ok) {
      appendMessage('bot', `Server error: ${response.status}`);
      return;
    }
    const data = await response.json();
    if (data && data.response) {
      appendMessage('bot', data.response);
    } else {
      appendMessage('bot', '[No response from server]');
    }
  } catch (err) {
    appendMessage('bot', `Network error: ${err.message}`);
  }
});

function appendMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.textContent = text;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}