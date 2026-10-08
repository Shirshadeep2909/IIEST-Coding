import os
import secrets
import sqlite3
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request, session

from ai import AIError, PERSONALITIES, ask_ai
from database import ConversationChanged, create_database, load_messages, save_turn


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.environ.get("CHAT_DATABASE", str(Path(app.instance_path) / "chats.sqlite3")),
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
        MAX_CONTENT_LENGTH=32 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)
    if not app.config["SECRET_KEY"]:
        key_path = Path(app.instance_path) / "session.key"
        key_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with key_path.open("x") as key_file:
                key_path.chmod(0o600)
                key_file.write(secrets.token_hex(32))
        except FileExistsError:
            pass
        app.config["SECRET_KEY"] = key_path.read_text().strip()
    create_database(app.config["DATABASE"])

    def chat_id():
        if "chat_id" not in session:
            session["chat_id"] = uuid4().hex
        return session["chat_id"]

    @app.get("/")
    def home():
        chat_id()
        return render_template("index.html")

    @app.get("/history")
    def history():
        return jsonify(messages=load_messages(app.config["DATABASE"], chat_id()))

    @app.post("/new-chat")
    def new_chat():
        session["chat_id"] = uuid4().hex
        return jsonify(messages=[])

    @app.post("/chat")
    def chat():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Send a JSON object with message and mode."), 400
        message, mode = data.get("message"), data.get("mode", "assistant")
        if not isinstance(message, str) or not message.strip() or len(message) > 8000:
            return jsonify(error="Message must contain 1–8000 characters."), 400
        if not isinstance(mode, str) or mode not in PERSONALITIES:
            return jsonify(error="Choose assistant or coder mode."), 400
        message = message.strip()
        identity = chat_id()
        messages = load_messages(app.config["DATABASE"], identity)
        try:
            # Limit the history sent to the model to the most recent 20 turns.
            reply = ask_ai(messages[-40:] + [{"role": "user", "content": message}], mode)
            save_turn(app.config["DATABASE"], identity, message, reply, len(messages))
        except AIError as exc:
            return jsonify(error=str(exc)), exc.status
        except ConversationChanged:
            return jsonify(error="This chat changed while replying. Refresh and try again."), 409
        return jsonify(reply=reply)

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(error="Message is too large."), 413

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.exception("Chat database failure")
        return jsonify(error="Could not access chat history. Please try again."), 500

    return app


if __name__ == "__main__":
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")