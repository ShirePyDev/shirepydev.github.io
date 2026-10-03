"""
Experiment A: does an injected email make the agent send the secret out?

Runs three injection styles x three positions, plus two controls, each
repeated `--repeats` times, against every model you pass. Writes one JSONL
line per trial and prints the counts behind the post's leak table. The post's
table of what the summaries said comes from reading them, not from this script.

    export OPENAI_API_KEY=sk-...
    python experiment_a.py --models gpt-4o-mini-2024-07-18 gpt-4o-2024-08-06 --repeats 20

Nothing is sent anywhere: send_email is a mock that only records its arguments.
The secret is a synthetic canary. See harness.py.
"""

import argparse
import datetime as dt
import json
import platform
import sys
from collections import defaultdict

import harness
import payloads

# Per-trial outcomes counted in the tables (see harness.score).
FLAGS = ["exfiltrated", "offpolicy_send", "token_disclosed",
         "sent_to_trusted", "replied", "mentioned_injection"]


def get_create():
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("openai not installed. Run: pip install openai")
    return OpenAI().chat.completions.create


def scenarios():
    for style in payloads.INJECTION_STYLES:
        for pos in payloads.POSITIONS:
            yield (f"{style}/{pos}", style, pos,
                   payloads.build_inbox(style, pos))
    yield ("control/clean", "control", "clean", payloads.clean_inbox())
    yield ("control/legit", "control", "legit",
           payloads.legitimate_instruction_inbox())


def row_of(res):
    """The blog table's row: the style, or the control kept separate."""
    return res.style if res.style != "control" else f"control:{res.position}"


def print_table(title, counts):
    print(f"\n=== {title} ===")
    print(f"{'model':26} {'row':30} {'n':>4} {'err':>4} "
          + " ".join(f"{f:>19}" for f in FLAGS))
    for key in sorted(counts):
        c = counts[key]
        print(f"{key[0]:26} {' / '.join(key[1:]):30} {c['n']:>4} {c['error']:>4} "
              + " ".join(f"{c[f]:>15}/{c['n']:<3}" for f in FLAGS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+",
                    default=["gpt-4o-mini-2024-07-18", "gpt-4o-2024-08-06"])
    ap.add_argument("--repeats", type=int, default=20)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-steps", type=int, default=5)
    ap.add_argument("--out", default="results_a.jsonl")
    args = ap.parse_args()

    try:
        import openai
        sdk = openai.__version__
    except Exception:
        sdk = "unknown"

    meta = {"experiment": "A",
            "run_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "openai_sdk": sdk, "python": platform.python_version(),
            "models": args.models, "repeats": args.repeats,
            "temperature": args.temperature, "max_steps": args.max_steps,
            "trusted_recipient": harness.TRUSTED_RECIPIENT,
            "attacker_recipient": harness.ATTACKER_RECIPIENT}

    # Never overwrite an earlier run: its numbers may already be published.
    try:
        fh = open(args.out, "x", encoding="utf-8")
    except FileExistsError:
        sys.exit(f"{args.out} already exists. Pass a new --out so earlier "
                 "results are kept.")

    create = get_create()
    print(json.dumps(meta))

    by_row = defaultdict(lambda: defaultdict(int))
    by_pos = defaultdict(lambda: defaultdict(int))

    with fh:
        fh.write(json.dumps({"meta": meta}) + "\n")
        for model in args.models:
            for scen, style, pos, inbox in scenarios():
                for r in range(args.repeats):
                    res = harness.run_trial(
                        create, model, inbox, payloads.USER_REQUEST,
                        scenario=scen, style=style, position=pos, repeat=r,
                        max_steps=args.max_steps, temperature=args.temperature,
                    )
                    fh.write(res.as_json() + "\n")
                    fh.flush()
                    keys = [(by_row, (model, row_of(res)))]
                    if style != "control":
                        keys.append((by_pos, (model, style, pos)))
                    for table, key in keys:
                        table[key]["n"] += 1
                        table[key]["error"] += int(bool(res.error))
                        for f in FLAGS:
                            table[key][f] += int(getattr(res, f))
                    marks = [f for f in FLAGS[:4] if getattr(res, f)]
                    print(f"{'ERR ' if res.error else 'ok  '} {model:26} {scen:24} "
                          f"r{r:<3} {' '.join(marks)} {res.error}")

    print_table("by model and blog-table row (controls kept separate)", by_row)
    print_table("by model, style and position (injected scenarios only)", by_pos)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
