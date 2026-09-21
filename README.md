# Yusuf Khalid Shire · AI Security, Safety & Policy

**[shirepydev.github.io](https://shirepydev.github.io/)**

Research notes on how language-model systems are attacked, how their defenses fail, how to measure that failure honestly, and what those measurements should mean for the rules we write for deployed AI.

This repository is the source of the blog: every post, every figure, and the code behind every result.

## Why this exists

When I started working in AI security, most of what I could find was one of two things: research papers that assume you already know the field, or social-media threads that are loud and often wrong. Short, sourced, reproducible explanations were rare. This blog is written into that gap.

It is also how I check my own understanding. If I cannot explain an attack in plain language, with a concrete example and a number I can source, I do not understand it yet.

## What you will find

| Kind | What it is |
|---|---|
| **Explainers** | How an attack or defense works, starting from something you can run rather than a definition. |
| **Research** | Write-ups of my own work, ending with the experiment I would run next. |
| **Paper notes** | Close readings of papers worth your time. |
| **Build logs** | Projects as they were built, including the parts that went wrong. |

The recurring themes are prompt injection (direct and indirect), the security of LLM agents and retrieval systems, how prompt-injection detectors are evaluated, and where that evidence meets AI safety requirements and policy.

## Standards

- **Reproducible.** A post that makes a claim ships the code behind it. Each post lives in its own folder under [`content/posts/`](content/posts/), with its scripts next to the text, so you can run exactly what I ran.
- **Sourced.** Every number links to where it came from, or to my own experiment.
- **Honest about failure.** Expectations are stated before results, and negative results stay in.
- **One idea per post.** If a post needs "and also", that is the next post.

## Research

- Yusuf Khalid Shire and Sang-Chul Kim. **PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift.** *IEEE Access*, vol. 14, 2026. [DOI](https://doi.org/10.1109/ACCESS.2026.3728186) · [arXiv](https://arxiv.org/abs/2609.15017) · [Code](https://github.com/ShirePyDev/Prompt-Injection-Detection-System)

## About the author

I am a Master's student in the Department of AI Convergence at Kookmin University in Seoul, working in MCLab with Professor Sang-Chul Kim. More on the [About](https://shirepydev.github.io/about/) page.

## Corrections and feedback

If you find an error, or run a demo and get a different result, please [open an issue](https://github.com/ShirePyDev/shirepydev.github.io/issues) or email [khalidshire@kookmin.ac.kr](mailto:khalidshire@kookmin.ac.kr). Corrections are welcome.

## License

- **Writing and figures** (posts, pages and images) are licensed under [CC BY 4.0](LICENSE). You may reuse and adapt them, including commercially, as long as you credit the author and link to the source.
- **Code** (the scripts that accompany posts, code samples inside posts, and the site's own layouts and styles) is licensed under [MIT](LICENSE-CODE).
- **Not covered:** photographs of the author in [`static/images/`](static/images/), and the [PaperMod](themes/PaperMod/) theme, which keeps its own [MIT license](themes/PaperMod/LICENSE).

---

<sub>Built with [Hugo](https://gohugo.io/) and the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme, deployed to GitHub Pages with GitHub Actions.</sub>
