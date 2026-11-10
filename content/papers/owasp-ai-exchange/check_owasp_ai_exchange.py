"""Check the quotes and link counts used in my note on the OWASP AI Exchange.

The AI Exchange is a living document, so the PDF changes. This script takes a
PDF you downloaded (https://owaspai.org/OWASP-AI-Exchange.pdf), finds the page
of every passage the note quotes or relies on, and says which ones are gone.
It also counts the link targets in the PDF by domain.

The note was written against the snapshot "Generated from owaspai.org on:
9/10/2026" (376 pages).

    pip install pypdf
    python check_owasp_ai_exchange.py OWASP-AI-Exchange.pdf
"""
import re
import sys
import collections
from urllib.parse import urlparse

from pypdf import PdfReader

# (page in the 9/10/2026 snapshot, passage). Matching ignores case,
# punctuation and line breaks.
PASSAGES = [
    (15, "over 170 carefully selected experts"),
    (17, "effectively and informally making the AI Exchange the standard in AI security"),
    (27, "Evaluation characterizes behaviour; it does not prove correctness"),
    (29, "most of these controls are about familiar conventional security countermeasures, "
         "unless you are training your own model"),
    (55, "If vendors would do this secretly, it would get out because there are ways to tell"),
    (66, "you start big, but you end up with a relatively small list of risks"),
    (66, "I've seen many cases of protections in place for threats that effectively don't matter"),
    (75, "typically through transfer learning, federated learning, insurance or outsourcing"),
    (75, "reconstruct publicly available input data from model outputs"),
    (88, "Model inversion and membership inference are typically low to zero risks for GenAI"),
    (94, "Do generative AI models really look up existing work that may be copyrighted? In essence: no"),
    (94, "this remains a difficult discussion"),
    (94, "Parts of this content may show remnants of existing work, but that is more of a coincidence"),
    (95, "Test the resulting model for memorisation and extraction of training material"),
    (110, "Global Jurisdictional considerations (as of end of 2023)"),
    (137, "define what is permitted, not what is wise"),
    (199, "do not provide security guarantees against adaptive adversaries"),
    (199, "Under current architectures, prompt injection is not solvable at the model layer alone"),
    (204, "detection of prompt injection is difficult, with substantial risk of false positives "
          "and false negatives"),
    (205, "when an email summarizer attempts to send a thousand emails"),
    (210, "the best approach for high-risk situations is to utilize LLM-based detectors"),
    (211, "Pangea, Hiddenlayer, AIShield, and Aiceberg"),
    (211, "evaluate each detector's miss-rate against adversarial inputs per supported language"),
    (221, "This can help identify unintended memorization and potential data leakage"),
    (291, "Conflating the two produces controls that are only partially effective against each"),
    (298, "Confirm designed controls work under normal conditions before adversarial load"),
    (298, "coverage gaps are findings"),
    (299, "probabilistic LLM behaviour requires reporting rates, not single pass/fail"),
    (307, "not too many false positives are triggered by benign inputs"),
    (352, "3,000 stars"),
    (353, "accurate as of September 2024"),
    (354, "altering the data to make it sufficiently unrecognizable"),
]

ACADEMIC = re.compile(r"arxiv\.org|doi\.org|acm\.org|ieee|usenix|openreview|"
                      r"aclanthology|neurips|springer|sciencedirect|ndss|proceedings")


def norm(text):
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = re.sub(r"-\s*\n\s*", "", text)          # words split over lines
    text = re.sub(r"[^a-z0-9']+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def main(path):
    reader = PdfReader(path)
    pages = [norm(p.extract_text() or "") for p in reader.pages]
    first = (reader.pages[0].extract_text() or "")
    stamp = re.search(r"Generated from owaspai\.org on:\s*([0-9/]+)", first)
    print(f"{path}: {len(pages)} pages, generated {stamp.group(1) if stamp else 'unknown'}")
    print()
    missing = 0
    for expected, passage in PASSAGES:
        key = norm(passage)
        found = [i + 1 for i, t in enumerate(pages) if key in t]
        if not found:
            # a passage can straddle a page break
            found = [i + 1 for i in range(len(pages) - 1)
                     if key in pages[i] + " " + pages[i + 1]]
        if found:
            note = "" if expected in found else f"  (was p. {expected})"
            print(f"  p. {found[0]:>3}  {passage}{note}")
        else:
            missing += 1
            print(f"  GONE   {passage}  (was p. {expected})")
    print()
    print(f"{len(PASSAGES) - missing} of {len(PASSAGES)} passages found")

    urls = set()
    for page in reader.pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A")
            if action and action.get("/URI"):
                urls.add(str(action["/URI"]))
    external = [u for u in urls if "owaspai.org" not in u]
    domains = collections.Counter(
        urlparse(u).netloc.lower().removeprefix("www.") for u in external)
    print()
    print(f"distinct link targets: {len(urls)}, external (not owaspai.org): {len(external)}")
    print(f"academic-looking external links: {sum(1 for u in external if ACADEMIC.search(u))}")
    for domain, count in domains.most_common(8):
        print(f"  {count:>4}  {domain}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
