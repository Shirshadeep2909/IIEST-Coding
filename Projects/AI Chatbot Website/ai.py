"""Ollama inference without mutating stored conversation history."""
import os

import httpx
import ollama

PERSONALITIES = {
    "assistant": "You are a helpful AI assistant.",
    "coder": "You are an expert programming mentor. Explain code clearly.",
}


class AIError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message)
        self.status = status


def ask_ai(messages, mode="assistant"):
    if mode not in PERSONALITIES:
        raise ValueError("Unknown assistant mode")
    model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    client = ollama.Client(timeout=120)
    request_messages = [{"role": "system", "content": PERSONALITIES[mode]}]
    request_messages.extend(dict(message) for message in messages if message["role"] != "system")
    try:
        response = client.chat(model=model, messages=request_messages, stream=False)
    except httpx.TimeoutException as exc:
        raise AIError("Ollama took too long to respond. Please try again.", 504) from exc
    except (ConnectionError, httpx.RequestError) as exc:
        raise AIError("Cannot reach Ollama. Start it with 'ollama serve'.") from exc
    except ollama.ResponseError as exc:
        if exc.status_code == 404:
            raise AIError(f"Model '{model}' is unavailable. Run 'ollama pull {model}'.") from exc
        raise AIError("Ollama could not generate a reply. Check the Ollama server logs.", 502) from exc
    reply = response["message"]["content"]
    if not isinstance(reply, str) or not reply.strip():
        raise AIError("Ollama returned an empty reply. Please try again.", 502)
    return reply
