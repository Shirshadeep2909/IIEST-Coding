const box = document.getElementById("msg");
const chat = document.getElementById("chat");
const mode = document.getElementById("mode");
const sendButton = document.getElementById("send-button");
const newChatButton = document.getElementById("new-chat");
let busy = false;
let ready = false;

function setBusy(value) {
    busy = value;
    sendButton.disabled = value || !ready;
    box.disabled = value || !ready;
    mode.disabled = value;
    newChatButton.disabled = value;
}

function addMessage(role, content) {
    chat.querySelector(".welcome")?.remove();
    const element = document.createElement("div");
    element.className = role === "assistant" ? "ai" : "user";
    if (role === "assistant") {
        element.innerHTML = DOMPurify.sanitize(marked.parse(content));
    } else {
        element.textContent = content;
    }
    chat.appendChild(element);
    chat.scrollTop = chat.scrollHeight;
    return element;
}

async function api(path, options = {}) {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request failed. Please try again.");
    return data;
}

function showError(message) {
    const element = document.createElement("div");
    element.className = "ai error";
    element.setAttribute("role", "alert");
    element.textContent = message;
    chat.appendChild(element);
}

async function send() {
    const text = box.value.trim();
    if (!text || busy || !ready) return;
    setBusy(true);
    const userMessage = addMessage("user", text);
    box.value = "";
    const loading = addMessage("assistant", "Thinking...");
    try {
        const data = await api("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: text, mode: mode.value})
        });
        loading.innerHTML = DOMPurify.sanitize(marked.parse(data.reply));
    } catch (error) {
        loading.remove();
        userMessage.remove();
        box.value = text;
        showError(error.message);
    } finally {
        setBusy(false);
        box.focus();
        chat.scrollTop = chat.scrollHeight;
    }
}

async function newChat() {
    if (busy) return;
    setBusy(true);
    try {
        await api("/new-chat", {method: "POST"});
        chat.replaceChildren();
        box.value = "";
        ready = true;
    } catch (error) {
        showError(error.message);
    } finally {
        setBusy(false);
        box.focus();
    }
}

async function loadHistory() {
    setBusy(true);
    try {
        const data = await api("/history");
        for (const message of data.messages) addMessage(message.role, message.content);
        ready = true;
    } catch (error) {
        showError("Could not load history. Refresh or start a new chat. " + error.message);
    } finally {
        setBusy(false);
    }
}

sendButton.addEventListener("click", send);
newChatButton.addEventListener("click", newChat);
box.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.isComposing) {
        event.preventDefault();
        send();
    }
});
loadHistory();
