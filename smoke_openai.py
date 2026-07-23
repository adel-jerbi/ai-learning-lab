import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

r = client.chat.completions.create(
    model="gpt-4o-mini",  # cheap model for tests
    messages=[{"role": "user", "content": "Say hello in one word"}],
)
print(r.choices[0].message.content)