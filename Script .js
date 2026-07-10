const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");

function appendMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}-message`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = text;

    msgDiv.appendChild(bubble);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return msgDiv;
}

function showTyping() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot-message typing-indicator";
    typingDiv.id = "typingIndicator";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = "Assistant is typing...";
    typingDiv.appendChild(bubble);
    chatWindow.appendChild(typingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTyping() {
    const typingDiv = document.getElementById("typingIndicator");
    if (typingDiv) typingDiv.remove();
}

async function sendMessage(message) {
    if (!message.trim()) return;

    appendMessage(message, "user");
    userInput.value = "";
    showTyping();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message }),
        });
        const data = await res.json();
        removeTyping();

        if (data.error) {
            appendMessage("Sorry, something went wrong. Please try again.", "bot");
        } else {
            appendMessage(data.response, "bot");
        }
    } catch (err) {
        removeTyping();
        appendMessage("Unable to connect to the server. Please try again.", "bot");
    }
}

chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage(userInput.value);
});

function sendQuickMessage(text) {
    sendMessage(text);
}
