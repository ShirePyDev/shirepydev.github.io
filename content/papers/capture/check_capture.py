"""Recompute every calculation in my note on CAPTURE (Kholkar and Ahuja, LLMSec 2025).

All inputs are copied from the paper's tables (arXiv v2, identical in the ACL
version) and, for the last check, from the InjecGuard paper (arXiv 2410.22770v1).
Standard library only:  python check_capture.py
"""

# Table 2 and Table 3: false negative rate (attacks missed) and false positive
# rate (harmless prompts blocked), in percent.
DOMAINS = ["Stock", "Movies", "Python", "Travel", "Covid", "Shopping"]
FNR = {
    "ProtectAIv2":  [23.87, 22.78, 30.60, 14.98, 29.17, 24.02],
    "InjecGuard":   [99.84, 100.00, 35.65, 99.84, 100.00, 98.28],
    "PromptGuard":  [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    "Deepset":      [0.47, 0.47, 0.00, 0.78, 0.47, 1.40],
    "Fmops":        [100.00, 100.00, 100.00, 100.00, 100.00, 100.00],
    "GPT-4o":       [16.38, 7.48, 13.72, 7.33, 9.36, 15.60],
    "Llama3.2-1B":  [69.84, 76.44, 58.20, 64.27, 70.04, 63.96],
    "CaptureGuard": [0.15, 0.00, 0.00, None, None, None],
}
FPR = {
    "ProtectAIv2":  [48.84, 43.27, 27.06, 82.27, 43.27, 61.34],
    "InjecGuard":   [99.12, 99.12, 0.88, 99.71, 98.25, 99.72],
    "PromptGuard":  [100.00, 100.00, 24.12, 100.00, 100.00, 99.72],
    "Deepset":      [83.14, 70.76, 100.00, 16.86, 79.82, 62.18],
    "Fmops":        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    "GPT-4o":       [5.81, 9.35, 2.64, 5.23, 13.15, 3.08],
    "Llama3.2-1B":  [20.05, 24.85, 62.53, 20.63, 30.20, 25.49],
    "CaptureGuard": [0.00, 2.05, 2.05, None, None, None],
}

# Table 6: accuracy (%) on NotInject (average), WildGuard benign, BIPIA injections.
TABLE6 = {
    "Deepset":      (5.31, 50.98, 84.67),
    "Fmops":        (5.60, 50.88, 88.67),
    "PromptGuard":  (0.88, 6.69, 100.00),
    "ProtectAIv2":  (56.64, 75.18, 8.67),
    "GPT-4o":       (86.62, 84.24, 66.00),
    "InjecGuard":   (87.31, 76.11, 68.34),
    "CaptureGuard": (79.04, 75.00, 54.77),
}


def fits(rate, n):
    """Can a rate printed with two decimals come from k out of n prompts?"""
    k = round(rate * n / 100)
    return abs(round(100 * k / n, 2) - rate) < 1e-9


def smallest_n(rate):
    return next(n for n in range(1, 100000) if fits(rate, n))


print("1. CaptureGuard against InjecGuard on the outside benchmarks (Table 6)")
names = ("NotInject", "WildGuard", "BIPIA")
for i, bench in enumerate(names):
    diff = TABLE6["CaptureGuard"][i] - TABLE6["InjecGuard"][i]
    print(f"   {bench:9s}  CaptureGuard {TABLE6['CaptureGuard'][i]:6.2f}  "
          f"InjecGuard {TABLE6['InjecGuard'][i]:6.2f}  difference {diff:+.2f}")
print("   Average of the three columns, ranked:")
for name, row in sorted(TABLE6.items(), key=lambda kv: -sum(kv[1])):
    print(f"     {name:12s} {sum(row) / 3:6.2f}")
print(f"   CaptureGuard misses {100 - TABLE6['CaptureGuard'][2]:.2f}% of BIPIA injections; "
      f"its largest miss rate on its own test sets is {max(v for v in FNR['CaptureGuard'] if v is not None):.2f}%")

print("\n2. Cells where a model both misses and blocks nearly everything (FNR and FPR >= 95%)")
for name in FNR:
    for d, fn, fp in zip(DOMAINS, FNR[name], FPR[name]):
        if fn is not None and fn >= 95 and fp >= 95:
            print(f"   {name:12s} {d:9s} misses {fn:6.2f}% of attacks, blocks {fp:6.2f}% of harmless prompts")
print("   InjecGuard in Python, for contrast: misses "
      f"{FNR['InjecGuard'][2]:.2f}%, blocks {FPR['InjecGuard'][2]:.2f}%")

print("\n3. How many prompts each rate comes from (rate = k/n, printed to two decimals)")
print("   Paper: 641 test/validation attacks (Section 2.2) and 171 test/validation")
print("   harmless prompts 'across six domains' (Section 2.3).")
GUARDS = ["ProtectAIv2", "InjecGuard", "PromptGuard", "Deepset", "Fmops"]
OTHERS = ["GPT-4o", "Llama3.2-1B", "CaptureGuard"]
for table, label in [(FNR, "attacks"), (FPR, "harmless prompts")]:
    print(f"   Smallest number of {label} per domain that fits all five public guards:")
    for j, d in enumerate(DOMAINS):
        vals = [table[g][j] for g in GUARDS]
        n = next(n for n in range(1, 5000) if all(fits(v, n) for v in vals))
        misfit = [o for o in OTHERS if table[o][j] is not None and not fits(table[o][j], n)]
        print(f"     {d:9s} n = {n:4d}   rows that do not fit this n: {', '.join(misfit) or 'none'}")
for label, rate in [("CaptureGuard miss rate, Stock", 0.15),
                    ("CaptureGuard false positive rate, Movies and Python", 2.05)]:
    print(f"   {label:52s} {rate:5.2f}%  needs n >= {smallest_n(rate)}")
print("\n4. Table 6 baselines against the InjecGuard paper (arXiv v1)")
INJECGUARD_V1 = {  # Table 2 over-defense; Table 7 WildGuard benign and BIPIA injection
    "Deepset":     (5.31, 50.98, 84.67),
    "Fmops":       (5.60, 50.88, 88.67),
    "PromptGuard": (0.88, 6.69, 100.00),
    "ProtectAIv2": (56.64, 75.18, 8.67),
    "GPT-4o":      (86.73, 84.24, 66.00),
    "InjecGuard":  (87.32, 76.11, 68.34),
}
for name, v1 in INJECGUARD_V1.items():
    diffs = [f"{n}: {a} vs {b}" for n, a, b in zip(names, TABLE6[name], v1) if abs(a - b) > 1e-9]
    print(f"   {name:12s} {'matches' if not diffs else 'differs, ' + '; '.join(diffs)}")
# NotInject average recomputed from the InjecGuard paper's per-level scores (Table 7)
for name, levels in [("GPT-4o", (95.58, 85.84, 78.76)), ("InjecGuard", (91.15, 89.38, 81.42))]:
    print(f"   {name} NotInject average from levels {levels}: {sum(levels) / 3:.2f}")
