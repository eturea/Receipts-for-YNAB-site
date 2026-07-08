#!/usr/bin/env python3
"""
Regenerate docs/Planning/Tickets/tickets.json (and the Claude Desktop
prompt's embedded data block) from YAML frontmatter in TICKET_*.md files.

Walks:
  docs/Planning/Tickets/         -> open / in-progress / deferred
  docs/Planning/Tickets/done/    -> done
  docs/Planning/Tickets/wontfix/ -> wontfix

Strict validation. Exits non-zero on:
  - Missing or malformed YAML frontmatter
  - status that doesn't match folder location
  - Unknown severity
  - Missing or non-ISO `opened` / `closed` dates
  - Terminal status (done / wontfix) without `closed` date
  - Active status (open / in-progress / deferred) WITH a `closed` date

Soft warnings (printed to stderr, do not fail default mode):
  - Title mismatch between frontmatter `title:` and body `# H1`
  - Deferred ticket without `revisit_when:` trigger
  - Duplicate active `next_up:` pins
  - `depends_on` references an unknown ticket id
  - Active ticket depends on a `wontfix` ticket
  - Active pinned ticket depends on another active pinned ticket pinned later
  - `rollup: true` ticket with no `depends_on` listed

Run from anywhere — paths are resolved relative to this script.

    python3 tools/regenerate-tickets-json.py            # write JSON + prompt
    python3 tools/regenerate-tickets-json.py --check    # exit 1 if json would change
    python3 tools/regenerate-tickets-json.py --new FOO  # scaffold TICKET_FOO.md

Stdlib only. Requires Python 3.10+.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────
# CONFIG — the ONLY per-repo block. Everything else is repo-agnostic and
# derives its paths from THIS FILE's location, so the script is drop-in
# portable: copy it into another repo's scripts dir, edit CONFIG, done.
# Never hard-code an absolute path — all paths derive from Path(__file__) so
# the script stays cwd-independent and survives spaces in the repo path.
# ─────────────────────────────────────────────────────────────────────────
CONFIG = {
    "app_id": "rfy-site",                       # short machine id embedded in tickets.json + dashboard
    "project_name": "Receipts-for-YNAB-site",   # human-facing project name
    # Xcode project dir, used ONLY for the build-version stamp. None here —
    # this is a static-site repo with no Xcode tooling at all.
    "xcodeproj": None,
}

APP_ID = CONFIG["app_id"]
PROJECT_NAME = CONFIG["project_name"]

ROOT = Path(__file__).resolve().parents[1]
PLANNING = ROOT / "docs" / "Planning"
TICKETS_DIR = PLANNING / "Tickets"
OUT_FILE = TICKETS_DIR / "tickets.json"
PROMPT_FILE = PLANNING / "CLAUDE_DESKTOP_PROMPT.md"
PBXPROJ = (
    ROOT / CONFIG["xcodeproj"] / "project.pbxproj"
    if CONFIG.get("xcodeproj") else None
)

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
# Match `**Anything:**` at start of a stripped line — the metadata-block pattern
# every ticket uses. Tightens the previous over-eager `**`-prefix skip so that
# legitimate prose starting with `**Important:**`-style emphasis is preserved.
METADATA_LINE_RE = re.compile(r"^\*\*[^*\n]+:\*\*")
JSON_BLOCK_RE = re.compile(r"```json\s*\n.*?\n```", re.DOTALL)
TICKET_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
TITLE_PREFIX_RE = re.compile(r"^TICKET\s*[—–-]\s*", re.IGNORECASE)

SEVERITY_LEGEND = {
    "P1": "Major — blocks release",
    "P2": "Minor — ship-quality polish",
    "P3": "Trivial — nice-to-have / deferred",
}

STATUS_LEGEND = {
    "open": "actionable, not started",
    "in-progress": "actively being worked on",
    "deferred": "intentionally postponed; revisit trigger documented",
    "done": "resolved and shipped",
    "wontfix": "closed without fix; rationale documented",
}

TERMINAL_STATUSES = {"done", "wontfix"}
ACTIVE_STATUSES = {"open", "in-progress", "deferred"}

# New optional planning enums. Validation is WARN-ONLY: an unknown value emits
# a stderr warning but never blocks regen (so old tickets without these fields,
# and typos, can't break the build).
EFFORT_VALUES = {"evening", "weekend", "multi-day"}   # what time slot the work fits
RISK_VALUES = {"low", "high"}                          # high = data-destructive / release / migration / schema
AREA_VALUES = {"app", "site", "marketing"}            # where the work lives; absent ⇒ treated as "app"

LOCATION_RULES = [
    (TICKETS_DIR,             ACTIVE_STATUSES),
    (TICKETS_DIR / "done",    {"done"}),
    (TICKETS_DIR / "wontfix", {"wontfix"}),
]

NEW_TICKET_TEMPLATE = """\
---
status: open
severity: P3
opened: {date}
title: {title}
#effort: TODO   optional — evening | weekend | multi-day (what time slot the work fits)
#risk: TODO     optional — low | high (high = data-destructive / release / migration / schema change)
#area: TODO     optional — app | site | marketing (default app if omitted)
---

# TICKET — {title}

**Opened:** {date}
**Priority:** P3 — TODO state the user-visible / architectural impact in one line
**Related:** TODO link the source review / commit / spec

---

## Problem

TODO: one prose paragraph that the JSON summary will pick up automatically.
Lead with the punchline (what breaks, where), not the context.

## Proposed fix

TODO

## Acceptance

- TODO
"""


def parse_frontmatter(text: str) -> tuple[dict[str, str | list[str]] | None, int]:
    """Return (frontmatter_dict, body_offset) or (None, 0) if absent.

    Supports three value shapes per key:
      `key: value`              → string
      `key: [a, b, c]`          → list[str] (inline YAML flow list)
      `key:` followed by lines  → list[str] (block YAML list)
        `  - a`
        `  - b`

    Multi-line block lists are detected when a key has an empty value AND
    the next non-blank line starts with `- ` at the same indentation level.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, 0
    fm: dict[str, str | list[str]] = {}
    lines = m.group(1).splitlines()
    i = 0

    def _strip_quotes(v: str) -> str:
        return v.strip().strip('"').strip("'")

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" not in line or line.lstrip().startswith("- "):
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Inline flow list: `key: [a, b, c]`
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            items = [_strip_quotes(x) for x in inner.split(",") if x.strip()] if inner else []
            fm[key] = items
            i += 1
            continue
        # Block list: empty value + following `- item` lines.
        if not value:
            items: list[str] = []
            j = i + 1
            while j < len(lines):
                nxt_raw = lines[j]
                nxt = nxt_raw.strip()
                if nxt == "":
                    j += 1
                    continue
                if nxt.startswith("- "):
                    items.append(_strip_quotes(nxt[2:]))
                    j += 1
                    continue
                break
            if items:
                fm[key] = items
                i = j
                continue
        fm[key] = _strip_quotes(value)
        i += 1
    return fm, m.end()


def extract_summary(body: str) -> str:
    """First non-empty paragraph after the `# Title` heading.

    Skips only the bold key-value metadata block at the top of every ticket
    (e.g. `**Opened:** 2026-04-23`). Prose lines starting with bold emphasis
    that *aren't* key:value are preserved.
    """
    lines = body.splitlines()
    seen_title = False
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not seen_title:
            if stripped.startswith("# "):
                seen_title = True
            continue
        # Boundaries that end (or skip) the search
        if stripped.startswith(("## ", "---", "```")):
            if paragraph:
                break
            continue
        if METADATA_LINE_RE.match(stripped):
            if paragraph:
                break
            continue
        if stripped:
            paragraph.append(stripped)
        elif paragraph:
            break
    summary = " ".join(paragraph).strip()
    if len(summary) > 240:
        summary = summary[:237].rsplit(" ", 1)[0] + "..."
    return summary or "(no summary)"


def ticket_id(filename: str) -> str:
    return filename.removeprefix("TICKET_").removesuffix(".md")


def compute_age_days(opened: str, closed: str | None, status: str) -> int | None:
    """Age of a ticket in whole days.

    Active tickets: today − opened (how long it's been sitting).
    Terminal tickets: closed − opened (how long it stayed open before closing).
    Returns None if the required dates don't parse (validation already flagged
    that as an error, so the record simply omits the field).
    """
    try:
        opened_d = date.fromisoformat(opened)
    except (ValueError, TypeError):
        return None
    if status in TERMINAL_STATUSES:
        if not closed:
            return None
        try:
            end_d = date.fromisoformat(closed)
        except (ValueError, TypeError):
            return None
    else:
        end_d = date.today()
    return (end_d - opened_d).days


def get_current_build() -> str:
    """Read marketing-version + build via agvtool, falling back to a direct
    `project.pbxproj` parse. Returns empty string if both fail.
    """
    # Repos configured without an Xcode project carry no build stamp — return
    # empty and never shell out to agvtool (keeps non-Xcode repos, e.g. RFY,
    # from touching Xcode tooling).
    if not CONFIG.get("xcodeproj"):
        return ""
    # 1. agvtool — works when run from the project root with the .xcodeproj present.
    try:
        marketing = subprocess.run(
            ["agvtool", "what-marketing-version", "-terse1"],
            cwd=ROOT, capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        build = subprocess.run(
            ["agvtool", "what-version", "-terse"],
            cwd=ROOT, capture_output=True, text=True, timeout=5, check=True,
        ).stdout.strip()
        if marketing and build:
            return f"v{marketing} (build {build})"
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 2. Direct pbxproj parse — agvtool is finicky about plist style and
    #    project layout; the raw file is more reliable.
    if PBXPROJ.exists():
        try:
            content = PBXPROJ.read_text(encoding="utf-8")
            mv = re.search(r"MARKETING_VERSION\s*=\s*([^\s;]+)\s*;", content)
            cv = re.search(r"CURRENT_PROJECT_VERSION\s*=\s*([^\s;]+)\s*;", content)
            if mv and cv:
                return f"v{mv.group(1).strip()} (build {cv.group(1).strip()})"
        except OSError:
            pass

    return ""


def validate_ticket(
    fm: dict[str, str],
    text: str,
    rel_path: str,
    allowed_statuses: set[str],
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block JSON generation."""
    errors: list[str] = []
    warnings: list[str] = []

    status = fm.get("status", "")
    if status not in allowed_statuses:
        errors.append(
            f"{rel_path}: status '{status}' does not match folder "
            f"(allowed: {sorted(allowed_statuses)})"
        )
        return errors, warnings

    severity = fm.get("severity", "")
    if severity not in SEVERITY_LEGEND:
        errors.append(
            f"{rel_path}: severity '{severity}' not in {list(SEVERITY_LEGEND)}"
        )

    opened = fm.get("opened", "")
    if not opened:
        errors.append(f"{rel_path}: missing 'opened' date")
    else:
        try:
            date.fromisoformat(opened)
        except ValueError:
            errors.append(
                f"{rel_path}: 'opened' date '{opened}' is not YYYY-MM-DD"
            )

    closed_raw = fm.get("closed", "")
    has_closed = bool(closed_raw)
    if status in TERMINAL_STATUSES and not has_closed:
        errors.append(
            f"{rel_path}: status '{status}' requires a 'closed' date"
        )
    if status in ACTIVE_STATUSES and has_closed:
        errors.append(
            f"{rel_path}: status '{status}' is active and must not carry a "
            f"'closed' date (got '{closed_raw}')"
        )
    if has_closed:
        try:
            date.fromisoformat(closed_raw)
        except ValueError:
            errors.append(
                f"{rel_path}: 'closed' date '{closed_raw}' is not YYYY-MM-DD"
            )

    # Soft warnings — visible signal without failing the build.
    fm_title = fm.get("title", "")
    title_match = TITLE_RE.search(text)
    if fm_title and title_match:
        h1_raw = title_match.group(1).strip()
        h1_clean = TITLE_PREFIX_RE.sub("", h1_raw)
        # Normalize both sides: drop backticks (markdown-only; YAML titles
        # can't carry them safely), collapse whitespace, lowercase. Substantive
        # word differences still trigger the warning; pure formatting drift
        # does not.
        def _norm(s: str) -> str:
            return re.sub(r"\s+", " ", s.replace("`", "")).strip().lower()
        if h1_clean and _norm(fm_title) != _norm(h1_clean):
            warnings.append(
                f"{rel_path}: title mismatch — frontmatter='{fm_title}' "
                f"vs body H1='{h1_clean}'"
            )

    if status == "deferred" and not fm.get("revisit_when", "").strip():
        warnings.append(
            f"{rel_path}: deferred without 'revisit_when:' trigger — "
            f"add a one-line condition for when to revisit"
        )

    # Optional `next_up` pin — must be a positive integer if present.
    # Lower numbers float to the top of the dashboard's "Next up" rail.
    next_up_raw = fm.get("next_up", "")
    if isinstance(next_up_raw, list):
        errors.append(f"{rel_path}: 'next_up' must be a single integer, not a list")
        next_up_raw = ""
    next_up_raw = str(next_up_raw).strip()
    if next_up_raw:
        try:
            n = int(next_up_raw)
            if n < 1:
                errors.append(
                    f"{rel_path}: 'next_up' must be a positive integer (got {n})"
                )
        except ValueError:
            errors.append(
                f"{rel_path}: 'next_up' must be a positive integer (got '{next_up_raw}')"
            )
        # Pinning a terminal ticket is almost certainly a mistake — warn loudly.
        if status in TERMINAL_STATUSES:
            warnings.append(
                f"{rel_path}: 'next_up' set on terminal ticket (status={status}) "
                f"— remove the pin or reopen the ticket"
            )

    # Optional `depends_on` — list of TICKET_IDs. Treated as documentation
    # only; cross-reference validation runs after all tickets are collected
    # (see `cross_validate_dependencies`). Here we only check shape.
    deps = fm.get("depends_on", [])
    if isinstance(deps, str):
        # Single string is allowed shorthand; coerce to a one-element list.
        deps = [deps] if deps.strip() else []
    if deps and not isinstance(deps, list):
        errors.append(
            f"{rel_path}: 'depends_on' must be a list (got {type(deps).__name__})"
        )
    elif deps:
        for dep in deps:
            if not isinstance(dep, str) or not TICKET_ID_RE.match(dep):
                warnings.append(
                    f"{rel_path}: depends_on entry '{dep}' is not a valid ticket id "
                    f"(expected UPPER_SNAKE_CASE)"
                )

    # Optional `rollup` — boolean flag that marks a ticket as a milestone-
    # rollup gate. Cross-validator warns when a rollup has no `depends_on`.
    rollup_raw = fm.get("rollup", "")
    if isinstance(rollup_raw, list):
        errors.append(f"{rel_path}: 'rollup' must be a boolean, not a list")
    elif str(rollup_raw).strip() and str(rollup_raw).strip().lower() not in (
        "true", "false", "yes", "no", "1", "0"
    ):
        warnings.append(
            f"{rel_path}: 'rollup' value '{rollup_raw}' is not a recognized "
            f"boolean (use true/false)"
        )

    # Optional `effort` / `risk` planning enums — WARN-ONLY. A present-but-
    # unknown value is flagged for cleanup but never blocks regen.
    effort_raw = fm.get("effort", "")
    effort_raw = effort_raw.strip() if isinstance(effort_raw, str) else ""
    if effort_raw and effort_raw not in EFFORT_VALUES:
        warnings.append(
            f"{rel_path}: 'effort' value '{effort_raw}' not in {sorted(EFFORT_VALUES)}"
        )
    risk_raw = fm.get("risk", "")
    risk_raw = risk_raw.strip() if isinstance(risk_raw, str) else ""
    if risk_raw and risk_raw not in RISK_VALUES:
        warnings.append(
            f"{rel_path}: 'risk' value '{risk_raw}' not in {sorted(RISK_VALUES)}"
        )
    area_raw = fm.get("area", "")
    area_raw = area_raw.strip() if isinstance(area_raw, str) else ""
    if area_raw and area_raw not in AREA_VALUES:
        warnings.append(
            f"{rel_path}: 'area' value '{area_raw}' not in {sorted(AREA_VALUES)}"
        )

    return errors, warnings


def collect_tickets() -> tuple[list[dict], list[str], list[str]]:
    tickets: list[dict] = []
    errors: list[str] = []
    warnings: list[str] = []

    for folder, allowed in LOCATION_RULES:
        if not folder.exists():
            continue
        for md_path in sorted(folder.glob("TICKET_*.md")):
            rel = str(md_path.relative_to(ROOT))
            text = md_path.read_text(encoding="utf-8")
            fm, body_offset = parse_frontmatter(text)
            if fm is None:
                errors.append(f"{rel}: missing YAML frontmatter")
                continue

            ticket_errors, ticket_warnings = validate_ticket(fm, text, rel, allowed)
            errors.extend(ticket_errors)
            warnings.extend(ticket_warnings)
            if ticket_errors:
                continue

            title = fm.get("title", "").strip()
            if not title:
                m = TITLE_RE.search(text)
                title = (
                    TITLE_PREFIX_RE.sub("", m.group(1).strip())
                    if m else ticket_id(md_path.name)
                )

            def _str(key: str) -> str:
                v = fm.get(key, "")
                return v.strip() if isinstance(v, str) else ""

            ticket: dict = {
                "id": ticket_id(md_path.name),
                "title": title,
                "status": fm["status"],
                "severity": fm["severity"],
                "opened": fm["opened"],
                "app": APP_ID,
            }
            if _str("closed"):
                ticket["closed"] = _str("closed")
            # Computed, not frontmatter: age in days. Active = today − opened;
            # terminal = closed − opened (how long it stayed open). Bad/missing
            # dates already errored above, so parsing here is safe.
            age = compute_age_days(fm["opened"], ticket.get("closed"), fm["status"])
            if age is not None:
                ticket["age_days"] = age
            if _str("revisit_when"):
                ticket["revisit_when"] = _str("revisit_when")
            # Optional planning fields: target release ("v1.1.1", "v1.1.2",
            # "backlog", etc.) and a manual pin position for the dashboard's
            # "Next up" rail. Both are free-form strings/ints — no enum.
            if _str("milestone"):
                ticket["milestone"] = _str("milestone")
            next_up_raw = _str("next_up")
            if next_up_raw:
                try:
                    ticket["next_up"] = int(next_up_raw)
                except ValueError:
                    pass  # validate_ticket already emitted the error
            # Optional `depends_on` — list of TICKET_IDs. Documentation only;
            # cross-validator (post-collection) warns on bad references, order
            # inversions vs `next_up`, and dependencies that resolve to wontfix.
            deps_raw = fm.get("depends_on", [])
            if isinstance(deps_raw, str):
                deps_raw = [deps_raw] if deps_raw.strip() else []
            if isinstance(deps_raw, list):
                deps_clean = [d for d in deps_raw if isinstance(d, str) and d.strip()]
                if deps_clean:
                    ticket["depends_on"] = deps_clean
            # Optional `rollup` flag — true/false. The cross-validator warns
            # when a rollup ticket has no depends_on.
            rollup_raw = _str("rollup").lower()
            if rollup_raw in ("true", "yes", "1"):
                ticket["rollup"] = True
            # Optional planning enums — carried through as-is when present
            # (validation is warn-only; see validate_ticket).
            if _str("effort"):
                ticket["effort"] = _str("effort")
            if _str("risk"):
                ticket["risk"] = _str("risk")
            # `area` (app | site | marketing). Emitted only when explicitly set;
            # a missing area is treated as "app" by consumers (the dashboard).
            if _str("area"):
                ticket["area"] = _str("area")
            ticket["file"] = rel
            ticket["summary"] = extract_summary(text)
            # Full markdown body (post-frontmatter) embedded for the dashboard's
            # full-page ticket view. ~700 KB total across the corpus — small
            # enough to inline in the artifact's data block.
            ticket["body"] = text[body_offset:].lstrip("\n")
            tickets.append(ticket)

    active_pins: dict[int, list[dict]] = {}
    for ticket in tickets:
        if "next_up" not in ticket:
            continue
        if ticket["status"] in TERMINAL_STATUSES:
            continue
        active_pins.setdefault(ticket["next_up"], []).append(ticket)

    for pin, pinned in sorted(active_pins.items()):
        if len(pinned) <= 1:
            continue
        ids = ", ".join(t["id"] for t in sorted(pinned, key=lambda t: t["id"]))
        warnings.append(
            f"next_up {pin} is used by multiple active tickets: {ids}"
        )

    return tickets, errors, warnings


def build_payload(tickets: list[dict]) -> dict:
    by_status = {k: 0 for k in STATUS_LEGEND}
    by_severity = {k: 0 for k in SEVERITY_LEGEND}
    open_by_severity = {k: 0 for k in SEVERITY_LEGEND}
    for t in tickets:
        by_status[t["status"]] = by_status.get(t["status"], 0) + 1
        by_severity[t["severity"]] = by_severity.get(t["severity"], 0) + 1
        if t["status"] in {"open", "in-progress"}:
            open_by_severity[t["severity"]] += 1

    return {
        "generated_at": date.today().isoformat(),
        "app": APP_ID,
        "project": PROJECT_NAME,
        "current_build": get_current_build(),
        "severity_legend": SEVERITY_LEGEND,
        "status_legend": STATUS_LEGEND,
        "summary": {
            "app": APP_ID,
            "total": len(tickets),
            "by_status": by_status,
            "by_severity": by_severity,
            "open_by_severity": open_by_severity,
        },
        "tickets": sorted(tickets, key=lambda t: t["id"]),
    }


def regenerate_prompt(payload: dict) -> bool:
    """Replace the ```json … ``` block in CLAUDE_DESKTOP_PROMPT.md with the
    fresh payload, IF the prompt is configured for inline-JSON mode.

    The current default workflow is file-attachment — the user drags
    tickets.json into Claude Desktop directly — and the prompt body has no
    JSON fence. In that mode this is a no-op (returns False, silently).
    Users who prefer to keep the JSON inline (single-paste workflow) just
    leave a ```json … ``` block in their prompt and it gets rewritten in
    place; all surrounding prose is preserved either way.
    """
    if not PROMPT_FILE.exists():
        return False
    text = PROMPT_FILE.read_text(encoding="utf-8")
    json_str = json.dumps(payload, indent=2, ensure_ascii=False)
    new_block = f"```json\n{json_str}\n```"
    new_text, n = JSON_BLOCK_RE.subn(new_block, text, count=1)
    if n == 0:
        return False
    if new_text != text:
        PROMPT_FILE.write_text(new_text, encoding="utf-8")
    return True


def scaffold_new_ticket(slug: str) -> int:
    if not TICKET_ID_RE.match(slug):
        print(
            f"ERROR: ticket id '{slug}' must be UPPER_SNAKE_CASE "
            f"(letters, digits, underscores; first char a letter)",
            file=sys.stderr,
        )
        return 1
    target = TICKETS_DIR / f"TICKET_{slug}.md"
    if target.exists():
        print(
            f"ERROR: {target.relative_to(ROOT)} already exists",
            file=sys.stderr,
        )
        return 1
    today = date.today().isoformat()
    # Sentence-case title from slug
    words = slug.replace("_", " ").lower().split()
    title = (words[0].capitalize() + " " + " ".join(words[1:])).strip() if words else slug
    target.write_text(NEW_TICKET_TEMPLATE.format(date=today, title=title))
    print(f"Created {target.relative_to(ROOT)}")
    print("Next: edit frontmatter (severity, title) + body. Then re-run without --new.")
    return 0


# Fields excluded from the --check content comparison. Each is recomputed from
# today's date or the local toolchain on every run, so it rotates without any
# ticket edit and must never mark tickets.json "stale":
#   generated_at   – date.today() stamp (top level)
#   current_build  – agvtool / pbxproj read; flips with the user's PATH
#   age_days       – today − opened for ACTIVE tickets (per-ticket, date-derived)
# These are still WRITTEN on every real regen (the dashboard renders age_days);
# they are ignored only when deciding whether the committed content is stale.
_VOLATILE_TOP = ("generated_at", "current_build")
_VOLATILE_TICKET = ("age_days",)


def _strip_volatile(payload: dict) -> dict:
    """Return a shallow copy of `payload` with today()/toolchain-derived fields
    removed, so --check compares ticket *content* only (never date drift)."""
    clean = {k: v for k, v in payload.items() if k not in _VOLATILE_TOP}
    clean["tickets"] = [
        {k: v for k, v in t.items() if k not in _VOLATILE_TICKET}
        for t in payload.get("tickets", [])
    ]
    return clean


def diff_content(existing_text: str, fresh_payload: dict) -> list[str]:
    """Content-only diff of the committed tickets.json against a freshly built
    payload. Returns human-readable differences that name the specific ticket
    ids; an empty list means only date/toolchain drift, so --check passes.

    A real change (ticket edited without regen, added, or removed) or a
    summary/legend change returns a non-empty list → --check fails (exit 1).
    """
    try:
        existing = json.loads(existing_text) if existing_text.strip() else {}
    except json.JSONDecodeError:
        return ["committed tickets.json is not valid JSON — regenerate it"]

    old = _strip_volatile(existing)
    new = _strip_volatile(fresh_payload)

    old_tickets = {t.get("id"): t for t in old.get("tickets", [])}
    new_tickets = {t.get("id"): t for t in new.get("tickets", [])}
    old_ids, new_ids = set(old_tickets), set(new_tickets)

    diffs: list[str] = []
    added = sorted(new_ids - old_ids)
    removed = sorted(old_ids - new_ids)
    changed = sorted(
        tid for tid in (old_ids & new_ids) if old_tickets[tid] != new_tickets[tid]
    )
    if added:
        diffs.append(f"ticket(s) added but not in committed json: {', '.join(added)}")
    if removed:
        diffs.append(f"ticket(s) removed since last regen: {', '.join(removed)}")
    if changed:
        diffs.append(f"ticket(s) edited without regen: {', '.join(changed)}")

    # Non-ticket drift (summary counts, legends, project/app name). These move
    # only when tickets do, but surface them so nothing changes silently.
    old_meta = {k: v for k, v in old.items() if k != "tickets"}
    new_meta = {k: v for k, v in new.items() if k != "tickets"}
    if old_meta != new_meta:
        diffs.append("summary/metadata block differs (counts or legends changed)")

    return diffs


def cross_validate_dependencies(tickets: list[dict]) -> list[str]:
    """Post-collection sweep of `depends_on` and `rollup` against the full
    ticket index. Returns warnings only — order inversions, unknown ids,
    wontfix dependencies, and rollup gates without listed dependencies are
    documentation problems, not regen-blocking errors.

    Each warning is prefixed with the source ticket's file path so the
    output line is greppable from a terminal.
    """
    warnings: list[str] = []
    by_id = {t["id"]: t for t in tickets}

    for t in tickets:
        deps = t.get("depends_on", []) or []
        status = t.get("status", "")
        rel = t.get("file", t["id"])

        # Rollup gate without listed dependencies — only warn for active
        # rollups; closed ones presumably have already been satisfied.
        if t.get("rollup") is True and status in ACTIVE_STATUSES and not deps:
            warnings.append(
                f"{rel}: rollup gate has no 'depends_on' listed — a rollup "
                f"that aggregates other work should declare what it gates"
            )

        if not deps:
            continue

        for dep_id in deps:
            dep = by_id.get(dep_id)
            if dep is None:
                warnings.append(
                    f"{rel}: depends_on references unknown ticket '{dep_id}'"
                )
                continue
            # Wontfix dependency — the gate will never resolve naturally;
            # the depender either needs to drop the link or the gating
                # decision needs to change.
            if dep.get("status") == "wontfix":
                warnings.append(
                    f"{rel}: depends on wontfix ticket '{dep_id}' — drop the "
                    f"link or revisit the wontfix rationale"
                )
            # Order inversion: both active, both pinned to next_up, depender
            # pinned strictly earlier than the dependency. The dashboard
            # will let you start the depender first, which is almost always
            # a mistake.
            this_pin = t.get("next_up")
            dep_pin = dep.get("status") in ACTIVE_STATUSES and dep.get("next_up")
            if (
                status in ACTIVE_STATUSES
                and isinstance(this_pin, int)
                and isinstance(dep_pin, int)
                and this_pin < dep_pin
            ):
                warnings.append(
                    f"{rel}: pinned at next_up={this_pin} but depends on "
                    f"'{dep_id}' pinned at next_up={dep_pin} — the dependency "
                    f"is later in your work order"
                )

    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate Beheld ticket dashboard data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 tools/regenerate-tickets-json.py\n"
            "  python3 tools/regenerate-tickets-json.py --check\n"
            "  python3 tools/regenerate-tickets-json.py --new ANALYTICS_DROP_RATE\n"
        ),
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if tickets.json would change (CI / pre-commit).",
    )
    parser.add_argument(
        "--new", metavar="SLUG",
        help="Scaffold a new TICKET_<SLUG>.md in Tickets/ and exit.",
    )
    args = parser.parse_args()

    if args.new:
        return scaffold_new_ticket(args.new)

    tickets, errors, warnings = collect_tickets()
    # Cross-ticket dependency sweep — warnings only, never blocks regen.
    warnings.extend(cross_validate_dependencies(tickets))

    for w in warnings:
        print(f"WARN:  {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 2

    payload = build_payload(tickets)
    output = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        existing = OUT_FILE.read_text(encoding="utf-8") if OUT_FILE.exists() else ""
        diffs = diff_content(existing, payload)
        if diffs:
            print(
                "tickets.json is content-stale — run regenerate-tickets-json.py:",
                file=sys.stderr,
            )
            for d in diffs:
                print(f"  - {d}", file=sys.stderr)
            return 1
        print("tickets.json is up to date (content check; date/age drift ignored).")
        return 0

    OUT_FILE.write_text(output, encoding="utf-8")
    summary = payload["summary"]["by_status"]
    print(
        f"Wrote {OUT_FILE.relative_to(ROOT)} "
        f"({payload['summary']['total']} tickets: "
        f"{summary['open']} open, "
        f"{summary['in-progress']} in-progress, "
        f"{summary['deferred']} deferred, "
        f"{summary['done']} done, "
        f"{summary['wontfix']} wontfix)"
    )
    if regenerate_prompt(payload):
        print(f"Updated {PROMPT_FILE.relative_to(ROOT)} (inline-JSON mode)")
    sys.stdout.flush()  # ensure our log lines precede the subprocess's
    refresh_dashboard()
    return 0


# Combined two-app dashboard hook. After a real write, the regenerator asks
# tickets-dashboard/merge-tickets.py to re-merge BOTH repos' tickets.json into
# the shared dashboard. This REPLACES the retired single-app refresher
# (refresh-tickets-dashboard.py).
#
# Enabled in Phase 4 now that tickets-dashboard/merge-tickets.py exists. The
# hook re-merges BOTH repos into the shared dashboard; it soft-fails so a
# missing dashboard / merge error never blocks the regenerator or its hooks.
MERGE_HOOK_ENABLED = True
MERGE_SCRIPT = Path.home() / "my_works" / "tickets-dashboard" / "merge-tickets.py"


def refresh_dashboard() -> None:
    """Refresh the combined two-app dashboard by invoking merge-tickets.py.
    Runs only on actual writes (not --check, not --new). Hard-capped at 5 s and
    never raises — a missing merge script or merge error must not fail the
    regenerator (which is on the pre-commit hook path).
    """
    if not MERGE_HOOK_ENABLED:
        return
    if not MERGE_SCRIPT.exists():
        return  # dashboard tooling not present in this environment
    try:
        subprocess.run(
            [sys.executable, str(MERGE_SCRIPT)],
            timeout=5, check=False,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        # Soft-fail: dashboard refresh is best-effort.
        pass


if __name__ == "__main__":
    sys.exit(main())
