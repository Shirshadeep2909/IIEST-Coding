import ollama


def ask_ai(messages, mode="assistant"):

    personality = {

    "assistant":
    "You are a helpful AI assistant.",


    "coder":
    "You are an expert programming mentor. Explain code clearly.",

    }


    messages.insert(
        0,
        {
        "role":"system",
        "content":personality[mode]
        }
    )


    response = ollama.chat(

        model="llama3.2",

        messages=messages

    )


    return response["message"]["content"]