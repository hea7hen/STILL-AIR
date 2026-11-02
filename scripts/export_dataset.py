"""Export one synthetic world to data/ so the "dataset" can be read and shown.

Nothing in Still Air is trained. The experiment generates a fresh world per seed
(stillair/world.py); this script writes one of them out as JSON and Markdown.

    python3 scripts/export_dataset.py            # seed 0 -> data/world_seed0.{json,md}
    python3 scripts/export_dataset.py --seed 3
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stillair.world import generate  # noqa: E402

ROLE_NOTE = {
    "chain_f1": "half of a two-hop chain (relation)",
    "chain_f2": "half of a two-hop chain (property)",
    "dangling_rel": "relation with no matching property (distractor)",
    "dangling_prop": "property of a look-alike name (decoy)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    a = ap.parse_args()

    w = generate(a.seed)
    os.makedirs(a.out, exist_ok=True)

    data = {
        "seed": w.seed,
        "sessions": [
            [{"text": f.text, "role": f.role, "chain": f.chain} for f in s] for s in w.sessions
        ],
        "questions": [
            {"text": q.text, "answer": q.answer, "kind": q.kind, "chain": q.chain} for q in w.questions
        ],
        "true_derived_claims": sorted(
            [{"subject": s, "path": list(p), "object": o} for s, p, o in w.valid_derived],
            key=lambda d: d["subject"],
        ),
    }
    jpath = os.path.join(a.out, f"world_seed{a.seed}.json")
    with open(jpath, "w") as f:
        json.dump(data, f, indent=2)

    n_facts = sum(len(s) for s in w.sessions)
    lines = [
        f"# Synthetic world, seed {a.seed}",
        "",
        "Nothing here is trained on. The agent is *told* the facts below, one session at a time, "
        "then asked the questions. Names are invented so the answers cannot come from real-world knowledge.",
        "",
        f"- {n_facts} facts across {len(w.sessions)} sessions",
        f"- {len(w.chain_questions())} two-hop questions and {len(w.control_questions())} one-hop control questions",
        f"- {len(w.valid_derived)} true combined facts that nobody ever states (the ground truth)",
        "",
        "## Sessions (what the agent is told)",
        "",
    ]
    for i, s in enumerate(w.sessions, 1):
        lines.append(f"### Session {i}")
        lines.append("")
        lines.append("| Fact | Role |")
        lines.append("|---|---|")
        for f in s:
            lines.append(f"| {f.text} | {ROLE_NOTE[f.role]} |")
        lines.append("")
    lines += ["## Questions (asked later)", "", "| Kind | Question | Correct answer |", "|---|---|---|"]
    for q in w.questions:
        lines.append(f"| {q.kind} | {q.text} | {q.answer} |")
    lines.append("")
    mpath = os.path.join(a.out, f"world_seed{a.seed}.md")
    with open(mpath, "w") as f:
        f.write("\n".join(lines))

    print(f"wrote {jpath}\nwrote {mpath}")


if __name__ == "__main__":
    main()
