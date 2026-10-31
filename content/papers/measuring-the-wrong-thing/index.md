---
title: "Measuring the Wrong Thing: the jailbreaks that work score lower than the ones that fail"
date: 2026-11-01T00:00:00+09:00
draft: false
tags: [llm-security, guardrails, evaluation]
summary: "On Llama-3.1-8B, a harmfulness score that separates harmful from harmless prompts well ranks the jailbreaks that succeed below the ones that fail; the broader claims rest on thinner evidence."
paper:
  title: "Measuring the Wrong Thing: Internal Harmfulness Scores Anti-Rank Successful Jailbreaks"
  authors: "Mingyu Luo et al."
  venue: "arXiv"
  year: 2026
  url: "https://arxiv.org/abs/2608.09624"
  code: "https://github.com/kuangren777/aap-audit"
---

{{< paper >}}

This note covers arXiv v1 from August 2026; I could not find a peer-reviewed version. One disclosure: I work on the neighbouring problem for prompt injection. My paper, [PIDS-Bench]({{< ref "/posts/pids-bench" >}}), measures how injection detectors treat harmless text.

## What the paper claims

Some jailbreak defenses read the model's own internals before it writes anything: attention patterns, hidden states, the logit of a refusal word. These internal scores are usually validated one way. You collect harmful and harmless prompts and check that the score separates them. Then the score goes into a filter, and a high score is read as "this prompt is likely to break the model".

The authors argue that these are two different quantities. Harmful intent is a property of the prompt. Jailbreak success is an outcome, and it depends on the target model, the decoding settings and the judge that decides whether the reply was harmful. A score can be good at the first and useless, or worse, at the second.

Their headline result is on Llama-3.1-8B-Instruct. Wrapping harmful requests in jailbreak templates raises the rate of harmful replies from 5% to 27% and lowers the score's harmful-versus-harmless AUROC from 0.936 to 0.803. Among the 100 wrapped harmful prompts, the 27 that succeeded score lower than the 73 that failed: outcome AUROC 0.220 (95% CI 0.109 to 0.343), where 0.5 is chance. The score still notices harm. It notices it least in the attacks that work.

A second question asks whether the harmfulness reading itself survives distribution shift. Their answer is that calibration and fixed thresholds break before ranking does.

## How they tested it

The measuring tool is Active Attention Probing (AAP). Three learned embedding vectors are inserted into the system part of the chat template, at the same position for every prompt. The score is the attention the last prompt token pays to those vectors in 20 selected heads, turned into a number between 0 and 1 by an XGBoost model trained on BeaverTails. The fixed position matters because a wrapper changes the prompt: if attention is read at positions that depend on the prompt, a change in score could come from the moved read location rather than from the model. AAP is a measuring device here, not a proposed defense.

The core experiment is a matched design. The authors take 100 harmful and 100 benign goals from JailbreakBench and give each a plain and a wrapped version. There are five fixed templates (role-play, authority override, "unfiltered mode", a compliance prefix and a research pretext), with 20 goals per template and class. Benign goals get the same wrappers, so the wrapper cannot stand in for the label. Llama answers every prompt with greedy decoding and without the probe. Llama Guard 3 labels the replies, and a Qwen3-14B rubric labels them again.

They repeat the outcome test with four other channels (rare-token, a passive read with nothing inserted, and adaptations of AttentionDefense and HiddenDetect), with Mistral and Qwen as targets, and with seven stronger attacks on Llama: GCG, AutoDAN, AutoDAN-Turbo, PAIR, TAP, Best-of-N and Many-shot. For a deployment view, they set a threshold on benign prompts at a 5% false-positive budget and count which attacks get blocked.

## What the results show

The reversal is not specific to AAP. The other internal channels keep wrapped harmfulness AUROC between 0.751 and 0.828, and their outcome AUROC lies between 0.145 and 0.248 (Table 6). Llama Guard, used as a prompt classifier, sits at 0.507 and does not rank success in either direction.

The filter numbers make this concrete. At the 5% benign budget (5.7% achieved), the filter blocks 42.5% of the attacks that failed and 14.8% of the attacks that succeeded, so 23 of the 27 jailbreaks get through. That is still about 2.6 times what random blocking at the same budget would remove, and the authors say plainly that the filter is not worse than no filter. It spends most of its budget on attacks that were going to fail anyway.

The information is there, though. A readout trained on success labels, using the same internal features, reaches 0.930 out-of-fold on the wrapped harmful prompts and 0.875 when a whole template is held out.

For the shift question, the score keeps an AUROC of 0.850 on WildJailbreak, but F1 at the frozen threshold falls from 0.925 to 0.559 (Table 3). Most of that is because the source score was never calibrated and the class balance differs. After calibration on in-distribution data, the threshold reaches F1 0.667 against an oracle of 0.678. The most useful result here is about encodings. When only the harmful prompts are encoded (base64, rot13 or a Caesar shift), the score separates them well (AUROC 0.85 to 0.89), but a character-entropy statistic with no model at all reaches 0.997 to 1.000. Encode both classes and the score falls to about 0.5 under all three encodings. On base64, so does every other score, Llama Guard included.

I checked what the release allows. It contains analysis code, tests and the authors' aggregate numbers, but no per-prompt scores, labels, prompts or completions, so none of the AUROCs can be recomputed. The counts that can be checked fit together: the McNemar p-values, for example, follow from 23 against 1 flipped outcomes on Llama and 14 against 12 on Mistral.

## What they don't show

The authors state their limitations clearly. The outcome labels are automated and were never audited by humans, the three judges agree poorly (Fleiss κ about 0.3), Llama Guard guided several of the attack searches, most results use one greedy decode, Llama and Qwen give only 27 and 10 successes, and the Japanese translation condition has an artifact. Four more points came out of my reading. They are mine, not the authors'.

**The broad claims rest on fewer cells than the abstract suggests.** The abstract says the reversal persists across three targets, seven attack families and two judges. On Mistral the outcome AUROC is 0.491, which is chance. The authors argue that this cell is uninformative, because Mistral already complies with 68% of plain harmful prompts. That is fair, but it also means Mistral is not evidence of persistence. Of the 14 attack-by-judge cells, 6 have intervals below chance: GCG and AutoDAN under both judges, AutoDAN-Turbo under Llama Guard and TAP under Qwen3. Many-shot, PAIR and Best-of-N are at chance under both judges. No cell is above chance and the pooled estimate is 0.313, but the authors' own design-effect calculation puts the 23 cells at about 2.5 independent units. The clean evidence is Llama, the matched templates, and GCG and AutoDAN.

**Two templates produce most of the successes.** The paper says three of the five templates have only two successes each, and that 15.4% of success-failure pairs fall within one template. The only split of the 27 successes that fits both statements is 12, 9, 2, 2 and 2. So part of the 0.220 is about which template was used. Within templates the estimate is 0.333. Restricted to the two templates with enough successes it is 0.313, with an interval that touches chance (Appendix C).

**The labels depend heavily on the judge.** PAIR's attacked success rate is 52% under Llama Guard and 7% under Qwen3. For Best-of-N it is 94% against 26% (Table 2).

**The direction of the effect was predictable.** Ball et al. (EACL 2026) found that "effective jailbreaks noticeably reduce a model's perception of prompt harmfulness". If that holds, a score that reads harm from the model's internals should give lower scores to the jailbreaks that work. The paper cites this work. Its contribution is measuring the consequence carefully and pricing it in a filter, not discovering the mechanism.

## What I think

This is a careful paper with an unusually honest appendix. The authors report a checkpoint bug in their own pipeline and what it changed, replace a number from an earlier draft, exclude a judge substitute that scored refusals as successes, and show that much of their per-head result is what a mechanical null would produce.

The lesson is not that internal probes are bad. A score validated on harmful versus harmless prompts has been validated for that and nothing else. My reading of why the reversal happens: a jailbreak succeeds when the model fails to register the request as harmful, and an internal score reads that same registration, so among attacks it is lowest on the ones that worked. Llama Guard looks at the prompt from outside, does not reverse, and on natural WildJailbreak prompts ranks outcomes better (0.625) than any internal channel. One result does not fit my reading neatly: scores computed from Mistral's and Qwen's internals also rank Llama's successes low (Table 1). Whatever the attacks exploit seems to be shared across similar models.

If you evaluate a pre-generation filter, measure it against realized outcomes on the model you protect, name the judge, report blocking at a fixed benign budget split by outcome, and apply every transformation to both classes. The same holds for prompt-injection detectors, where "looks like an injection" and "the agent followed it" are different labels.

[check_counts.py](check_counts.py) checks the counts above against the released aggregates, using only the Python standard library. If I have misread something, I want to know: <khalidshire@kookmin.ac.kr>.
