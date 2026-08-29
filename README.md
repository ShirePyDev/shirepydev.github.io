# shirepydev.github.io — AI Security blog

Hugo + PaperMod, deployed free on GitHub Pages. The theme is vendored in
`themes/PaperMod` (no git submodules), so the repo is self-contained: clone,
push, it builds.

## Go live (one time, ~10 minutes)

1. **Create the repo.** On GitHub, create a new **public** repo named exactly
   `shirepydev.github.io` (repo name = your URL). No README, no license —
   completely empty.

2. **Push this folder.** From inside this folder:

   ```bash
   git init
   git add .
   git commit -m "Initial blog setup"
   git branch -M main
   git remote add origin https://github.com/ShirePyDev/shirepydev.github.io.git
   git push -u origin main
   ```

3. **Turn on Pages.** On GitHub: repo → Settings → Pages → under "Build and
   deployment", set **Source: GitHub Actions**. The workflow in
   `.github/workflows/hugo.yml` runs on every push. First run takes ~1 minute
   (check the Actions tab). Your site is then live at
   **https://shirepydev.github.io/**

## Before you publish anything

Open `hugo.yaml` and edit every line marked `# EDIT`. Then rewrite
`content/about.md` in your own words — it is a draft, not final copy.

## Writing workflow (every post)

```bash
hugo new content posts/my-post-name.md   # creates from the posts archetype
# write in content/posts/my-post-name.md
hugo server -D                            # preview at http://localhost:1313 (drafts visible)
# when ready: change  draft: true  ->  draft: false
git add . && git commit -m "Post: my post name" && git push   # auto-deploys
```

The first post is already outlined for you (as a draft, so it will NOT appear
on the live site until you finish it):
`content/posts/what-is-indirect-prompt-injection.md`

## Local preview: install Hugo on your machine

You need the **extended** edition, v0.146 or newer (the workflow pins 0.165.0).

- **macOS:** `brew install hugo`
- **Windows:** `winget install Hugo.Hugo.Extended`
- **Ubuntu/Debian:** download the `hugo_extended_*_linux-amd64.deb` from
  https://github.com/gohugoio/hugo/releases and `sudo dpkg -i` it
  (the version in `apt` is usually too old for PaperMod).

Verify with `hugo version` — the output must contain the word `extended`.

## Features already wired up

- Home page profile card (name, tagline, buttons) — edit in `hugo.yaml` under `profileMode`
- Post list with reading time, tags, table of contents, copy-code buttons
- Search page at `/search/` (client-side, Fuse.js — built into PaperMod)
- Archive at `/archives/`, tags at `/tags/`, RSS at `/index.xml`
- Light/dark mode following the reader's system, with a manual toggle
- Syntax highlighting via Hugo's Chroma (PaperMod's own light/dark styles)
- LaTeX per post: put `math: true` in a post's front matter (loads KaTeX from CDN only on those pages)
- Writing checklist baked into every new post (see `archetypes/posts.md`)

## Maintenance notes (honest ones)

- **Theme updates are manual** because the theme is vendored. Every few months:
  download a fresh copy of https://github.com/adityatelange/hugo-PaperMod,
  replace the `themes/PaperMod` folder, run `hugo server` to check nothing
  broke. Vendoring was a deliberate trade: beginners lose hours to submodule
  problems; you lose nothing except auto-updates.
- **Custom domain later:** buy a domain, add a `CNAME` file containing it to
  the repo root, point DNS per GitHub's docs, and update `baseURL` in
  `hugo.yaml`. Do this only after ~10 posts exist. Content first.
- **Comments:** intentionally off. If you want them later, giscus (GitHub
  Discussions-based) is the standard choice for this stack.
