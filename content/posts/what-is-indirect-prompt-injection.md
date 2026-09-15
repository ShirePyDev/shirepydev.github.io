---
title: "What Is Indirect Prompt Injection (and Why Filters Keep Missing It)"
date: 2026-08-27
draft: true
tags: [explainer, prompt-injection, llm-security]
summary: ""   # ONE sentence that states the claim. Write it last.
---

<!--
THIS IS AN OUTLINE, NOT A POST. I deliberately did not write it for you.
Your blog only works if it is in your voice — write each section yourself,
then delete these comments. Target: 800–1,500 words. This is a topic you
know better than almost anyone reading; write like you're explaining it
to yourself one year ago.
-->

## The one-sentence version

<!-- Define indirect prompt injection in ONE sentence a CS undergrad understands.
     Then one short paragraph: direct vs indirect — who controls the malicious text? -->

## A concrete example

<!-- Walk through ONE minimal scenario end to end. E.g., an email assistant that
     summarizes a message containing hidden instructions. Show the actual attack
     text in a code block. Keep the example harmless and illustrative — the point
     is the mechanism, not a working exploit. -->

## Why this is hard to fix

<!-- Your core expertise. Explain: the model can't reliably separate instructions
     from data because both are just tokens. Reference the ICLR 2025 paper you
     presented ("Can LLMs Separate Instructions from Data?") — you already know it. -->

## Why detectors struggle

<!-- 2–3 short paragraphs from your benchmark work: over-defense on benign text
     that "looks like" attacks, distribution shift, obfuscation. Cite your own
     IEEE Access paper here once it has a DOI. Do NOT paste results tables —
     link to the paper. -->

## What actually helps (a little)

<!-- Honest, sourced list: privilege separation, tool-call confirmation,
     provenance tracking, spotlighting/delimiters and their limits. Be blunt
     about what is mitigation vs. solution. -->

## Further reading

<!-- 3–5 links max: the Greshake et al. paper that named indirect PI, one good
     survey, one defense paper, your own paper. Verify every link opens. -->
