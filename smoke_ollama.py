import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",  # required by the client; Ollama ignores it
)

r = client.chat.completions.create(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    messages=[{"role": "user", "content": "Say hello in one word"}],
)
print(r.choices[0].message.content)