# Applying these changes

Two ways. Pick one.

## A. Apply the patch (cleanest, keeps your history)

From inside your local clone of shirepydev.github.io, on branch main with no uncommitted changes:

    git apply --check blog-changes.patch     # dry run, should print nothing
    git am blog-changes.patch                # applies it as one commit
    hugo server                              # preview at http://localhost:1313
    git push                                 # deploys via the existing workflow

If `git am` complains about author identity, run `git am --abort` and use option B.

## B. Copy the files

Copy everything under `files/` into the repo root, keeping the folder structure. It replaces:

    hugo.yaml
    assets/css/extended/custom.css
    archetypes/posts.md
    content/about.md
    content/posts/what-is-indirect-prompt-injection.md   (front matter only changed)
    static/og-default.png                                (new)
    static/images/                                       (new, empty: your photo goes here)

Then `hugo server`, check, commit, push.

## Three things only you can fill in

1. `hugo.yaml`  -> socialIcons -> linkedin url  (search for YOUR-HANDLE)
2. `content/about.md` -> LinkedIn link at the bottom (same placeholder), and confirm the
   public email address is the one you want.
3. Your photo: save it as `static/images/yusuf.jpg`, then in `content/about.md` remove the
   `<!--` and `-->` around the image line.

## What changed and why (short)

- Research areas everywhere now read: AI security, AI safety, and AI policy (prompt injection,
  defense evaluation, AI governance). No references to VLM or drones remain.
- hugo.yaml: site title and header are your full name (findable from the paper); home page
  is PaperMod "home-info" mode (intro sentences, posts underneath) instead of a profile card
  with buttons; menu is Posts / About / Search (add Tags after ~8 posts, Archive after ~15);
  LinkedIn + email icons; full-text RSS; default social-preview image; covers open full size.
- custom.css: one accent color for links, muted centered figure captions, one callout style
  (blockquote), plus the table and inline-code tweaks you already had. 27 lines.
- archetypes/posts.md: new checklist with the two post shapes, the tag scheme (one kind tag +
  topic tags), figure house style with the three palette colors, cover/summary placeholders.
- content/about.md: rewritten around your full name, lab, research direction, why the blog
  exists, a publications list with DOI/arXiv/code links, contact, photo placeholder. It is
  written to be edited: change any sentence that does not sound like you.
- content/posts/what-is-indirect-prompt-injection.md: still a draft; only the tags line
  changed to the new scheme. Post 1 will be built on it.
- static/og-default.png: 1200x630 plain image used for link previews when a post has no cover.

Verified: builds cleanly with Hugo 0.165.0 extended (the version your workflow pins).
