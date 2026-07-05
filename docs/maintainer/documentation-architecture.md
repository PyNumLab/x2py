---
title: Documentation Architecture
audience: maintainers
prerequisites: repository checkout, documentation metadata standard
related: README.md, ../developer/testing-strategy.md, ../user/index.md
status: maintained
---

# Documentation Architecture

This page defines how x2py documentation is organized and maintained. It is a
repository-governance contract, not part of the product-learning material.
`mkdocs.yml` owns published navigation for the User and Developer lanes. The
Maintainer lane stays repository-only and is read through GitHub.

## Architecture Principles

1. Active documentation has three physical lanes: `user/`, `developer/`, and
   `maintainer/`. Only User and Developer documentation enters site navigation.
2. `docs/index.md` routes the two published lanes. `maintainer/README.md` is the
   repository-only entry point for maintainer policy.
3. Implemented behavior is documented as supported only when current code and
   tests prove it.
4. Planned behavior is marked explicitly and never presented as an implemented
   user contract.
5. Maintainer policy and volatile internals do not appear in user workflows.
6. Historical material remains under `old_docs/` and outside active navigation.
7. User-facing source-driven examples show the complete input source before the
   command that consumes it. Generated paths must come from an immediately
   preceding command, and commands show their expected result.

## Audience Lanes

| Lane | Primary reader | Publication | Content |
| --- | --- | --- | --- |
| `user/` | People using x2py | Documentation website | Getting Started, guides, tutorials, examples, public reference, support status, FAQ, troubleshooting, changelog |
| `developer/` | People changing x2py | Documentation website | Source orientation, implementation maps, testing, coding standards, feature work, contribution workflow |
| `maintainer/` | People governing x2py | GitHub repository only | Documentation policy, design decisions, internal architecture, CI administration, releases, roadmaps |

Pages use their primary audience for placement. A developer may consult a
maintainer design record, but that does not make governance material part of
the developer workflow. Cross-lane links should be exceptional and explain why
the reader is leaving the current lane.

## Reading Order And Cross-Links

The `nav` sequence in `mkdocs.yml` is the canonical reading order. Sequential
User documentation pages may link back to pages the reader has already
completed. They must not link from instructional prose to a later page in that
sequence. Name the later topic in plain text and say that it is covered later
instead of asking the reader to leave the current task.

Each page includes the behavior, warning, ownership fact, or limitation needed
for its current task. A forward reference never defers a fact needed now.
README documentation lists, lane indexes, and explicit navigation menus are
exceptions because choosing a destination is their purpose. Same-page anchors
and links to source or test evidence do not change documentation reading order.

## Page Metadata Contract

Every page under `docs/` starts with front matter containing:

- `title`: navigation title;
- `audience`: primary intended readers;
- `prerequisites`: assumed knowledge or pages;
- `related`: adjacent pages; and
- `status`: `maintained`, `draft`, `planned-documentation`,
  `not-yet-implemented`, `design`, or `active-roadmap`.

Pages with status `draft`, `planned-documentation`, or
`not-yet-implemented` include a `## TODO` section.

## Repository Tree

```text
docs/
  index.md
  user/
    index.md
    getting-started/
    guide/
    tutorials/
    examples/
    reference/
    language-support/
    faq/
    troubleshooting/
    changelog/
  developer/
    index.md
    contributing/
    source and workflow pages
  maintainer/
    README.md
    documentation-architecture.md
    design/
    internal-architecture/
    roadmap/
    CI and release policy
  old_docs/
```

New active pages must be created in one of the three lanes. Do not restore
top-level topic directories, place maintainer rules beside the website landing
page, or add `maintainer/` pages to `mkdocs.yml`. The `exclude_docs` setting
must exclude both `maintainer/**` and `old_docs/**` from website builds.

## Continuous Documentation Quality

- Require metadata for every active page.
- Keep website navigation, repository routing, lane indexes, and physical lanes
  synchronized.
- Reject Maintainer documentation from published site navigation.
- Check that User documentation does not link forward from instructional prose.
- Treat unsupported-feature placeholders as blocking reminders during feature
  completion.
- Run link, structure, generated-reference freshness, and executable-example
  checks in CI.
