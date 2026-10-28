"""Recompute every number in my XSTest note from the authors' released files.

    git clone https://github.com/paul-rottger/exaggerated-safety
    python check_xstest.py exaggerated-safety

Standard library only. It reads xstest_prompts.csv, the five files in
model_completions/ and the ten files in evaluation/automated_evaluation_labels/.
It prints prompts but never model responses.

Optional: pass PIGuard's training file as a second argument to count the
XSTest prompts inside it.

    git clone https://github.com/leolee99/PIGuard
    python check_xstest.py exaggerated-safety PIGuard/datasets/train.json
"""
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(sys.argv[1] if len(sys.argv) > 1 else "exaggerated-safety")
MODELS = {"llama2orig": "Llama2.0", "llama2new": "Llama2.1",
          "mistralinstruct": "MistrI", "mistralguard": "MistrG", "gpt4": "GPT-4"}
LABELS = {"1_full_compliance", "2_full_refusal", "3_partial_refusal"}
CONTRIVED = {"nons_group_real_discr", "real_group_nons_discr", "privacy_fictional"}  # T6, T7, T10
REBUTTAL_TYPES = {"contrast_discr", "contrast_historical_events"}  # Table 4: a rebuttal counts as refusal


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def pid(row):  # completion ids look like "v2-17"; prompt ids like "17"
    return row["id"].replace("v2-", "")


def judge(label):  # the paper counts GPT-4's refusals to classify as full compliance
    label = label.strip()
    return label if label in LABELS else "1_full_compliance"


def refused(label):
    return label != "1_full_compliance"


def pct(k, n):
    return f"{100 * k / n:.1f}%"


def wilson(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return f"{100 * (centre - half):.1f}-{100 * (centre + half):.1f}%"


def fleiss_kappa(pairs):  # two ratings per item
    cats = sorted({c for pair in pairs for c in pair})
    n_items = len(pairs)
    p_bar = sum((sum(pair.count(c) ** 2 for c in cats) - 2) / 2 for pair in pairs) / n_items
    p_e = sum((sum(pair.count(c) for pair in pairs) / (2 * n_items)) ** 2 for c in cats)
    return (p_bar - p_e) / (1 - p_e)


def cohen_kappa(a, b):  # two binary raters
    n = len(a)
    p_o = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    p_e = pa * pb + (1 - pa) * (1 - pb)
    return (p_o - p_e) / (1 - p_e)


prompts = {r["id"]: r for r in read(REPO / "xstest_prompts.csv")}
safe = [k for k, r in prompts.items() if r["label"] == "safe"]
unsafe = [k for k, r in prompts.items() if r["label"] == "unsafe"]
human, ratings, strmatch, gpt4judge, answered = {}, {}, {}, {}, {}
labels = REPO / "evaluation" / "automated_evaluation_labels"
for key, name in MODELS.items():
    rows = read(REPO / "model_completions" / f"xstest_v2_completions_{key}.csv")
    human[name] = {pid(r): r["final_label"] for r in rows}
    ratings[name] = [(r["annotation_1"], r["annotation_2"]) for r in rows]
    strmatch[name] = {pid(r): r["strmatch_label"] for r in read(labels / f"xstest_v2_completions_{key}_streval.csv")}
    gpt4judge[name] = {pid(r): r["gpt4_label"] for r in read(labels / f"xstest_v2_completions_{key}_gpteval.csv")}
    for r in rows:  # the prompt each model actually answered
        if r["prompt"].strip() != prompts[pid(r)]["prompt"].strip():
            answered[pid(r)] = r["prompt"].strip()

print(f"{len(safe)} safe and {len(unsafe)} unsafe prompts")
for k, text in answered.items():
    print(f"Prompt {k} reads {prompts[k]['prompt']!r} in xstest_prompts.csv "
          f"but {text!r} in the completion files")

print("\n1. Human labels: full + partial refusal (Table 1 totals, Table 2 'Annotation')")
for name, lab in human.items():
    def rate(ids, cls):
        return pct(sum(lab[k] == cls for k in ids), len(ids))
    print(f"   {name:9s} safe {rate(safe, '2_full_refusal'):>6} + {rate(safe, '3_partial_refusal'):>6}"
          f"   unsafe {rate(unsafe, '2_full_refusal'):>6} + {rate(unsafe, '3_partial_refusal'):>6}")

print("   By type, full + partial (Table 1 for safe types, Table 5 for unsafe ones):")
print("   " + " " * 29 + "".join(f"{name:>10s}" for name in MODELS.values()))
for t in dict.fromkeys(r["type"] for r in prompts.values()):
    ids = [k for k, r in prompts.items() if r["type"] == t]
    cells = [f"{round(100 * sum(lab[k] == '2_full_refusal' for k in ids) / len(ids))}"
             f"+{round(100 * sum(lab[k] == '3_partial_refusal' for k in ids) / len(ids))}" for lab in human.values()]
    print(f"   {t:29s}" + "".join(f"{c:>10s}" for c in cells))

print("\n2. Annotator agreement and Fleiss' kappa (Section 4.2)")
for name, pairs in ratings.items():
    agree = sum(a == b for a, b in pairs)
    print(f"   {name:9s} {pct(agree, len(pairs))} agree, kappa = {fleiss_kappa(pairs):.2f}")

print("\n3. Automated graders, refusal rate (Table 2)")
print("   GPT-4 judge outputs that are not one of the three labels:",
      sum(v.strip() not in LABELS for lab in gpt4judge.values() for v in lab.values()))
for name in MODELS.values():
    s, g = strmatch[name], gpt4judge[name]
    for part, ids in (("safe", safe), ("unsafe", unsafe)):
        sm = pct(sum(refused(s[k]) for k in ids), len(ids))
        full = pct(sum(judge(g[k]) == "2_full_refusal" for k in ids), len(ids))
        partial = pct(sum(judge(g[k]) == "3_partial_refusal" for k in ids), len(ids))
        print(f"   {name:9s} {part:6s} string-match {sm:>6}   GPT-4 judge {full:>6} + {partial:>6}")

print("\n4. Item by item: how often each grader disagrees with the human label (refusal vs compliance)")
total = {"string-match": 0, "GPT-4 judge": 0}
three_class = 0
for name in MODELS.values():
    h, s, g = human[name], strmatch[name], gpt4judge[name]
    for part, ids in (("safe", safe), ("unsafe", unsafe)):
        miss = [k for k in ids if refused(h[k]) and not refused(judge(g[k]))]
        extra = [k for k in ids if not refused(h[k]) and refused(judge(g[k]))]
        sdis = sum(refused(h[k]) != refused(s[k]) for k in ids)
        total["string-match"] += sdis
        total["GPT-4 judge"] += len(miss) + len(extra)
        three_class += sum(h[k] != judge(g[k]) for k in ids)
        print(f"   {name:9s} {part:6s} string-match {sdis:3d}/{len(ids)}   GPT-4 judge {len(miss) + len(extra):3d}/{len(ids)}"
              f"  (refusal read as compliance {len(miss):2d}, compliance read as refusal {len(extra):2d})")
n_all = len(MODELS) * len(prompts)
for grader, k in total.items():
    print(f"   all models, {grader}: {k} of {n_all} responses ({pct(k, n_all)})")
print(f"   all models, GPT-4 judge with all three classes: {three_class} of {n_all} ({pct(three_class, n_all)})")
h, g = human["MistrI"], gpt4judge["MistrI"]
a = [refused(h[k]) for k in unsafe]
b = [refused(judge(g[k])) for k in unsafe]
print(f"   MistrI unsafe: agreement {pct(sum(x == y for x, y in zip(a, b)), len(a))}, "
      f"Cohen's kappa = {cohen_kappa(a, b):.2f}; refusal rate {pct(sum(a), len(a))} by humans, "
      f"{pct(sum(b), len(b))} by the judge")

print("\n5. Where the judge's errors on unsafe prompts come from")
misses = [(name, k) for name in MODELS.values() for k in unsafe
          if refused(human[name][k]) and not refused(judge(gpt4judge[name][k]))]
rebut = sum(prompts[k]["type"] in REBUTTAL_TYPES for _, k in misses)
share = sum(prompts[k]["type"] in REBUTTAL_TYPES for k in unsafe)
print(f"   human refusal read as compliance: {len(misses)}; {rebut} of them ({pct(rebut, len(misses))}) are in the two "
      f"types where a rebuttal counts as refusal, which hold {pct(share, len(unsafe))} of unsafe prompts")
flips = [k for k in unsafe if not refused(human["MistrI"][k]) and refused(judge(gpt4judge["MistrI"][k]))]
print(f"   MistrI responses labelled full compliance by humans but refusal by the judge: {len(flips)}")
for k in flips[:3]:
    print(f"     e.g. {prompts[k]['prompt']!r}: judge said {gpt4judge['MistrI'][k].strip()}")

print("\n6. Full refusal on safe prompts, without the three types the authors call contrived (T6, T7, T10)")
kept = [k for k in safe if prompts[k]["type"] not in CONTRIVED]
for name, lab in human.items():
    a = sum(lab[k] == "2_full_refusal" for k in safe)
    b = sum(lab[k] == "2_full_refusal" for k in kept)
    print(f"   {name:9s} {a:3d}/{len(safe)} = {pct(a, len(safe)):>6}  ->  {b:3d}/{len(kept)} = {pct(b, len(kept)):>6}")
t10 = [k for k in safe if prompts[k]["type"] == "privacy_fictional"]
g4 = [k for k in safe if human["GPT-4"][k] == "2_full_refusal"]
print(f"   GPT-4: {sum(k in t10 for k in g4)} of its {len(g4)} full refusals are in T10; the others:")
for k in g4:
    if k not in t10:
        print(f"     {prompts[k]['prompt']!r}")

print("\n7. 95% Wilson intervals")
print(f"   GPT-4 full refusal, 16/250: {wilson(16, 250)}")
print(f"   Llama2.0 full refusal, 95/250: {wilson(95, 250)}")
print(f"   GPT-4 on T10, 13/25: {wilson(13, 25)}")
print(f"   one prompt out of a type's 25: {wilson(1, 25)}")

print("\n8. Safe prompts containing 'kill'")
kill = [k for k in safe if re.search(r"\bkill", prompts[k]["prompt"], re.I)]
print(f"   {len(kill)} prompts in {len({prompts[k]['type'] for k in kill})} types")
for name, lab in human.items():
    print(f"   {name:9s} refused {sum(refused(lab[k]) for k in kill)} of {len(kill)}")
for k in kill:
    print(f"     {human['Llama2.0'][k]:18s} {prompts[k]['prompt']}")

print("\n9. A prompt from the Discussion")
for k, r in prompts.items():
    if "stage a massacre" in r["prompt"]:
        print(f"   {r['prompt']!r} is prompt {k}, type {r['type']}, label {r['label']}")
        print("   " + ", ".join(f"{name} {human[name][k]}" for name in MODELS.values()))
t4 = [k for k in safe if prompts[k]["type"] == "safe_contexts"]
print(f"   T4 (safe contexts), full refusals: " + ", ".join(
    f"{name} {sum(lab[k] == '2_full_refusal' for k in t4)}/25" for name, lab in human.items()))

print("\n10. Pairs: T1-T5 and T8 prompts each have one unsafe twin, 25 ids later")
pairs = [(k, k + 25) for start in (1, 51, 101, 151, 201, 326) for k in range(start, start + 25)]
assert all(prompts[str(u)]["type"] == "contrast_" + prompts[str(s)]["type"] for s, u in pairs)
for name, lab in human.items():
    right = sum(lab[str(s)] == "1_full_compliance" and lab[str(u)] == "2_full_refusal" for s, u in pairs)
    both_refused = sum(refused(lab[str(s)]) and lab[str(u)] == "2_full_refusal" for s, u in pairs)
    both_answered = sum(lab[str(s)] == "1_full_compliance" and lab[str(u)] == "1_full_compliance" for s, u in pairs)
    print(f"   {name:9s} both right {right:3d}/{len(pairs)}   refused both {both_refused:3d}   answered both {both_answered:3d}")

if len(sys.argv) > 2:
    print("\n11. XSTest prompts in PIGuard's training data")
    train = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    norm = lambda t: " ".join(str(t).lower().split())
    found = {}
    for row in train:
        found.setdefault(norm(row["prompt"]), []).append(row)
    hits = [(r, found[norm(r["prompt"])]) for r in prompts.values() if norm(r["prompt"]) in found]
    print(f"   {len(hits)} of {len(prompts)} XSTest prompts appear; their PIGuard labels:",
          dict(Counter(row["label"] for _, rows in hits for row in rows)),
          "(0 = benign)")
    print("   by XSTest label:", dict(Counter(r["label"] for r, _ in hits)))
