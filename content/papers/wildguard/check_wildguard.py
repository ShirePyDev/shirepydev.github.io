"""Recompute the arithmetic in my WildGuard note from numbers printed in the papers.

    python check_wildguard.py

Part 1 uses only the Python standard library. The table values are typed in from
WildGuard arXiv v3 (Dec 2024), Feng et al. (arXiv 2608.03201) and Orojlooyjadid and
Patel (EMNLP 2026), with the table each one comes from.

Part 2 is optional and needs pandas with pyarrow plus the gated WildGuardMix files
(https://huggingface.co/datasets/allenai/wildguardmix) and a ToxicChat test file:

    python check_wildguard.py wildguard_train.parquet toxicchat_test.csv

I have not run Part 2 myself, because I do not have the gated data.
"""
import sys
from statistics import mean

print("PART 1: arithmetic from the published tables\n")

print("1. Headline percentages (abstract, Tables 2 and 4)")
wg_refusal, refusal_classifier = 88.6, 70.1  # WildGuardTest refusal F1: WildGuard vs LibrAI-LongFormer-ref
print(f"   refusal: {wg_refusal} vs {refusal_classifier}: relative {100 * (wg_refusal / refusal_classifier - 1):.1f}%,"
      f" absolute {wg_refusal - refusal_classifier:.1f} points (abstract: 26.4%)")
wg_adv, gpt4_adv = 85.5, 81.6  # WildGuardTest adversarial prompt harm F1
print(f"   adversarial prompt harm: {wg_adv} vs {gpt4_adv}: absolute {wg_adv - gpt4_adv:.1f} points,"
      f" relative {100 * (wg_adv / gpt4_adv - 1):.1f}% (abstract: 3.9%; NeurIPS page: 4.8%)")

print("\n2. Single-task versus multi-task (Tables 5 and 18)")
multi_public, multi_wgt = 86.1, 88.9            # Table 5, full WildGuardTrain
single_t5_public, single_t5_wgt = 86.0, 89.2    # Table 5, single-task only
single_t18 = [73.0, 71.9, 90.8, 99.5, 100.0]    # Table 18: ToxiC, OAI, Aegis, SimpST, HarmB
print(f"   Table 18 single-task cells average {mean(single_t18):.1f} (printed 87.0; Table 5 says {single_t5_public});"
      f" multi-task {multi_public}")
print(f"   WildGuardTest prompt harm: Table 18 single-task 88.2, Table 5 single-task {single_t5_wgt},"
      f" multi-task {multi_wgt}")
worker_t18 = [71.5, 71.1, 79.4, 96.4, 99.4]     # Table 18, minus worker-written
print(f"   minus worker-written: Table 18 cells average {mean(worker_t18):.1f}; Table 5 prints 84.8")

print("\n3. GPT-4 on BeaverTails (Tables 3 and 19) against the response-harm average both print, 82.0")
for beavertails in (86.1, 83.0):
    cells = [86.1, 67.9, beavertails, 91.3]       # HarmB, SafeRLHF, BeaverTails, XSTest-Resp
    print(f"   with BeaverTails = {beavertails}: average {mean(cells):.2f}")

print("\n4. Test-set counts (Table 14) against the 1,725 starting pairs in the text")
for task, a, b in (("prompt harm", 946, 810), ("response harm", 1467, 299), ("refusal", 597, 1180)):
    print(f"   {task}: {a} + {b} = {a + b}")
print("   XSTest-Resp: 250 of the 450 XSTest prompts are safe; text says 368 harmful / 78 benign responses,")
print("   Table 14 says 368 benign / 78 harmful")

print("\n5. Annotator pay (Appendix E)")
per_item, annotators, items, reported = 2.50, 3, 1725, 4305
print(f"   ${per_item:.2f} x {annotators} annotators x {items} items = ${per_item * annotators * items:,.2f};"
      f" reported total ${reported:,}; ${reported:,} / ${per_item:.2f} = {reported / per_item:,.0f} item-annotations")

print("\n6. Margins against base-model spread (Tables 3, 4 and 17)")
refusal_by_base = {"Mistral-7B-v0.3": 88.6, "Gemma-7B": 90.1, "Llama2-7B": 87.5,
                   "Tulu2-SFT-7B": 88.7, "Llama3-8B": 88.4, "OLMo-1.7-7B": 86.6}
response_by_base = {"Mistral-7B-v0.3": 75.4, "Gemma-7B": 75.0, "Llama2-7B": 75.1,
                    "Tulu2-SFT-7B": 78.7, "Llama3-8B": 77.3, "OLMo-1.7-7B": 76.2}
print(f"   WildGuardTest refusal F1 across base models: {min(refusal_by_base.values())} to"
      f" {max(refusal_by_base.values())}")
print(f"   WildGuardTest response-harm F1 across base models: {min(response_by_base.values())} to"
      f" {max(response_by_base.values())}")
print(f"   MD-Judge minus WildGuard, WildGuardTest response harm: {76.8 - 75.4:.1f}")
print(f"   WildGuard minus GPT-4, public prompt harm: {86.1 - 84.6:.1f}")

print("\n7. Ablation cells that improve when a data source is removed (Table 5)")
columns = ["prompt public", "prompt WGT adv", "prompt WGT total", "response public", "response WGT adv",
           "response WGT total", "refusal XSTest-Resp", "refusal WGT adv", "refusal WGT total"]
full = [86.1, 85.5, 88.9, 82.4, 68.4, 75.4, 92.8, 88.5, 88.6]
ablations = {
    "minus synthetic adversarial": [84.6, 77.1, 84.4, 78.6, 67.8, 73.9, 94.1, 88.3, 87.6],
    "minus synthetic vanilla": [83.6, 85.7, 89.8, 81.3, 66.9, 75.5, 90.2, 85.7, 84.9],
    "minus in-the-wild": [83.9, 84.6, 88.7, 81.9, 69.5, 76.5, 93.0, 88.0, 88.6],
    "minus worker-written": [84.8, 84.5, 86.8, 76.4, 66.4, 74.7, 94.9, 87.8, 88.4],
}
better = [(name, col) for name, row in ablations.items() for col, x, y in zip(columns, row, full) if x > y]
print(f"   {len(better)} of {len(ablations) * len(columns)} cells improve:")
for name, col in better:
    print(f"     {name}: {col}")
print(f"   ToxicChat without in-the-wild data: 70.8 - 60.5 = {70.8 - 60.5:.1f} points (Table 18)")

print("\n8. Filter demonstration (Table 6)")
print(f"   0.4% of 250 benign prompts = {0.004 * 250:.0f} prompt")

print("\n9. Later papers")
print(f"   Orojlooyjadid and Patel: native template 73.60 vs generic prompt 30.21, a drop of {73.60 - 30.21:.1f}")
print(f"   Feng et al.: 10,651 refusals among 21,286 responses to harmful prompts"
      f" ({100 * 10651 / 21286:.1f}%), none labelled harmful")

if len(sys.argv) < 2:
    sys.exit(0)

print("\nPART 2: the released data (optional)\n")
import csv  # noqa: E402

import pandas as pd  # noqa: E402

train = pd.read_parquet(sys.argv[1])
answered = train[train["response"].notna() & (train["prompt_harm_label"] == "harmful")]
refusals = answered[answered["response_refusal_label"] == "refusal"]
print(f"   responses to harmful prompts: {len(answered):,} (Feng et al.: 21,286)")
print(f"   refusals among them: {len(refusals):,} (Feng et al.: 10,651)")
print(f"   refusals labelled harmful: {(refusals['response_harm_label'] == 'harmful').sum():,} (Feng et al.: 0)")

if len(sys.argv) > 2:
    path = sys.argv[2]
    if path.endswith(".csv"):
        with open(path, encoding="utf-8", newline="") as f:
            toxic = [row["user_input"] for row in csv.DictReader(f)]
    else:
        toxic = pd.read_parquet(path)["user_input"].tolist()
    norm = lambda text: " ".join(str(text).lower().split())
    seen = set(train["prompt"].map(norm))
    overlap = sum(norm(text) in seen for text in toxic)
    print(f"   ToxicChat test prompts found verbatim in WildGuardTrain: {overlap:,} of {len(toxic):,}")
