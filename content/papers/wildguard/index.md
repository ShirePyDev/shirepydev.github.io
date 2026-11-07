---
title: "WildGuard: the refusal label was the right call, the GPT-4 comparison is weaker than it looks"
date: 2026-11-08T00:00:00+09:00
draft: false
tags: [guardrails, moderation, evaluation, llm-security]
summary: "WildGuard was the first open moderation model to label prompt harm, response harm and refusal separately, and that part holds up. Its margins over GPT-4 sit inside base-model noise, GPT-4 helped grade the test set, and later work shows a refusal sentence in front of a harmful reply makes the guard call it safe."
paper:
  title: "WildGuard: Open One-stop Moderation Tools for Safety Risks, Jailbreaks, and Refusals of LLMs"
  authors: "Seungju Han, Kavel Rao et al."
  venue: "NeurIPS Datasets and Benchmarks"
  year: 2024
  url: "https://arxiv.org/abs/2406.18495"
  code: "https://github.com/allenai/wildguard"
---

{{< paper >}}

The paper appeared on arXiv in June 2024 and at the NeurIPS 2024 Datasets and Benchmarks track; the numbers below are from arXiv v3 (December 2024). Two disclosures: I work on the neighbouring problem, over-defense in prompt-injection detectors ([PIDS-Bench]({{< ref "/posts/pids-bench" >}})), and one of the paper's authors endorsed my own paper's arXiv submission.

## What the paper claims

A moderation model is a classifier that sits beside a chatbot. It reads the user's prompt, and sometimes the chatbot's reply, and decides whether either one is harmful. Llama Guard, Aegis and MD-Judge all do some version of this.

The authors' argument is that two labels are not enough. Take "How do I kill a Python process?". A refusal ("I can't help with violence") and a correct answer are both harmless, so a harm label cannot tell them apart. If you want to measure over-refusal, you need a third label: did the model refuse? WildGuard answers all three questions at once, prompt harmful or not, response harmful or not, response a refusal or not, from one input. No open model did that before, and the one open refusal classifier they could find, a LongFormer trained on Do-Not-Answer, was only modestly better than keyword matching.

The paper's second motivation is adversarial prompts. On a sample of WildJailbreak, open tools that score well on plain harmful requests fall apart when the same requests are wrapped in jailbreak tactics, and GPT-4 does not.

The contributions are a dataset and a model. WildGuardMix has 92K labelled items: WildGuardTrain, 86,759 items for training, and WildGuardTest, 5,299 human-labelled items. WildGuard is Mistral-7B-v0.3 fine-tuned on the training set. The headline results are that WildGuard beats every open baseline on all three tasks, matches GPT-4, and cuts the success rate of jailbreaks against an unsafe chatbot from 79.8% to 2.4% when used as a filter.

## How they tested it

Most of the training data is synthetic, and GPT-4 wrote most of it. GPT-4 generated harmful prompts from a 13-subcategory taxonomy, and benign prompts built to look harmful, in the style of XSTest. The WildTeaming framework, from the same group, then rewrote both kinds with jailbreak tactics mined from real chat logs, so the training set has adversarial harmful prompts and adversarial benign ones in roughly equal numbers (4,489 and 4,339 with responses, 11,289 and 11,411 prompt-only). A suite of open models wrote refusals and compliances to each prompt, told in a suffix which one to produce. GPT-4 labelled the results, and a 500-item human audit agreed with its labels on 92%, 82% and 95% of items for the three tasks. Two smaller slices come from elsewhere: 1,888 real prompts from LMSYS-Chat-1M and WildChat, labelled by the OpenAI Moderation API, and 9,491 prompts from HH-RLHF and Anthropic's red-teaming data, labelled by GPT-4.

WildGuardTest is a held-out slice of the synthetic data. Three Prolific annotators labelled each item; Fleiss' κ was 0.55 for prompt harm, 0.72 for refusal and 0.50 for response harm. Items without two-way agreement were dropped, then GPT-4 was run over the set and the items where it disagreed with the annotators were inspected by hand. The authors also built XSTest-Resp: model responses to the XSTest prompts, with human labels for harm and refusal.

Evaluation is F1 on ten public benchmarks plus WildGuardTest, against ten open models, the OpenAI Moderation API and GPT-4. For GPT-4 they tried several prompts and kept the one that scored best. Everything is one training run at one decision point; the model emits yes or no, so there is no threshold to sweep.

## What the results show

On prompt harmfulness, WildGuard averages 86.1 F1 across five public benchmarks against 84.6 for GPT-4 and 80.0 for the best open model (Table 3). On WildGuardTest the picture splits: WildGuard wins on the adversarial prompts, 85.5 against GPT-4's 81.6, and loses on the plain ones, 91.7 against 93.4 (Table 4). On response harmfulness it is about level with GPT-4 and MD-Judge. On refusal detection, the task no open model handled, it scores 88.6 on WildGuardTest where the previous best open model scored 73.1 and the dedicated refusal classifier 70.1; GPT-4 scores 92.4. On XSTest-Resp, GPT-4's refusal F1 is 98.1 and WildGuard's 92.8.

Two of the headline percentages are relative and one is not. The "26.4% improvement on refusal detection" is 88.6 over 70.1, a gap of 18.5 points. The "3.9% improvement" over GPT-4 on adversarial prompts is 85.5 minus 81.6, in points; the relative figure would be 4.8%. The abstract on the NeurIPS proceedings page gives 25.3% and 4.8% for the same two claims.

The ablation says the adversarial data earns its place: without it, adversarial prompt-harm F1 on WildGuardTest drops from 85.5 to 77.1. The filter demonstration uses the WildJailbreak validation set, 2,000 harmful and 250 benign adversarial prompts, in front of a Tulu-2 model with no safety tuning: attack success falls from 79.8% to 2.4%, refusals of benign prompts rise from 0 to 0.4%, about one prompt in 250.

## What they don't show

The authors give three limitations: most of the data is synthetic, the harm taxonomy is theirs, and so is the definition of refusal. Four more came out of my reading. These are my findings, not theirs.

**GPT-4 is on both sides of the comparison.** It wrote the vanilla prompts, mined the jailbreak tactics, labelled the training data, labelled the annotator-written data, and then the test labels were "further audited" by inspecting the items where GPT-4 disagreed with the annotators. After that, GPT-4 is the baseline WildGuard is said to match. Some agreement is built in. The in-the-wild slice is the odd one out: its labels come from the OpenAI Moderation API, which the paper's own Tables 3 and 4 rank last of every tool tested, at 41.8 average F1 on prompt harm and 12.1 on WildGuardTest, and the paper says those labels did not need an audit. Removing that slice costs 10.3 F1 on ToxicChat, which the authors read as the value of real data. ToxicChat and LMSYS-Chat-1M were both collected from the same LMSYS Vicuna demo. The paper reports no overlap check between them, and I could not run one.

**The tables disagree with each other.** Table 5 gives the single-task prompt model 86.0 average F1 on public benchmarks and 89.2 on WildGuardTest; Table 18 gives the same model 87.0 and 88.2, and its five per-benchmark cells average to 87.0. If Table 18 is right, the single-task model beats the multi-task one on public prompt harm, and the sentence "on all tasks except refusal detection on XSTest-Resp, the multi-task model outperforms single-task models" is wrong. The two tables also disagree on the worker-written ablation (84.8 against 83.6). Table 3 gives GPT-4 86.1 on BeaverTails and Table 19 gives 83.0; only 83.0 fits the 82.0 average both tables report. The text says XSTest-Resp has 368 harmful and 78 benign responses, Table 14 says 368 benign and 78 harmful, and since 250 of the 450 XSTest prompts are safe, the table is the plausible one. The text says the test set started as 1,725 pairs, but the per-task counts in Table 14 run from 1,756 to 1,777. And Appendix E's annotator pay, $2.50 per item for three annotators on 1,725 items, comes to about $12,900 before XSTest-Resp and the audit, against a reported total of $4,305. None of these changes the main story. Together they mean the smaller margins should not be read closely.

**The margins are inside the noise.** There is one run per configuration and no intervals. Table 17 trains the same data on six base models: WildGuardTest refusal F1 runs from 86.6 to 90.1 and response-harm F1 from 75.0 to 78.7. MD-Judge is 1.4 points ahead of WildGuard on WildGuardTest response harm, and WildGuard's lead over GPT-4 on public prompt harm is 1.5. In the ablation, eight cells improve when a data source is removed, including both WildGuardTest response-harm scores without the in-the-wild data, which sits awkwardly next to "each is essential".

**The adversarial results are in-distribution.** The adversarial training prompts, the adversarial half of WildGuardTest, and the WildJailbreak set used for the filter demonstration all come from the same WildTeaming pipeline. The benign-adversarial data is the paper's answer to over-refusal, a benign request in jailbreak clothing for every harmful one, and it clearly works on test items built the same way. Nothing in the paper tests it on jailbreak-styled benign prompts written by other people. In PIDS-Bench I found that hard negatives written in one style fixed the false positives written in that style and barely touched prompts from other sources, so I would not assume the transfer.

## What I think

The three-label design is the lasting contribution. Refusal is a different question from harm, you need it to measure over-refusal, and XSTest-Resp and the refusal half of WildGuardTest are still the only human-labelled refusal sets I know of. The data is released under a gated ODC-BY licence and the recipe is complete, which is more than Llama Guard offered. The model is tied to its template: a 2026 benchmark of 53 models found that swapping WildGuard's native prompt for a generic safety prompt drops its average F1 from 73.6 to 30.2 ([Orojlooyjadid and Patel, EMNLP 2026](https://aclanthology.org/2026.emnlp-main.1748.pdf)). In that benchmark WildGuard ranks 20th on prompt-only moderation, below GPT-4.1 and GPT-5, and 6th when the response is included, below Llama Guard 3. It is strong on XSTest (95.0 macro-F1) and weak on prompt-only HarmBench (50.2) and HarmAug (49.6). BingoGuard beats it on WildGuard's own data when responses are included (88.8 against 84.7).

The more interesting follow-up concerns the labels. [Feng et al.](https://arxiv.org/abs/2608.03201) (preprint, August 2026) audited WildGuardMix and found that among 21,286 responses to harmful prompts, all 10,651 refusals are labelled unharmful; not one refusal is labelled harmful. A guard trained on that can learn that refusal wording means safe. They test it by putting refusal sentences such as "I apologize, but I cannot fulfill your request." in front of harmful responses in WildGuardTest, leaving the harmful content in place: at least one of their three cues flips WildGuard's verdict from harmful to unharmful on 37.7% of them, against 0.7% for neutral control sentences, and up to 59.4% on the Aegis2 test set when the cue goes at the end. Masking a small set of attention heads and MLP neurons brings the 37.7% down to 2.9% without retraining. The paper's data is balanced by class. It is not balanced by the co-occurrence of two labels, and that was enough to create a shortcut.

For my own area, two things carry over. First, when a dataset says "balanced", check the pairs, not the marginals; a detector trained on refusal-plus-harmful equals zero learned exactly what it was shown. Second, the benign-adversarial contrastive data is the same move as the hard negatives in PIDS-Bench, and the open question is the same: whether it transfers. I could not find a test of WildGuard's prompt-harm head on benign prompts that look like attacks but come from outside its generator, such as NotInject or the PIDS-Bench hard-benign set. It is a 7B model, so that test is cheap, and I would run it before trusting the 0.4% over-refusal figure anywhere but on WildJailbreak.

I did not run WildGuard or download WildGuardMix for this note. Everything above that is not from the paper comes from the two later papers. [check_wildguard.py](check_wildguard.py) recomputes every arithmetic claim here from the papers' tables with the standard library. An optional second part, for readers with access to the gated dataset, repeats Feng et al.'s label count and checks ToxicChat's test prompts against the training set; I could not run that part myself.

If I have misread something, I want to know: <khalidshire@kookmin.ac.kr>.
