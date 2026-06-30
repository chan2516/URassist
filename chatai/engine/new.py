from ollama import chat

MODEL = "llama3.2"
TEMPERATURE = 0

stream = chat(
    mode=MODEL,
    messages=[{"role": "user", "content": "who is narendra modi"}],
    options={"temperature": TEMPERATURE},
    stream=True,
)
for chunk in stream:
    print(chunk["message"]["CONTENT"], end="", flush=True)