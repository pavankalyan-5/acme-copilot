# acme-copilot

Support copilot for Acme Freight (a fictional logistics company).
Learning project: LLM features with evals, guardrails and tracing.

## What it does (so far)

`scripts/triage.py` classifies a support ticket into JSON:

```bash
uv run scripts/triage.py "My parcel to Chennai is 4 days late and the box arrived crushed."
```
```json
{"category": "damage", "urgency": "high", "summary": "Customer reports a late parcel that arrived damaged."}
```

- `category`: delay | damage | lost | billing | other
- `urgency`: low | medium | high
- Output is validated with Pydantic; one automatic retry on invalid output.

## Setup

```bash
uv sync
echo "OPENAI_API_KEY=sk-..." > .env
```

## Development

```bash
uv run pytest         # unit tests (LLM is mocked, no API calls)
uv run ruff check .   # lint
uv run ruff format .  # format
```

See `DEVLOG.md` for experiments and results.
