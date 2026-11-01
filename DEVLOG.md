# DEVLOG

## 2026-11-01 — scripts/hello.py (OpenAI)

- Switched `scripts/hello.py` from Anthropic to the OpenAI SDK (`gpt-4o-mini`, `max_tokens=300`, `temperature=1.0`).
- Prompt: Acme Freight support triage, user message "My parcel to Chennai is 4 days late and the box arrived crushed."
- Ran with `uv run scripts/hello.py`.
- Tokens in/out: **42 / 164** (prompt / completion)
