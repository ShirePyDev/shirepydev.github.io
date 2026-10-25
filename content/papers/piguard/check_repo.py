"""Print every count in my PIGuard note from the authors' released files.

    git clone https://github.com/leolee99/PIGuard
    python check_repo.py PIGuard/datasets

Standard library only. It reads train.json, valid.json, the three NotInject files,
wildguard.json and the two BIPIA files. PINT is not public, so it is not checked.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(sys.argv[1] if len(sys.argv) > 1 else "PIGuard/datasets")
CHINESE = re.compile(r"[一-鿿]")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def norm(text):
    return " ".join(str(text).lower().split())


train = load("train.json")
valid = load("valid.json")
notinject = [row for part in ("one", "two", "three") for row in load(f"NotInject_{part}.json")]
tests = {
    "NotInject": [row["prompt"] for row in notinject],
    "WildGuard": [row["prompt"] for row in load("wildguard.json")],
    "BIPIA": [text for f in ("BIPIA_text.json", "BIPIA_code.json") for v in load(f).values() for text in v],
}

print("1. Validation items that are also test items")
print(f"   valid.json has {len(valid)} items")
for name, prompts in tests.items():
    in_valid = [norm(r["prompt"]) for r in valid if r.get("source", "").startswith(name)]
    test_set = set(map(norm, prompts))
    print(f"   {name:9s}: {len(in_valid):3d} in valid.json, {sum(p in test_set for p in in_valid):3d} of them also in the test file")
pint = sum(r.get("source", "").startswith("PINT") for r in valid)
print(f"   PINT     : {pint:3d} in valid.json (test file not public, not checked)")

print("\n2. Language in NotInject")
foreign = [r for r in notinject if r["category"] == "Multilingual"]
print(f"   {len(foreign)} of {len(notinject)} sentences are in the Multilingual category, "
      f"{sum(bool(CHINESE.search(r['prompt'])) for r in foreign)} of them contain Chinese characters")
words = sorted({w for r in notinject for w in r["word_list"]})
not_english = [w for w in words if not re.fullmatch(r"[A-Za-z]+", w)]
chinese_words = [w for w in words if CHINESE.search(w)]
print(f"   {len(not_english)} of {len(words)} trigger words are not English words; "
      f"{len(chinese_words)} are single Chinese characters: {' '.join(chinese_words)}")

print("\n3. Those Chinese characters in the training data, MOF rows removed")
base = [r for r in train if r["source"] != "over-defense"]
benign = [r["prompt"] for r in base if r["label"] == 0]
attack = [r["prompt"] for r in base if r["label"] == 1]
has = lambda p: any(w in p for w in chinese_words)
print(f"   attack samples containing one: {sum(map(has, attack))} of {len(attack)}")
print(f"   benign samples containing one: {sum(map(has, benign))} of {len(benign)}")

print("\n4. The MOF rows")
mof = [r["prompt"] for r in train if r["source"] == "over-defense"]
print(f"   {len(mof)} rows labelled 'over-defense' (the paper says 1,000 were generated)")
NON_ASCII = re.compile(r"[^\x00-\x7F]")
print(f"   {sum(bool(CHINESE.search(p)) for p in mof)} of them contain Chinese characters")
print(f"   {sum(bool(NON_ASCII.search(p)) for p in mof)} contain any non-ASCII character")

print("\n5. A BIPIA string scored as an attack")
bipia = load("BIPIA_text.json")
print(f"   'Conversational Agent': {bipia['Conversational Agent'][0]!r}")
