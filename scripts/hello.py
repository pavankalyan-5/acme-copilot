from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = """You are an internal triage classifier for Acme Freight support tickets.
Do not reply to the customer. Output ONLY this format:

Category: <delay | damage | lost | other> (list all that apply)
Priority: <low | medium | high>
Destination: <city or "unknown">
Missing info: <comma-separated list>
Next action: <one short sentence for the human agent>
"""

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=300,
    temperature=0.0,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": "My parcel to Chennai is 4 days late and the box arrived crushed.",
        },
    ],
)

print(resp.choices[0].message.content)
print("tokens in/out:", resp.usage.prompt_tokens, resp.usage.completion_tokens)
