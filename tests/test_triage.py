import pytest
from pydantic import ValidationError

import triage as triage_mod
from triage import Triage, triage

VALID = '{"category": "damage", "urgency": "high", "summary": "Customer reports a crushed box."}'
INVALID = '{"category": "damaged", "urgency": "high", "summary": "Customer reports a crushed box."}'


def fake_model(monkeypatch, replies):
    """Replace call_model with a fake that returns `replies` in order.
    Returns a list that records the messages sent on each call."""
    calls = []
    replies = iter(replies)

    def fake(messages):
        calls.append(list(messages))  # copy: triage() mutates the list later
        return next(replies)

    monkeypatch.setattr(triage_mod, "call_model", fake)
    return calls


def test_valid_parse(monkeypatch):
    calls = fake_model(monkeypatch, [VALID])

    result = triage("box arrived crushed")

    assert isinstance(result, Triage)
    assert result.category == "damage"
    assert result.urgency == "high"
    assert len(calls) == 1  # no retry needed


def test_invalid_twice_raises(monkeypatch):
    calls = fake_model(monkeypatch, [INVALID, INVALID])

    with pytest.raises(ValidationError):
        triage("box arrived crushed")

    assert len(calls) == 2  # tried once, retried once, gave up


def test_retry_recovers(monkeypatch):
    calls = fake_model(monkeypatch, [INVALID, VALID])

    result = triage("box arrived crushed")

    assert result.category == "damage"
    assert len(calls) == 2

    retry_messages = calls[1]
    assert retry_messages[-2] == {"role": "assistant", "content": INVALID}
    assert "Your output was invalid" in retry_messages[-1]["content"]
