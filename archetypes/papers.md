---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
tags: [topic-tag]   # 1-3 topic tags: prompt-injection, llm-security, agents, benchmarks, guardrails, evaluation, policy
summary: ""         # ONE sentence: what the paper finds, and the main thing to know about it. Write it last.
paper:
  title: ""
  authors: ""       # "First Author et al." if more than three
  venue: ""         # e.g. "USENIX Security" or "arXiv preprint"
  year:
  url: ""           # the paper itself (arXiv abs page, DOI or proceedings page), not a blog post about it
  code: ""          # official code or data, if released; delete the line if not
---

{{ "{{< paper >}}" }}

<!--
Delete this comment before publishing.

WHO THIS IS FOR. A researcher or engineer deciding whether to read the paper, or trying to understand it
after reading. Write so they understand it faster than they would from the abstract.

SHAPE. Use these headings unless the paper needs something else.
  What the paper claims      2-3 sentences, in plain words. Who should care and why.
  How they tested it         threat model, models, data, metric. Only what the results depend on.
  What the results show      numbers with their table or figure: "(Table 3)". Copy no table whole.
  What they don't show       gaps between the claim and the evidence. Limitations the authors state,
                             and ones they don't. Say which is which.
  What I think               your reading, labelled as yours. If you reran something, say what and how.

RULES.
  1. Keep three things apart: what the authors claim, what the experiments show, and what you think.
  2. Every number points to where it comes from in the paper.
  3. If you could not check something, write "I could not verify this", not a guess.
  4. If you reran their code, report the number you got next to theirs, even if it matches.
  5. Figures: copy a figure only if the paper's license allows it (CC BY does; arXiv's default license
     does not). Otherwise make your own chart or point to the figure number.
  6. 800-1500 words. Read it aloud once. Cut what repeats.
  7. When it is published, tell the authors. Send them the link and ask them to correct anything you got wrong.
-->
