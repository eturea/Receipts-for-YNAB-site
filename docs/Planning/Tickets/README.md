# Ticket System — Frontmatter Schema & Validator

Canonical reference for the ticket frontmatter schema and the
`regenerate-tickets-json.py` validator. This document is intentionally
**repo-neutral and byte-identical across all four repos — Beheld, Receipts for
YNAB, Beheld-site, and Receipts-for-YNAB-site** — each repo's `CLAUDE.md`
carries the repo-specific bits (ticket directories, the regen command path, the
triage pointer). Edit all four copies together.

`tickets.json` is generated — **never edit it by hand**. Edit the source
`TICKET_*.md` and re-run the regen script (no flags) to validate + rewrite
`tickets.json` and refresh the combined two-app dashboard.

## Computed fields (not frontmatter)

Each ticket record also carries two fields injected by the regen script:

- `app` — the owning repo (`beheld` / `rfy` / `beheld-site` / `rfy-site`), from
  the script's `CONFIG` block. The combined dashboard maps the site repos onto
  their parent app (`beheld-site` → `beheld`, `rfy-site` → `rfy`) so the
  dashboard still reads as two apps.
- `age_days` — `today − opened` for active tickets; `closed − opened` for terminal ones.

## Frontmatter schema

| Field | Required? | Notes |
|---|---|---|
| `status` | yes | `open` / `in-progress` / `deferred` / `done` / `wontfix`. Must match folder. |
| `severity` | yes | `P1` (blocks release) / `P2` (ship-quality polish) / `P3` (trivial). |
| `opened` | yes | `YYYY-MM-DD`. |
| `closed` | required for `done`/`wontfix` | `YYYY-MM-DD`. Errors out if active status carries one. |
| `title` | yes | Must match the body H1 (after stripping `TICKET — ` prefix). |
| `revisit_when` | required for `deferred` | One-line trigger condition. |
| `milestone` | optional | Free-form target release: `v1.1.1`, `v1.1.2`, `backlog`. Surfaces as a pill in the dashboard. |
| `next_up` | optional | Positive integer. Pin position on the dashboard's "Next up" rail. Active tickets only. |
| `depends_on` | optional | List of TICKET_IDs that must finish first — **same repo only, never cross-app**. Hard-blocker documentation only; never an auto-scheduler. |
| `rollup` | optional | `true` on milestone-rollup gates. Validator warns if a `rollup: true` ticket has no `depends_on`. |
| `effort` | optional | `evening` / `weekend` / `multi-day` — what time slot the work fits. Warn-only enum. |
| `risk` | optional | `low` / `high` — `high` = data-destructive / release / migration / schema change. Warn-only enum. |
| `area` | optional | `app` (default if omitted) / `site` / `marketing`. Warn-only enum. **Site work is ticketed in the site repo's own ticket system** (`~/my_works/Beheld-site`, `~/my_works/Receipts-for-YNAB-site`); the combined dashboard maps site-repo tickets to the parent app with `area: site` default, so site tickets may omit the field. *(Reversed 2026-07-08, PLAN-TIME Phase 0 — site/marketing tickets previously lived in the app repos.)* |

## Validator behavior

**Errors block regen** (missing/malformed YAML, status/folder mismatch, unknown
severity, bad date format, terminal status without `closed:`, active status with
`closed:`, `next_up` not a positive integer, `depends_on` not a list).

**Warnings print to stderr but don't block** (title mismatch, deferred without
`revisit_when`, duplicate active `next_up`, `next_up` on a terminal ticket,
unknown `depends_on`, depends on `wontfix`, order inversions, `rollup: true` with
empty `depends_on`, unknown `effort`/`risk` values).

## When you create or update a ticket

- **New ticket** → scaffold via the repo's regen script (`--new SLUG`), edit the body + frontmatter, then regen.
- **Closing** → move the file to `done/`, set `status: done` + `closed:`, add a `## Resolution` section with commit refs / verification notes, then regen.
- `next_up` reflects actual work order, not severity.
- `depends_on` is for hard technical blockers only ("X must ship first because Y"), never "nice to have first."
