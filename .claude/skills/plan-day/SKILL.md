---
name: plan-day
description: Coach the user through one day of their acme-copilot study plan. Use whenever the user names a date (e.g. "nov 10", "10th november", "let's do 17 Nov") and asks for help with that day's project work, scope, tasks or session, or says "move on to <date>" / "next day's project". Looks up that date's Project rows in the plan CSV, writes an engaging study note for theory to-dos, and walks through implementation to-dos with code blocks and explanations, without editing project code.
---

# Plan day

The user is working through a 3-month FDE / SDE-2/3 plan. The plan lives in
`FDE_SDE_Plan_Nov-Jan.xlsx - Plan.csv` at the repo root. The user learns by doing it
themselves, so this skill teaches and guides. It does not do the work for them.

## 1. Find the day's tasks

Read the CSV. The real header is on line 8:
`#, Date, Day, Week, Phase, Track, Session / theme, To-do, Difficulty, Est. time, Resource 1-3, Status, Notes`.
Dates look like `10 Nov 2026`. Pick out the rows for that date where `Track == Project`.
Note the other tracks (DSA, System design, LLD) for that date too, but only list them at the
end; the user asked about the project.

Before writing anything, check where the project stands today: read `DEVLOG.md` and the code
files the tasks touch. The guidance must fit the code as it is now (real function names, the
real prompt, the real model and SDK). Generic snippets that don't match the repo waste the
user's time. If an earlier task this one depends on looks unfinished, say so in one line.

## 2. Sort each to-do: theory or implementation

- **Theory**: reading, concepts, "write down", "sketch", "read the X guide". The output is
  understanding.
- **Implementation**: building, coding, running, testing, deploying, logging results. The
  output is a change to the repo.

A session often has both (e.g. "read the guide" and then "apply it"). Handle theory first so
the implementation builds on it.

## 3. Theory → write a study note

Write `notes/YYYY-MM-DD-<topic-slug>.md`. This is the one file the skill does create.

The goal is that the user actually reads to the end and remembers it. Dry summaries get
skimmed and forgotten, so make it engaging:

- **Open with a hook**: a short scenario, ideally at Acme Freight, where the concept saves
  the day or its absence causes a mess.
- **"30-second version"** near the top, for the user to revisit later.
- **Explain the *why***, not only the *what*: the mechanism behind the technique. Use
  analogies from everyday life or logistics.
- **Tie it to the user's own project**: their tickets, their prompt, their DEVLOG results.
  Concrete beats abstract.
- **Pitfalls / myths**: what people get wrong.
- **Short sections, headers, tables, a few small code or prompt snippets.** No wall of text.
- **A quick self-quiz** (3-5 questions) with answers hidden in `<details>` blocks.
- **"Predict before you run"**: if an implementation task follows, ask the user to write
  down predictions first. It makes the experiment stick.
- **Interview angle**: one or two lines on how this comes up in FDE / SDE interviews.
- **Further reading**: the resources named in the CSV row.

Accuracy matters more than flair. Don't invent statistics or quotes. If something depends on
the model or provider, say so.

## 4. Implementation → guide, don't edit

Don't edit project code. The user types it in themselves, because that's how they learn.
Give, in the reply:

- Numbered steps, each with a **goal**, the **code block**, and a short **why it works**.
- Code that fits the current files exactly (correct names, imports, paths).
- How to run it and what the user should see.
- A way to check it works (a test, a deliberate break, an expected output).
- Common mistakes for that step.
- A closing step to log results in `DEVLOG.md` (what to record).

If the user explicitly asks you to write the code ("give me code", "do it"), you may edit
then. This skill is only the default.

## 5. Reply shape

1. One line: the date, the session title, and its to-dos.
2. Theory: link to the note you wrote plus a 2-3 line teaser of what's in it.
3. Implementation walkthrough.
4. "Also on today's plan": other tracks for the date, one line each.
5. One line offering to review their results when they're done.
