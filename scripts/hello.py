from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=300,
    temperature=1.0,
    messages=[
        {
            "role": "system",
            "content": "You are a support triage assistant for Acme Freight, a logistics company.",
        },
        {
            "role": "user",
            "content": "My parcel to Chennai is 4 days late and the box arrived crushed.",
        },
    ],
)

print(resp.choices[0].message.content)
print("tokens in/out:", resp.usage.prompt_tokens, resp.usage.completion_tokens)