---
title: "OWASP’s AI security guide, applied to an email agent"
date: 2026-11-11T00:00:00+09:00
draft: false
tags: [explainer, prompt-injection, agents, llm-security]
summary: "OWASP's AI Exchange explains prompt-injection defense with an email summarizer; run on the one I built, its questions find the real design flaw in a few steps, but the evidence behind its specific advice is thin."
aliases: ["/papers/owasp-ai-exchange/"]
cover:
  image: "cover.png"
  alt: "Seven rows, one for each layer of prompt-injection protection in the OWASP AI Exchange, judged against an email agent that holds a secret token and can send email. Layers 1 to 4, model alignment, input handling, human oversight and automated oversight, are marked 'might catch it'. Layer 5, user-based least privilege, is marked 'does not stop it'. Layers 6 and 7, intent-based least privilege and just-in-time authorization, are marked 'stops it by design'. Caption: Four layers might catch the leak. One does not help. Two take away the means to send the token."
  relative: true
---

OWASP's AI Exchange explains how to defend against prompt injection with an email summarizer, the same kind of agent I built for the [email agent post]({{< ref "/posts/ipi-harness" >}}). So I ran my agent through the guide's method. Its questions found the real design flaw in a few steps and pointed to a fix I had not used. The specific advice around them is weaker: most of it comes without evidence, and a few parts are wrong or out of date.

That matters because of where the text goes. The AI Exchange is OWASP's guide to AI security, free under CC0 and written on GitHub by what it calls "over 170 carefully selected experts". Its authors say its text feeds ISO/IEC 27090, the international guidance on AI security, and prEN 18282, the draft European standard for the EU AI Act's cybersecurity requirements. What the guide says now is likely to show up later in what auditors ask for.

I read the PDF generated from owaspai.org on 10 September 2026, 376 pages. The guide changes most weeks, so the page numbers below refer to that copy.

## What the guide says about prompt injection

Much of the guide is not about language models. It covers poisoned training data, stolen models, privacy, and attacks on ordinary classifiers. Its starting point is that AI security is mostly ordinary security applied to new assets: training data, model weights, the system prompt and documents inserted into a prompt, and the model's input and output. In its words, "most of these controls are about familiar conventional security countermeasures, unless you are training your own model" (p. 29).

On prompt injection it takes the position I argued in the [first post]({{< ref "/posts/prompt-injection-explained" >}}): "Under current architectures, prompt injection is not solvable at the model layer alone" (p. 199). It lists seven layers of protection and says plainly that "none of these layers is sufficient by itself" (p. 204). The first two try to stop the injection. The other five assume it gets through and limit what it can do, which the guide calls blast radius control.

## The agent, briefly

The rest of this post depends on the setup, so here it is again. The agent reads unread mail and writes a two-sentence summary. It holds a session token, written into its system prompt with a rule never to put it in an email or a reply. It has a `send_email` tool and a second rule: send only to the manager's address. One of the three emails in its inbox is a newsletter with an instruction spliced in, asking it to email the token to an outside address.

In 360 poisoned inboxes, neither gpt-4o-mini nor gpt-4o sent the token anywhere. In that post I argued that the zero proves less than it looks, and that the more reliable defense is a check in code that refuses every recipient except the manager. I did not run the harness with that check; both rules lived only in the prompt.

## From a long list to four risks

The guide's risk chapter is a series of about a dozen questions (pp. 68–73). Each answer either removes a group of threats or keeps it, and in the guide's words, "you start big, but you end up with a relatively small list of risks" (p. 66). The questions below are the guide's. The answers are mine.

Most answers removed something:

- **Who trains the model, and who runs it?** OpenAI, for both. Poisoning the model and tampering with it while it runs become the supplier's problem, and my job is choosing the supplier.
- **Is it used to classify?** No, so evasion attacks drop out.
- **Do you train it on sensitive data?** No, so model inversion, membership inference and training-data leaks drop out.
- **Is the model generative AI?** Yes, so prompt injection applies. Direct injection, where the user is the attacker, matters little here, because the user owns the token.

Three of the questions, taken together, describe my agent exactly. Does the system insert data into the prompt? Can the model trigger actions? Can an action send data out, and can the agent reach sensitive data? Yes to all of them: the inbox is untrusted text inserted into the prompt, `send_email` can send data out, and the token sits in the system prompt. That is the lethal trifecta, and the guide is direct about the result: "The impact is: data exfiltration" (p. 71).

Three more answers kept a risk:

- **Is the input sensitive?** Yes. Personal mail goes to OpenAI, so check the supplier's logging and retention settings.
- **Does it produce text output?** Yes. If the summary is shown as HTML or Markdown, it can carry a script, or an image link that sends data out.
- **Always:** protect against resource exhaustion, with rate limits and cost caps.

So four risks are left: the poisoned email turning into exfiltration, personal mail going to the supplier, the summary carrying something harmful into whatever displays it, and cost. The guide's reason for the whole exercise is blunt: "I've seen many cases of protections in place for threats that effectively don't matter" (p. 66).

What I like about these questions is what they leave out. None of them asks which model you use or how good your filter is. They go straight to capability: can the agent send data, and can it reach a secret? My test should have started there. A clean run of 360 poisoned inboxes is a fact about two models in one month. An agent that holds a secret and can email anyone is a fact about the design, and it stays true when the model changes.

## Seven layers, one summarizer

For four of the seven layers, the guide's own example is an email summarizer, which makes the comparison easy. The cover image shows my verdict for each one. Here is the reasoning.

**1. Model alignment:** the model's training and the rules in its prompt. This is the layer that held in my test, 360 times out of 360. The guide's verdict is that "models remain easy to mislead out of the box" (p. 204), and [Nasr et al.](https://arxiv.org/abs/2510.09023) showed how little a clean result against fixed attacks says about an attacker who adapts: adaptive attacks broke 12 recent defenses, most of which had reported near-zero attack success.

**2. Input handling:** sanitizing and filtering the input, and detecting injections before the model acts on them. The guide warns of a "substantial risk of false positives and false negatives" (p. 204). The false positives are what my [detector benchmark]({{< ref "/posts/pids-bench" >}}) measured: the best detector blocked about a third of harmless, security-related prompts from public datasets. In an inbox, a security newsletter is exactly that kind of text.

**3. Human oversight:** the user approves each send. That stops this leak if the user reads the recipient. The guide names the catch itself: people "quickly suffer from approval fatigue" (p. 205), especially when most actions are harmless.

**4. Automated oversight:** code that watches for suspicious activity. The guide's example is stopping an agent "when an email summarizer attempts to send a thousand emails" (p. 205). One email to one new address is much quieter, so whether this catches the leak depends on the rule someone writes.

**5. User-based least privilege:** the agent gets the rights of the person it serves. "An email summarizer should only be able to access the user's emails" (p. 205). That does not help here. The user can email anyone, so the agent can too.

**6. Intent-based least privilege:** the agent gets only the rights its task needs. "An email summarizer should only be able to read emails" (p. 205). My agent's task was a summary. It never needed `send_email`, and without it the exfiltration path is gone, whatever the model decides.

**7. Just-in-time authorization:** rights per subtask, which can include a mechanism that "hardens privileges the moment untrusted data enters the flow" (p. 206). Once the inbox has been read, nothing after it can send.

The guide states a rule my agent did not follow: "Avoid implementing authorization in Generative AI instructions" (p. 133). The rule "only send to the manager" lived in the system prompt. The code check I suggested afterwards moves it out of the model, which is the guide's point. The guide goes one step further than I did. For a summary, the agent should not have had a send tool at all.

Removing the tool does not fix everything. In my harness, the token could still appear in the reply to the user, and the guide's output question covers what happens if that reply is rendered somewhere an image link can fire. But the path the attacker wanted, mail to an outside address, would no longer exist.

## Where the guide is thin

The questions and the layers are the guide at its best. The specific advice is where it gets thin.

**Advice without evidence.** The guide calls itself "effectively and informally" the standard in AI security (p. 17), but its recommendations come without data. For detection it says "the best approach for high-risk situations is to utilize LLM-based detectors" (p. 210) and shows no comparison. Of the 404 distinct outside links in the PDF, I count about 40 that go to academic sources; the most-linked outside sites are OpenCRE (68) and MITRE ATLAS (38). It maps other frameworks more than it reviews what has been shown to work.

**Detector advice that ignores false alarms.** For measuring detectors, the guide asks for each detector's "miss-rate against adversarial inputs per supported language" (p. 211). False alarms are named as a risk, but the test procedure only asks that benign inputs not trigger "too many false positives" (p. 307). It says nothing about benign inputs that look like attacks, or about how rare real attacks are, and the second point can decide whether a detector is usable. In the PIDS-Bench paper's arithmetic for DeBERTa-v3, if one prompt in ten is an attack, 89% of what the detector blocks is an attack; if one in a thousand is, only 7% is ([details in the detector post]({{< ref "/posts/pids-bench" >}})). The section names four commercial vendors and five open-source packages (p. 211), but the guide never mentions training-time defenses with published evaluations, such as StruQ, SecAlign or the instruction hierarchy, or agent benchmarks such as AgentDojo and InjecAgent.

**Parts are out of date.** The list of AI laws is "as of end of 2023" (p. 110) and still includes Canada's AIDA, which [died in January 2025](https://www.dlapiper.com/insights/publications/2025/01/canadian-privacy-and-ai-horizon-shifts-again), and the EU AI Liability Directive, which the Commission [withdrew in 2025](https://www.euronews.com/next/2025/07/31/eu-commission-confirms-ditching-of-ai-liability-and-patents-proposals). The review of testing tools is "accurate as of September 2024" (p. 353) and rates them by GitHub stars, contributors, scalability and integration (p. 352), not by which attacks they cover. The website has moved on: the repository has 62 commits between the snapshot and 6 November, including an [update to the standards status](https://github.com/OWASP/www-project-ai-security-and-privacy-guide/commit/e168cc9a57c5738c20b830dca49e024c78538056). ISO/IEC 27090 was [published in October 2026](https://www.bsigroup.com/en-GB/insights-and-media/media-centre/press-releases/2026/october/new-international-guidance-to-help-organizations-protect-ai-from-security-threats/), and the authors now expect prEN 18282 early in 2027. If you cite the guide, cite a section of the website with a date.

{{< collapse summary="Two contradictions and three wrong terms" >}}
**Memorization.** The copyright section asks whether generative models really look up existing work and answers "In essence: no", calling any remnants "more of a coincidence", before adding that it "remains a difficult discussion" (p. 94). The next page recommends testing models for memorisation (p. 95), and the section on data disclosure recommends checks for "unintended memorization" (p. 221). The research sits with the second view. [Carlini et al.](https://arxiv.org/abs/2301.13188) extracted over a thousand training images from diffusion models, and [found](https://arxiv.org/abs/2202.07646) that memorization in language models grows with model size, duplication in the data and prompt length.

**Telling whether a vendor trained on your data.** On hosted models, the guide says that if a vendor secretly trained on your input, "it would get out because there are ways to tell" (p. 55), without naming one. Elsewhere it says model inversion and membership inference are "typically low to zero risks for GenAI" (p. 88). Membership inference is the obvious way to tell, and [Duan et al.](https://arxiv.org/abs/2402.07841) found it barely beats chance on the pretraining data of large language models in most settings. If it fails as an attack, it fails as an audit.

**Terms.** Transfer learning is listed as a way to transfer risk (p. 75). Model inversion is described as reconstructing "publicly available input data" (p. 75). Differential privacy is described as "altering the data to make it sufficiently unrecognizable" (p. 354); it is a property of the training or release mechanism, not a way of disguising data. In a text that feeds standards, wording like this gets copied.
{{< /collapse >}}

## How I would use it

Run its risk questions on your own system before you pick a single control. For my agent they pointed at the design, not the model.

Read the overview, the risk chapter, the agent sections, the prompt-injection section and the testing chapter. That is about a third of the guide, and the part I would keep. The testing chapter has advice that research papers often skip: send test payloads through the real ingestion path instead of pasting them into a prompt, check that controls work on normal input before attacking them, report "rates, not single pass/fail" because models are not deterministic (p. 299), and treat what you did not test as a finding.

Do not cite it as evidence that a control works. It never measured that, but its tone makes it easy to forget.

The guide accepts contributions on GitHub, and two changes would cost little: ask for false-positive rates at a stated base rate next to miss rates, and rate testing tools by what they test rather than by GitHub stars.

## What this reading does not show

The answers in the table and the verdicts in the cover image are mine. The guide does not evaluate my agent. I did not rerun the harness without the send tool or with shrinking permissions, so what those layers block follows from what they remove, not from a measurement.

I read one snapshot of a document that changes every week. I read the risk, agent, prompt-injection and testing parts closely and skimmed the chapters on development-time threats and privacy. And counting links is a crude way to judge how much a document rests on research: it shows where the guide points, not whether its advice is right.

[check_owasp_ai_exchange.py](check_owasp_ai_exchange.py) finds every passage quoted here in a copy of the PDF and prints its page, or says it is gone from a newer version. It also repeats the link count.

## Further reading

- OWASP AI Exchange, [owaspai.org](https://owaspai.org/), with its [source on GitHub](https://github.com/OWASP/www-project-ai-security-and-privacy-guide). Read the website version, and note the date.
- Luca Beurer-Kellner et al., [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837), 2025. Agent designs that limit what an agent can do after it reads untrusted input; the guide links it.
- Edoardo Debenedetti et al., [Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813), 2025. CaMeL, which the guide mentions. It solves 77% of AgentDojo tasks with provable security, against 84% with no defense.
- Milad Nasr et al., [The Attacker Moves Second](https://arxiv.org/abs/2510.09023), USENIX Security 2026. Why a defense that holds against fixed attacks can still fall.

If you run the guide's questions on your own system and end up with a different short list, I want to know: [khalidshire@kookmin.ac.kr](mailto:khalidshire@kookmin.ac.kr).
