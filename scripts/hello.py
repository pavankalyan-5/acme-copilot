from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=300,
    temperature=1.0,
    system="You are a support triage assistant for Acme Freight, a logistics company.",
    messages=[{
        "role": "user",
        "content": "My parcel to Chennai is 4 days late and the box arrived crushed.",
    }],
)

print(resp.content[0].text)
print("tokens in/out:", resp.usage.input_tokens, resp.usage.output_tokens)