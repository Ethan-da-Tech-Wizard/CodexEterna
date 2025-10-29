/*
 * Miranda4 Frontend Script
 * ------------------------
 *
 * This JavaScript file wires up the chat interface on the client side.  It
 * listens for user input, sends messages to the backend API, handles
 * responses and errors, and appends messages to the chat window.  To
 * understand exactly how it works, read the comments on each line.
 */

// Grab a reference to the chat window where messages will be displayed.  This
// corresponds to the <div id="chatWindow"> element in index.html.
const chatWindow = document.getElementById('chatWindow');

// Grab the form element that wraps the input and send button.  We'll
// listen for its "submit" event to know when the user wants to send a
// message.
const chatForm = document.getElementById('chatForm');

// Grab the text input where the user types their message.  We'll read
// its ``value`` when sending a message and then clear it afterwards.
const userInput = document.getElementById('userInput');

// Add a submit event listener to the form.  We mark the callback as
// ``async`` because we'll be awaiting an HTTP request inside.
chatForm.addEventListener('submit', async (e) => {
  // Prevent the default browser behaviour of reloading the page on form
  // submission.  We'll handle everything via JavaScript instead.
  e.preventDefault();

  // Read the user's message from the input and trim whitespace from both
  // ends.  If it's empty, bail out and do nothing.
  const message = userInput.value.trim();
  if (!message) return;

  // Immediately append the user's message to the chat window so it shows
  // up in the interface.  ``appendMessage`` will handle formatting.
  appendMessage('user', message);

  // Clear the input box so the user can type a new message without
  // manually deleting the old text.
  userInput.value = '';

  try {
    // Send the message to the backend API.  We use fetch() with
    // ``method: 'POST'`` and set the Content-Type header to JSON.  The
    // body contains a JSON string with a single ``message`` property.
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    });

    // If the server returns a non‑2xx HTTP status, inform the user
    // something went wrong on the backend.  We include the status code in
    // the message for debugging purposes.
    if (!response.ok) {
      appendMessage('bot', `Server error: ${response.status}`);
      return;
    }

    // Parse the JSON body of the response.  ``await response.json()``
    // returns a JavaScript object, or throws if parsing fails.
    const data = await response.json();

    // Check that the response contains the expected ``response`` field.
    // If it does, display the bot's message.  Otherwise, show a default
    // error message and log the entire response to the console for
    // debugging.
    if (data && data.response) {
      appendMessage('bot', data.response);
    } else {
      appendMessage('bot', '[No response from server]');
      console.error('Unexpected response format:', data);
    }
  } catch (err) {
    // If the fetch itself rejects (e.g. network error), catch the
    // exception and show a network error message to the user.
    appendMessage('bot', `Network error: ${err.message}`);
  }
});

/**
 * Append a message to the chat window.
 *
 * @param {string} role   Who sent the message: 'user' or 'bot'.  This
 *                        determines the styling (see style.css).
 * @param {string} text   The message text to display.
 */
function appendMessage(role, text) {
  // Create a new <div> to hold the message.
  const msg = document.createElement('div');

  // Assign two CSS classes: "message" for base styles and the role
  // ('user' or 'bot') for role‑specific colours/alignment.
  msg.className = `message ${role}`;

  // Set the text content of the div.  Using textContent escapes any
  // HTML characters so user input can't inject markup.  If you want to
  // render markdown or HTML from the model, you could use innerHTML
  // instead, but be careful to sanitise to avoid XSS.
  msg.textContent = text;

  // Append the message to the bottom of the chat window.
  chatWindow.appendChild(msg);

  // Scroll the chat window to the bottom so the latest message is in view.
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
