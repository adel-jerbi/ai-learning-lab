from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client; Ollama ignores it
)

r = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Say hello in one word"}],
)
print(r.choices[0].message.content)