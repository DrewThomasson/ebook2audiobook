---
name: living-wiki
description: >-
  Keep a documents folder publishable and current as a code wiki: check page names and
  links, regenerate the home page, folder pages and .order files, publish the wiki, and read
  it back. Use whenever a page under the documents folder is added, renamed, moved or
  deleted, whenever a folder appears there, before the commit, and when asked about the wiki.
---

# The documents wiki

The documents folder is published as a code wiki: the wiki renders the Markdown on the
publishing branch under that folder, so every merge into the branch updates it and nothing on
the wiki side ever runs. Nobody edits the wiki in its own UI, because those edits land as
commits on the publishing branch. Anything that should not appear on the wiki stays outside
the documents folder, because a code wiki shows every page under its folder and `.order`
cannot hide one.

| Placeholder | Meaning |
| --- | --- |
| `<docs-root>` | The documents folder the wiki publishes |
| `<wiki-check>` | The command that runs `wiki.mjs` with the repository's config |
| `<descriptions>` | The tab-separated file of page descriptions |
| `<publish-ops>` | How the wiki is published and read back, if the repository does |
| `<writers>` | The skills that write under `<docs-root>` and so run the check |

What keeps the wiki living is one check, run on every change like the other documentation
gates.

## 1. The check

```bash
<wiki-check>            # check
<wiki-check> --write    # regenerate the pages it owns
<wiki-check> --report   # also list every name the wiki may retitle
```

It fails (exit 2) on what the wiki cannot carry:

- a file or folder name anywhere under `<docs-root>` with a space, attachments and source
  documents included. Each run of spaces, with any hyphens touching it, is written as one
  hyphen: `ACT 4.0 - Activity Entry.md` is `ACT-4.0-Activity-Entry.md`, which the wiki titles
  `ACT 4.0 Activity Entry`. The failure names the hyphenated name to rename to;
- a page or folder name with `\`, `#` or a control character, or one that starts or ends
  with a period;
- a page path over 235 characters;
- two names in one folder that read as the same page title (a `-` in a file name reads as a
  space in the title);
- a relative link that leaves `<docs-root>`, names a missing file, names a folder, points at
  a local drive, or starts with `/` (the wiki reads that as a page path). A file outside
  `<docs-root>` is named as code text, never linked.

It exits 3 when the pages it generates are behind the tree, and `--write` fixes that:

- `Home.md`, the wiki's landing page;
- one page beside each folder (`apps.md` beside `apps/`), which the wiki shows as that
  folder's page;
- `.order` files, which pin only `Home` and the sections the config names at the root, and
  `index` in a folder that has one. Every other page falls in alphabetically after them, so
  adding a document never touches an `.order` file.

Each generated page opens with a marker comment. A hand-written page beside a folder has no
marker, and the check leaves it alone.

Descriptions come from `<descriptions>`. A new folder or a new page at the top of
`<docs-root>` fails the check until it has a row. A row key ending in `/*` covers every
folder directly under that path, with `{name}` standing for the folder's name.

The check reads the working tree, not the index, so an untracked file under `<docs-root>`
counts. Run it on the tree as it will be committed.

Names with a hyphen or a character outside ASCII are counted, not failed. How the server
titles and opens them is settled by reading the live wiki back (section 3).

## 2. Where it runs

The repository's static checks run it, beside its other text scans. Every skill that writes
under `<docs-root>` runs it before its commit, and `--write` when it adds a folder, after
giving the folder its row in `<descriptions>`. The extension lists them in `<writers>`.

## 3. Publishing and reading it back

How the wiki is created and read back depends on the host. Where the repository publishes
one, `<publish-ops>` names the operations. The wiki is published only after the changes are
on the publishing branch. Publish once, then read the wiki back after it and after any batch
of renames. A name shape that does not open on the server is a rename rule for `wiki.mjs` to
enforce, not a one-off fix.

## 4. Which skills run it

Every skill that writes a file under `<docs-root>` runs the check before its commit,
beside the acronym scan. The extension lists them in `<writers>`. A skill that moves changes
to the publishing branch has no wiki step of its own: the branch the wiki follows is the
update, and the check before the push is what keeps that merge publishable.
