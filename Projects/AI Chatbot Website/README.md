# 🤖 Shirsho AI - Local AI Chatbot

A ChatGPT-style AI assistant that I built using Python, Flask, and Ollama.

I made this project to understand how modern AI applications work — from sending user messages through a web interface to getting responses from a locally running Large Language Model (LLM). While building this project, I used documentation, tutorials, and AI tools (including ChatGPT) as learning resources to understand concepts, debug errors, and improve the implementation.

Instead of using paid APIs, this chatbot uses Ollama to run an open-source AI model locally on my computer.

---

## 🚀 Features

- ChatGPT-style interface
- Local AI responses using Ollama
- Conversation memory
- Coding assistant mode
- Modern dark-themed UI
- Markdown support for better formatted answers
- Runs completely locally without API costs

---

## 🛠️ Technologies Used

### Backend
- Python
- Flask

### AI
- Ollama
- Llama 3.2

### Frontend
- HTML
- CSS
- JavaScript

### Other
- SQLite (for storing chat data)

---

## 📂 Project Structure
AI-Assistant-Ollama

│
├── app.py # Flask backend
├── ai.py # AI response handling
├── database.py # Chat storage
│
├── templates/
│ └── index.html # Website interface
│
└── static/
├── style.css # UI design
└── script.js # Frontend logic

---

## ⚙️ How To Run

### 1. Install Ollama

Download Ollama and install it.

Pull the AI model:

ollama pull llama3.2


---

### 2. Install Python dependencies


pip install -r requirements.txt


---

### 3. Start Ollama


ollama serve
---

### 4. Run the chatbot

python app.py

Open:

http://127.0.0.1:5000/


---

## 📸 Screenshots

<img src="screenshots/chatbot.png" width="800">

<img src="screenshots/chatbot2.png" width="800">

---

## 📚 What I Learned

While building this project, I learned:

- How local LLMs can be used without paid services
- How to structure a full-stack Python project
- Basics of AI application development

---

## 🔮 Future Improvements

Some features I want to add later:

- PDF question-answering using RAG
- Voice input/output
- Better chat history management
- Deploying it online

---

## 👨‍💻 Author

Shirshadeep Sarkar

IIEST Shibpur

## Updated local setup and checks

Run `ollama serve`, then `ollama pull llama3.2`. In this project directory,
install `requirements.txt` and run `python app.py`. Debug mode is off by default;
set `FLASK_DEBUG=1` only when debugging locally. The Ollama Python client uses
`OLLAMA_HOST` if set; `OLLAMA_MODEL` overrides the default `llama3.2`.
Inference has a 120-second request timeout and uses the latest 20 chat turns.

Each browser session has separate history. Refresh restores that history;
**New Chat** starts a separate conversation. Old conversations remain in SQLite.
New data is stored in `instance/chats.sqlite3`, leaving the legacy
`database/chats.db` untouched. `CHAT_DATABASE` can override the database path.
A private signing key is generated in `instance/session.key`; retain it across
restarts, or supply `FLASK_SECRET_KEY`. Keep the instance directory private.

The UI serves bundled Marked 15.0.12 and DOMPurify 3.4.16 locally; their licenses
are included under `static/vendor`. No CDN is required at runtime.

Backend regression checks (mock inference; no model download required):

```sh
python -m unittest discover -s tests -v
```

Frontend regression checks with Node.js and jsdom installed outside the repository:

```sh
npm install --prefix /tmp/iiest-frontend-check jsdom
NODE_PATH=/tmp/iiest-frontend-check/node_modules node tests/frontend.cjs
```

For a real inference check, use the UI to send a message, verify a nonempty
reply, then refresh and confirm both messages remain. A missing model, stopped
Ollama service, or timeout should show an actionable error and preserve your
input for retry without saving a failed turn.
