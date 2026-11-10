---
title: "OWASP AI Exchange: the risk method holds up, the evidence behind the advice is thin"
date: 2026-11-10T00:00:00+09:00
draft: false
tags: [llm-security, agents, prompt-injection, policy]
summary: "The AI Exchange is a free, 376-page OWASP guide that maps AI threats to controls and, by its own account, feeds ISO/IEC 27090 and the draft EU standard prEN 18282. Its method for cutting a threat list down to what matters, and its rule that prompt injection must be contained outside the model, hold up. Its advice comes with little evidence, and a few sections are wrong or out of date."
paper:
  title: "OWASP AI Exchange"
  authors: "Rob van der Veer (lead editor) and contributors"
  venue: "OWASP flagship project, PDF snapshot of 10 September"
  year: 2026
  url: "https://owaspai.org/"
  code: "https://github.com/OWASP/www-project-ai-security-and-privacy-guide"
  label: "The guide"
  codelabel: "Source on GitHub"
---

{{< paper >}}

This note is about the PDF snapshot generated from owaspai.org on 10 September 2026, 376 pages. The guide changes most weeks, so where the website has moved on, I say so. Disclosure: I work on prompt-injection detectors ([PIDS-Bench]({{< ref "/posts/pids-bench" >}})), one of the controls the guide discusses.

It is not a paper and has no experiments, so I read it for accuracy, internal consistency and usefulness.

## What it claims

The AI Exchange is OWASP's guide to AI security: threats, controls, risk analysis and testing, for all kinds of AI, not only language models. It is free under CC0, edited on GitHub by what it calls "over 170 carefully selected experts", and led by Rob van der Veer. It says its text feeds ISO/IEC 27090, the international guidance on AI security, and prEN 18282, the draft European standard for the EU AI Act's cybersecurity requirements.

Three positions shape everything else:

- AI security is mostly ordinary security applied to new assets: training data, model weights, the documents and system prompts inserted into a prompt, and the model's input and output. In its words, "most of these controls are about familiar conventional security countermeasures, unless you are training your own model" (p. 29).
- Agents and RAG are not a separate threat area. Mostly they make existing threats worse, above all indirect prompt injection.
- Prompt injection cannot be fixed inside the model: "Under current architectures, prompt injection is not solvable at the model layer alone" (p. 199). Security has to sit in the architecture around it.

## How it is built

Three pieces do most of the work.

The first is a taxonomy. Each threat is placed by the asset it hits, its impact, and the surface it comes through: development time, the model's input, or the runtime infrastructure. Threats link to controls, more than 50 in all, and the longer control entries include a field for limitations.

The second is a risk procedure. You start from the full list and remove threats with context questions. If you only use a hosted model, protecting its training data from poisoning is the supplier's job, and yours is checking the supplier. If the training data is not sensitive, model inversion stops mattering. If an agent cannot send data anywhere, an injection that aims to leak data stays theoretical. In the guide's words, "you start big, but you end up with a relatively small list of risks" (p. 66).

The third is defense in layers. For prompt injection the guide lists seven: alignment; filtering and detection on input and output; human approval of critical actions; automated oversight, such as stopping an email summarizer that tries to send a thousand emails; giving the agent only the user's rights; giving it only the rights the task needs; and granting rights per subtask, which can mean narrowing them the moment untrusted data enters. Everything after detection is blast radius control: it assumes the attack gets through and limits the damage. The agent sections add standard security engineering: a policy engine outside the agent, a strict schema for every tool, permissions that only shrink when delegated, and sandboxes that deny network access by default.

## What holds up

The risk method is the most useful part. Most frameworks give you a list; this one tells you how to make it shorter, and why that matters: "I've seen many cases of protections in place for threats that effectively don't matter" (p. 66).

It is honest about limits. "Evaluation characterizes behaviour; it does not prove correctness" (p. 27). Authorization rules "define what is permitted, not what is wise" (p. 137). Six of the seven layers come with a stated flaw, including detection: "detection of prompt injection is difficult, with substantial risk of false positives and false negatives" (p. 204).

The testing chapter gives advice that research papers often skip. Send test payloads through the real ingestion path instead of pasting them into a prompt. Check that controls work on normal input before attacking them. Report "rates, not single pass/fail", because models are not deterministic (p. 299). Treat what you did not test as a finding. The guide also keeps jailbreak, a failure of the model's reasoning, apart from agent escape, a failure of enforcement: "Conflating the two produces controls that are only partially effective against each" (p. 291).

## What doesn't

**Authority stands in for evidence.** The guide calls itself "effectively and informally" the standard in AI security (p. 17), but its recommendations come without data. It says LLM-based detectors are "the best approach for high-risk situations" (p. 210) and shows no comparison. Of the 404 distinct outside links in the PDF, I count about 40 that go to academic sources; the most-linked outside sites are OpenCRE (68) and MITRE ATLAS (38). It maps other frameworks more than it reviews what has been shown to work.

**It contradicts itself on memorization.** The copyright section asks whether generative models really look up existing work and answers "In essence: no", calling any remnants "more of a coincidence", before adding that it "remains a difficult discussion" (p. 94). The next page recommends testing models for memorisation (p. 95), and the section on data disclosure recommends checks for "unintended memorization" (p. 221). The research sits with the second view. [Carlini et al.](https://arxiv.org/abs/2301.13188) extracted over a thousand training images from diffusion models, and [found](https://arxiv.org/abs/2202.07646) that memorization in language models grows with model size, duplication in the data and prompt length.

**Two of its claims cannot both be used.** On hosted models, it says that if a vendor secretly trained on your input, "it would get out because there are ways to tell" (p. 55), without naming one. Elsewhere it says model inversion and membership inference are "typically low to zero risks for GenAI" (p. 88). Membership inference is the obvious way to tell, and [Duan et al.](https://arxiv.org/abs/2402.07841) found it barely beats chance on the pretraining data of large language models in most settings. If it fails as an attack, it fails as an audit.

**Parts are out of date.** The list of AI laws is "as of end of 2023" (p. 110) and still includes Canada's AIDA, which [died in January 2025](https://www.dlapiper.com/insights/publications/2025/01/canadian-privacy-and-ai-horizon-shifts-again), and the EU AI Liability Directive, which the Commission [withdrew in 2025](https://www.euronews.com/next/2025/07/31/eu-commission-confirms-ditching-of-ai-liability-and-patents-proposals). The tool review is "accurate as of September 2024" (p. 353) and rates tools by GitHub stars, contributors, scalability and integration (p. 352), not by which attacks they cover. The website has moved on: the repository has 62 commits between the snapshot and 6 November, including an [update to the standards status](https://github.com/OWASP/www-project-ai-security-and-privacy-guide/commit/e168cc9a57c5738c20b830dca49e024c78538056). ISO/IEC 27090 was [published in October 2026](https://www.bsigroup.com/en-GB/insights-and-media/media-centre/press-releases/2026/october/new-international-guidance-to-help-organizations-protect-ai-from-security-threats/), and the authors now expect prEN 18282 early in 2027. If you cite the guide, cite a website section with a date.

**The detector advice skips the research.** The section on detecting prompt injection names four commercial vendors and five open-source packages (p. 211). The guide never mentions the training-time defenses with published evaluations, such as StruQ, SecAlign or the instruction hierarchy, or agent benchmarks such as AgentDojo and InjecAgent. Its measurement advice asks for each detector's "miss-rate against adversarial inputs per supported language" (p. 211). False alarms are named as a risk, but the test procedure only asks that benign inputs not trigger "too many false positives" (p. 307). It says nothing about benign inputs that look like attacks, or about base rates. False positives are the half PIDS-Bench measures, and at a realistic base rate they decide whether a detector is usable. In PIDS-Bench, one detector's precision fell from 0.89 when one prompt in ten is an attack to 0.07 when one in a thousand is.

**Some terms are wrong**, which matters in a text that feeds standards: transfer learning as a way to transfer risk (p. 75), model inversion as reconstructing "publicly available input data" (p. 75), and differential privacy as "altering the data to make it sufficiently unrecognizable" (p. 354), when it is a property of the mechanism, not of the data.

## What I think

Read the overview, the risk analysis chapter, the agent sections, the prompt-injection section and the testing chapter. That is about a third of the guide and the part I would keep. Use it as a checklist and a shared vocabulary with security teams, not as evidence that a control works. It never measured that, but its tone makes it easy to forget.

Its stance on prompt injection is right, and it has a consequence for people who build detectors, including me. If detection is one layer that is expected to miss, a detector should be judged at the operating point where it runs, not by F1 on a balanced test set. The guide's warning that static tests give no guarantee against adaptive attackers is backed by [Nasr et al.](https://arxiv.org/abs/2510.09023), who broke 12 recent defenses with adaptive attacks, most of which had reported near-zero attack success. I would add one thing the guide does not say: the warning applies to the attack side of a benchmark. Benign users do not adapt to your detector, so false-positive rates measured on fixed benign prompts keep their meaning.

The guide accepts contributions, and two changes would cost little: ask for false-positive rates at a stated base rate next to miss rates, and rate testing tools by what they test rather than by GitHub stars.

[check_owasp_ai_exchange.py](check_owasp_ai_exchange.py) finds every passage quoted here in a copy of the PDF and prints its page, or says it is gone from a newer version. It also repeats my link count.

If I have misread something, I want to know: <khalidshire@kookmin.ac.kr>.
