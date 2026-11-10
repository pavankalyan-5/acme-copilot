# Few-shot & Chain of Thought: Show, Then Think

*Study note · 10 Nov 2026 · Week 2: Prompting techniques*

---

## 🚚 Monday morning at Acme Freight

Two new support agents start on the same day.

**Agent A** gets a 4-page rulebook: *"Damage outranks delay. Billing disputes are medium.
Vague questions are 'other'…"* They read it and nod. By lunch they've tagged a "late and
soaked" parcel as `delay`, because the rulebook said damage outranks delay but they didn't
picture "soaked" as damage.

**Agent B** gets the same rulebook **plus three tickets a senior agent already handled**,
with the tags and the one-line notes they wrote. By lunch Agent B is writing summaries that
sound just like the senior's, and they keep the shipment ID in every one. Nobody told them to.

Then a really tricky ticket arrives: *"You charged me for express but it came 3 days late."*
Billing? Delay? Agent B, who **stops and thinks it through** (*"the customer's complaint is
the money, the lateness is the reason"*), gets it right. The agent who answers on reflex
doesn't.

That's today's lesson in two parts:

| Technique | What it does for the model | Agent analogy |
|---|---|---|
| **Few-shot** | *Shows* worked examples | The senior's past tickets |
| **Chain of thought** | Gives it room to *reason* before answering | Pausing to think it through |

---

## ⏱️ The 30-second version

- **Few-shot** = put 2-5 example inputs **with the ideal outputs** in the prompt. Great for
  teaching **format, tone and level of detail**, things that are hard to describe in rules.
- Good examples are **varied, realistic, and never taken from your test set**.
- **Chain of thought (CoT)** = let the model write out its reasoning **before** the answer.
  It helps on **judgment calls and multi-step problems**.
- CoT costs **output tokens**, which means more money and more latency. Don't use it on easy
  tasks.
- **Order matters:** reasoning *before* the answer helps. Reasoning *after* is just a
  justification of an answer already chosen.

---

## Part 1: Few-shot prompting

### Why it works

An LLM is a very powerful **pattern continuer**. When your prompt contains:

```
<ticket>A</ticket> → {"category": "damage", ...}
<ticket>B</ticket> → {"category": "other", ...}
<ticket>YOUR TICKET</ticket> → ???
```

…the most natural next thing to write is *another output in the same pattern*: same keys,
same tone, same length, same habits. This is called **in-context learning**. The model's
weights don't change; it picks up the pattern from what's in front of it, for the length of
that one request.

Rules tell the model **what** you want. Examples show it **what that looks like**. Some
things are much easier to show than to describe:

> Try writing a rule for "a good summary". *"Third person, concise, specific, keeps
> identifiers, doesn't editorialize, under 20 words…"* Now compare that with just showing one:
> `"Customer reports shipment AF-55102 to Surat arrived a week late with a soaked carton."`
> The example carries ten rules at once.

### 🎯 Connect it to your DEVLOG

On 9 Nov you added the rule *"summary in third person"*. It worked, but it caused a side
effect: summaries **lost the shipment IDs and cities** (ticket 1 lost "AF-20391" and "Pune").
That's what usually happens when you fix one thing with a rule. An example that *shows* a
third-person summary that **also keeps the ID and city** fixes both at once. That's your
experiment today.

### The 5 rules of good examples

| # | Rule | Why | Acme example |
|---|---|---|---|
| 1 | **Varied** | The model copies what the examples have in common. 3 damage examples will make it lean toward `damage`. | Use one damage, one vague, one billing. |
| 2 | **Realistic** | Neat, made-up examples teach the model to expect neat input. | Include typos, "??", ALL CAPS anger. |
| 3 | **Cover your weak spots** | Examples are best spent where the rules are unclear. | Late and wet (the precedence rule), "any update??" (vague → other). |
| 4 | **Exact output format** | The model copies format character for character, including mistakes. | Valid JSON, exact keys, no extra text. |
| 5 | **Never from your test set** | Otherwise your eval checks *memory*, not *skill*. This is called **data leakage**. | Don't reuse any of the 10 tickets in `tickets_handwritten.txt`. |

### How to format them

**Option A: XML tags inside the system prompt** (the simplest; use this today)

```xml
<examples>
<example>
<ticket>Shipment AF-55102 to Surat came a week late and the carton was soaked through.</ticket>
{"category": "damage", "urgency": "high", "summary": "Customer reports shipment AF-55102 to Surat arrived a week late with a soaked carton."}
</example>
</examples>
```

The tags make clear where the examples end and the real ticket begins. That's the same
reason you already wrap the user's ticket in `<ticket>`.

**Option B: fake conversation turns**

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "<ticket>Shipment AF-55102 ...</ticket>"},
    {"role": "assistant", "content": '{"category": "damage", ...}'},  # pretend the model said this
    {"role": "user", "content": f"<ticket>{ticket}</ticket>"},  # the real one
]
```

This works well too, because the model sees "this is how *I* reply". Choose one per project
and use it consistently.

### ⚠️ Few-shot pitfalls

- **Copying surface details.** If every example mentions a city, the model may **make up**
  a city for a ticket that has none. Include an example with no city (your "any update??"
  example does this).
- **The last example has the most pull.** Models tend to lean toward the most recent example.
  Don't always end on the same category.
- **Token cost on every call.** 3 examples add roughly 150-250 input tokens to *every*
  request. Across 10,000 tickets a day, that adds up. Measure it.
- **Examples that contradict the rules.** If an example breaks one of your rules, the example
  usually wins. Check them against your `<rules>`.

---

## Part 2: Chain of thought

### Why "thinking out loud" helps

The model builds its answer **one token at a time**, and each token gets roughly the same
amount of computation. It can't pause and think quietly before the first word. Whatever
reasoning happens has to happen **in the text**.

So if the very first token it writes is the category, it had to decide *immediately*. If it
first writes:

> *"The customer mentions lateness and a crushed box. Damage outranks delay per the rules…"*

…then by the time it writes `"category"`, that reasoning is part of what it reads to produce
the answer. **The written reasoning is its scratch paper.**

> 🧮 Analogy: ask someone for 17 × 24 in their head, and they might say 418. Give them paper
> and they'll write 340 + 68 = 408. Same person, more working space.

### Three levels of CoT

| Level | Prompt | Use when |
|---|---|---|
| **Basic** | "Think step by step before answering." | Quick try, any task |
| **Guided** | "First, list every issue the customer mentions. Then apply the precedence rule. Then pick the urgency." | You know the right reasoning steps |
| **Structured** | "Reason inside `<thinking>` tags, then give the answer inside `<answer>` tags." | You need to separate the reasoning from the answer automatically |

### CoT inside JSON (your setup)

You use JSON mode, so the reasoning can go in a field. **Put it first:**

```json
{"reasoning": "...", "category": "...", "urgency": "...", "summary": "..."}
```

✅ `reasoning` first → the model thinks, *then* decides.
❌ `reasoning` last → the model decides, then explains its choice. It sounds convincing, but it
did nothing to help the decision.

Your `Triage` Pydantic model doesn't need to change. Pydantic **ignores extra fields by
default**, so `reasoning` is parsed and discarded. Print `raw` if you want to read it.

### When *not* to use CoT

- **Easy, clear-cut tasks.** "Office hours in Bengaluru?" → `other`. Thinking adds cost and
  nothing else.
- **Latency-sensitive paths.** A chat reply streaming to a customer gets slower with
  every reasoning token.
- **Reasoning models.** Some models (e.g. OpenAI's o-series, or Claude with extended
  thinking) already reason internally. Adding "think step by step" mostly duplicates that.
  `gpt-4o-mini` is *not* a reasoning model, so CoT can help it.
- **Don't treat the reasoning as the truth.** The written reasoning isn't guaranteed to be
  what actually produced the answer. It's useful for debugging, but it isn't proof.

---

## 🧩 How they combine

| | No CoT | With CoT |
|---|---|---|
| **No examples** | Your 9 Nov baseline | Better judgment, format may drift |
| **Few-shot** | Better format and style ← **today's main experiment** | Best on hard tickets, highest cost |

Rule of thumb: **few-shot fixes *how* it answers, CoT fixes *whether* it reasons correctly.**
Your current failures are mostly *how* (summaries losing details), so few-shot is the right
first fix.

---

## 🔮 Predict before you run

Write these down **before** today's experiment. Being wrong is where you learn the most.

1. With 3 examples, will accuracy on the original 10 tickets go up, down, or stay at 10/10?
2. Will summaries keep shipment IDs and cities again? How many of 10?
3. How many extra **input** tokens per call: about 50, 200 or 500?
4. On the new hard ticket *"charged for express but it came 3 days late"*, what will it pick,
   with and without CoT?

---

## 📝 Self-quiz

**Q1.** You pick your 3 few-shot examples from `tickets_handwritten.txt` and your score goes
to 10/10. Why is that score worthless?
<details><summary>Answer</summary>
Data leakage: the model has seen those exact tickets with their answers in the prompt. You're
testing whether it can copy, not whether it can generalize. Examples must be separate from
the test set.
</details>

**Q2.** All 3 of your examples are `damage` tickets. What do you expect to happen?
<details><summary>Answer</summary>
A bias toward `damage`. The model copies whatever the examples have in common, including
the label. Vary the categories.
</details>

**Q3.** Why is `{"category": ..., "reasoning": ...}` worse than
`{"reasoning": ..., "category": ...}`?
<details><summary>Answer</summary>
Tokens are generated in order. With category first, the decision is made before any
reasoning exists. The reasoning afterwards only explains a choice already made.
</details>

**Q4.** Few-shot or CoT for "summaries keep losing shipment IDs"?
<details><summary>Answer</summary>
Few-shot. It's a format/style problem. Show summaries that keep the ID; reasoning won't help
here.
</details>

**Q5.** Your triage runs on 10,000 tickets a day. Your examples add 200 input tokens and CoT
adds 60 output tokens per call. Which costs more per day, and how do you decide whether
it's worth it?
<details><summary>Answer</summary>
Work it out: 2M extra input tokens vs 0.6M extra output tokens per day. Output tokens usually
cost several times more than input tokens, so look up the current prices before guessing.
Decide with evals: keep a technique only if it measurably improves accuracy on cases that
matter enough to justify the cost and latency.
</details>

---

## 💼 Interview angle

FDE interviews love the question *"the model gets X wrong, what do you try?"* A strong answer
works up a ladder: **clarify the rules → add few-shot examples → add CoT → change the model →
fine-tune**, and **measures each step with an eval**, with the cost and latency trade-off
stated. "I added examples and it felt better" is a weak answer. "Category accuracy went from
9/10 to 10/10, summaries kept IDs in 10/10 vs 4/10, and it cost +210 input tokens per call"
is a strong one.

---

## 📚 Further reading (from your plan)

- Anthropic: *Prompt engineering → Use examples (multishot prompting)*
- Anthropic: *Prompt engineering → Let Claude think (chain of thought)*
- Anthropic: *Use XML tags to structure your prompts* (you already use this)
