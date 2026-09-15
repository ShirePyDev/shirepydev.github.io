---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
tags: [kind-tag, topic-tag]   # exactly one kind tag: research | explainer | build-log | paper-notes | experiment
                              # plus 1-3 topic tags: prompt-injection, llm-security, vlm-security, benchmarks,
                              # adversarial-ml, agents, rag, tooling
summary: ""   # ONE sentence that states the claim. Used as meta description, RSS summary and list blurb. Write it last.
# cover:                       # only if the post has a real figure that summarizes it; a forced cover is worse than none
#   image: "cover.png"         # lives next to index.md (this post must then be a page bundle: posts/<slug>/index.md)
#   alt: ""                    # what a screen reader should say
#   caption: ""                # optional, shown under the image
# math: true                   # only if this post uses LaTeX
---

<!--
Delete this comment before publishing.

SHAPE. Pick one.
  research / experiment:  the finding -> why the usual view misses it -> what we measured (short)
                          -> what happened -> what I'd test next -> paper/code links
  explainer / build-log:  what it is -> one concrete example -> why it is hard -> what actually helps
                          -> further reading

RULES.
  1. One idea per post. If you need "and also", that is the next post.
  2. First paragraph: the point, in plain words. No "in this post I will".
  3. Every number has a link to where it comes from. Every claim has a source or your own experiment.
  4. Define a term in a clause the first time it appears. No glossary section.
  5. Depth goes in a collapse block:  {{</* collapse summary="Details for the curious" */>}} ... {{</* /collapse */>}}
  6. Say what you expected before you say what happened. Keep the failures in.
  7. End research posts with a section named exactly "What I would test next".
  8. Read it aloud once. Cut 20%.

FIGURES (house style, same on every post).
  Palette:  accent #1f6f8b (the thing we care about) | gray #8a8a8a (baseline, context) | warm #d1495b (attack, blocked, bad)
  Charts:   matplotlib, transparent background, no top/right spines, labels in plain words, one message per chart,
            export SVG or PNG 1600px wide.
  Diagrams: clean SVG (one tool for the whole blog).
  Every figure uses the shortcode so it gets alt text and a caption that says what to see:
    {{</* figure src="fig-1.png" alt="..." caption="..." */>}}
  Tables: only to compare, never wider than five columns, never copied from a PDF.
-->
