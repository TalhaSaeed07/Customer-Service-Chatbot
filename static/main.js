document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    const button = document.getElementById("send-button");
    const chatBox = document.getElementById("chat-box");

    // Function to send message
    async function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;

        // Display user message
        chatBox.innerHTML += `<div><strong>You:</strong> ${msg}</div><br>`;
        chatBox.scrollTop = chatBox.scrollHeight;
        input.value = "";

        // Add WhatsApp-style typing indicator
        const typingId = `typing-${Date.now()}`;
        chatBox.innerHTML += `
            <div id="${typingId}" class="typing-indicator">
                <strong>Bot</strong>
                <span class="typing-dots">
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </span>
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: msg })
            });

            const data = await res.json();

            // Replace typing with formatted bot reply (single-line)
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.outerHTML = `<div><strong>Bot:</strong> ${marked.parseInline(data.reply)}</div><br><br>`;
            }
        } catch (error) {
            console.error("Error:", error);
            const typingElement = document.getElementById(typingId);
            if (typingElement) {
                typingElement.outerHTML = `<div><strong>Bot:</strong> Couldn't connect to server.</div>`;
            }
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Send button click event
    button.addEventListener("click", sendMessage);

    // Enter key event
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
