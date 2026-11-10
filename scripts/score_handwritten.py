import csv

from triage import triage

tickets = open("data/tickets_handwritten.txt").read().splitlines()
expected = list(csv.DictReader(open("data/tickets_handwritten_expected.csv")))

both = 0
for ticket, exp in zip(tickets, expected):
    got = triage(ticket)
    ok = got.category == exp["category"] and got.urgency == exp["urgency"]
    both += ok
    print(
        f"{'✓' if ok else '✗'} {exp['line']:>2} {got.category}/{got.urgency} "
        f"(exp {exp['category']}/{exp['urgency']}) | {got.summary}"
    )

print(f"\nboth correct: {both}/{len(tickets)}")
