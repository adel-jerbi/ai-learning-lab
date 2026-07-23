import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",  # required by the client; Ollama ignores it
)
#get the text from the user
text = input("Enter the text to review: ")

prompt = """
Your task involves reviewing a text enclosed within triple quotes. Your responsibility will be to:

- Correct grammatical errors
- Fix spelling mistakes
- Enhance readability and clarity
- Make the content more professional

```
{text}
```
"""
r = client.chat.completions.create(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    messages=[{"role": "user", "content": prompt.format(text=text)}],
)
print(r.choices[0].message.content)