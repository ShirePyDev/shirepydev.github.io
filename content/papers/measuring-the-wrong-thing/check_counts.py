"""Check the arithmetic behind my note on "Measuring the Wrong Thing" (Luo et al., 2026).

    git clone https://github.com/kuangren777/aap-audit
    python check_counts.py aap-audit

Standard library only. The authors released aggregate numbers, not per-prompt scores
or labels, so no AUROC can be recomputed from the release. This script reads the
released aggregates and checks that the counts quoted in the paper fit together.
Numbers marked "paper" are typed in from the arXiv v1 text.
"""
import json
import math
import re
import sys
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "aap-audit") / "results" / "aggregates"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def section(doc, title):
    return next(s["rows"] for s in doc["sections"] if s["title"] == title)


def interval(text):
    lo, hi = map(float, re.findall(r"-?\d*\.\d+", text)[-2:])
    return lo, hi


def mcnemar_exact(b, c):  # two-sided exact binomial test on the discordant pairs
    n, k = b + c, min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


print("1. What the release contains")
levels = Counter(e["reproduction_level"] for e in load("manifest.json")["experiments"])
print(f"   experiments by reproduction level: {dict(levels)}")
print("   (no 'full analysis' entries: the per-prompt scores and labels are not released)")

print("\n2. The matched Llama cohort: 100 wrapped harmful goals, 27 successes, 73 failures (paper)")
rows = section(load("outcome_audit.json"), "Benign-budget deployment allocation")
successes, failures = 27, 73
for r in rows:
    s = round(r["successful_recall"] * successes)
    f = round(r["failed_recall"] * failures)
    print(f"   nominal {r['nominal_fpr']:.0%}: blocks {s}/{successes} successful and {f}/{failures} failed attacks;"
          f" {successes - s} jailbreaks pass")
blocked = round(0.148 * successes) + round(0.425 * failures)
print(f"   at 5%: admitted harm rate {successes - 4}/{100 - blocked} = {(successes - 4) / (100 - blocked):.3f} (paper 0.354)")
random_removed = 0.057 * successes
print(f"   random blocking at the achieved 5.7% removes {random_removed:.2f} successes; the score removes 4,"
      f" {4 / random_removed:.1f}x as many (paper: about 2.6x)")

print("\n3. Paired plain-versus-wrapped outcomes (McNemar, exact)")
# Llama: 5 plain successes, 27 wrapped; 23 of the 95 plain refusals flip to success,
# so 4 of the 5 plain successes stay successful and 1 flips to failure.
print(f"   Llama: 23 failure->success, 1 success->failure: p = {mcnemar_exact(23, 1):.1e} (paper 3e-6)")
print(f"   Mistral: 14 failure->success, 12 success->failure: p = {mcnemar_exact(14, 12):.2f} (paper 0.85)")

print("\n4. How the 27 Llama successes spread over the five wrapper families (20 goals each)")
print("   paper: three families have two successes each; 15.4% of the 27 x 73 = 1971 success-failure")
print("   pairs fall within one family")
fits = []
for a, b in combinations_with_replacement(range(21), 2):
    split = (2, 2, 2, a, b)
    if sum(split) == successes and a > 2 and b > 2:
        within = sum(k * (20 - k) for k in split)
        if round(100 * within / (successes * failures), 1) == 15.4:
            fits.append((sorted(split, reverse=True), within))
for split, within in fits:
    print(f"   only split that fits: {split} -> {within}/1971 = {within / 1971:.1%} within-family pairs")

print("\n5. Strong attacks on Llama (Table 2 and Table 8, after the checkpoint repair)")
strong = load("strong_attacks.json")
rates = section(strong, "Attack success rates")
total_lg3 = sum(r["n"] * float(r["lg3"].split("→")[1]) for r in rates)
total_q3 = sum(r["n"] * float(r["q3"].split("→")[1]) for r in rates)
print(f"   attacked successes implied by the two-decimal rates: {total_lg3:.0f} under Llama Guard 3 and about"
      f" {total_q3:.0f} under Qwen3 (paper: 325 of 354 and 123 of 133 pass the 5% filter)")
for r in rates:
    print(f"   {r['attack']:14s} n={r['n']:3d}  attacked success Llama Guard 3 {r['lg3'].split('→')[1]},"
          f" Qwen3 {r['q3'].split('→')[1]}")
below = []
for r in section(strong, "Outcome AUROC after checkpoint repair"):
    for judge in ("lg3", "q3"):  # the rubric column (sr) is excluded from inference by the authors
        lo, hi = interval(r[judge])
        if hi < 0.5:
            below.append(f"{r['attack']} ({'Llama Guard 3' if judge == 'lg3' else 'Qwen3'})")
print(f"   cells with the whole interval below 0.5: {len(below)} of 14: {', '.join(below)}")
print(f"   paper's design effect 9.3 over 23 cells leaves {23 / 9.3:.1f} independent units")

print("\n6. Target-native matrix (Table 1)")
cells = section(load("outcome_audit.json"), "Target-native score-by-generator matrix")
n_below = sum(interval(c["ci"])[1] < 0.5 for c in cells)
print(f"   {n_below} of {len(cells)} intervals lie below 0.5;"
      f" diagonal: " + ", ".join(f"{c['generator']} {c['ry']}" for c in cells if c["score_source"] == c["generator"]))
