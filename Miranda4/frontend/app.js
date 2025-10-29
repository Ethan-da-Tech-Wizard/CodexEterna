const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');

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
      body: JSON.stringify({ message })
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
      console.error('Unexpected response format:', data);
    }
  } catch (err) {
    appendMessage('bot', `Network error: ${err.message}`);
  }
});

function appendMessage(role, text) {
  const msg = document.createElement('div');
  msg.className = `message ${role}`;
  msg.textContent = text; // safe plain text

  // If you want HTML/Markdown rendering, swap with:
  // msg.innerHTML = text;

  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
