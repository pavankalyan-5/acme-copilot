import sys
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
client = OpenAI()


class Triage(BaseModel):
    category: Literal["delay", "damage", "lost", "billing", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(max_length=150)


SYSTEM_PROMPT = """You classify Acme Freight support tickets.
Return ONLY a JSON object, no prose, no code fences:
{"category": "...", "urgency": "...", "summary": "..."}

<rules>
category: one of delay, damage, lost, billing, other
If several categories apply, pick the one with the biggest impact on the customer:
lost > damage > delay > billing > other
(e.g. late AND crushed = damage, because damaged goods hurt more than a late delivery)
Only choose lost if the customer says the parcel is missing or never arrived; vague questions are other.
urgency: high = damaged/lost goods or angry customer; medium = delay, billing disputes or double charges; low = questions
summary: one sentence, under 20 words, in third person (e.g. "Customer reports..."); never copy the customer's words
</rules>
"""


def call_model(messages: list[dict]) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=messages,
    )
    return resp.choices[0].message.content


def triage(ticket: str) -> Triage:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"<ticket>{ticket}</ticket>"},
    ]

    # 1. First attempt
    raw = call_model(messages)
    try:
        return Triage.model_validate_json(raw)
    except ValidationError as e:
        print(f"[retry] first output invalid: {raw}", file=sys.stderr)
        # 2. Show the model its bad reply  3. ...and the error
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {
                "role": "user",
                "content": f"Your output was invalid: {e}. Return corrected JSON only.",
            }
        )

    # 4. One retry; a second ValidationError is raised to the caller
    raw = call_model(messages)
    return Triage.model_validate_json(raw)


if __name__ == "__main__":
    result = triage(sys.argv[1])
    print(result.model_dump_json(indent=2))
