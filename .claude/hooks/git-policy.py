#!/usr/bin/env python3
"""git-policy: a Claude Code PreToolUse hook on Bash and Monitor that enforces the branch model.

It is the early warning; the git hooks (pre-commit, pre-push, reference-transaction) are the
authority. Reads the hook payload on stdin, finds every git and gh command in the Bash command text,
and denies (exit 2, one line on stderr naming the rule) when one breaks a rule. Policy is decided
from the repository the command acts on: `git -C X`, `--git-dir`, `--work-tree`, else the last
`cd X` earlier in the chain, else the payload's cwd (with the folders a cd that may not run adds,
each checked). Not inside a repository: allowed.

Universal rules, every repository:
  U1  push with --force, -f, --force-with-lease, --force-if-includes, or a + refspec
  U2  push naming local-history, or --all or --mirror
  U3  push with --no-verify or -c core.hooksPath=; a push of a wip/* branch; a push whose outgoing
      commits carry "do not push" or "local only"; a push whose source cannot be resolved from the
      command and the config with certainty ("name the refspec"): a bare push follows
      remote.<r>.push, else push.default (simple, current, upstream; matching and nothing are
      refused). Grouped short flags (-uf, -Df) are split before every check.
  U4  branch deletion and ref removal (branch -d/-D, push --delete, a :X refspec, update-ref -d,
      worktree remove --force); any rename (branch -m/-M/--move), which deletes the old name: copy it
      with branch -c (gh-ticket#57); commit --amend, rebase, reset --hard on or naming a protected
      branch (PROTECTED_BRANCHES)
  U5  gh ticket merge --no-codex, or a prefix of it at least 3 long (--n, --no-c: argparse takes
      them): the owner's, from his own terminal
  U6  any gh invocation whose words include pr followed by create or merge, wherever the flags
      sit: use gh ticket pr / gh ticket merge; except one of four help lines given as the whole
      command text: gh pr merge|create --help|-h (gh-ticket#30). gh help pr merge|create stays
      refused: a gh alias named help can shadow the built-in help command
  U7  a gh or git command whose argv xargs assembles from stdin, or a script from its arguments
      ($@, $1), when a word that decides U1 to U6 or P1 to P3 cannot be read: name it on the line
  U8  a command word git-policy cannot read (gh-ticket#44): the head of any command the parser yields
      (the top, a shell's script, env's split string, a here-string), or git's subcommand at a git
      head, spelled through expansion, substitution, a glob, a brace list, zsh's =cmd or quoting the
      hook cannot decode ($'\\147\\150', $X, "$X", `...`, gi[t]), or built by an unquoted $( ), which
      the parser cuts at (g$(printf h), $(...) pr merge): write it literally. Only a segment that starts
      a command is read so: the words the parser cuts off after a ), inside ${ } or inside $(( )) are a
      tail, a parameter's text or an operand, never a head; after an assignment's or a leading
      redirection's $( ) (X=$(date) "$G" ...) the command word is still to come. In case WORD in ... esac
      a pattern list up to its ) is no head, and the command after the ) is one (gh-ticket#48). A path may start with ~/
      or a quoted variable, "$VAR"/path, "${VAR}"/path or "$VAR/path" (a plain name, literal parts),
      read by its last part. R5 (gh-ticket#49): a variable head ($S/tool, $PY, "$PY") is read as its value when
      the whole command text is plain (plain(): no eval, source, ., trap, alias, shell -c, env -S, heredoc,
      here-string, continuation, $', comment or quoted assignment, and only ; && || and newline between commands),
      the text assigns the name exactly once, unconditionally, to a literal (S=/opt/homebrew/bin;
      $S/tool), before any compound command, with no shell-managed name or dynamic writer, and the value is not
      cd, pushd or popd; the command is then checked as written with only the head's U8 off,
      and again with the value, and either refusal refuses. Option (3), the shim
      reading of an unresolved head, waits behind VARIABLE_HEADS_SHIM (owner-dated, off). When shlex cannot
      lex the line, or a written word does not lex alone to its decoded word, the words are not aligned and any quote, $ or backslash in a command word is
      unreadable. A word behind a runner is not checked: that is the gh shim's (gh-ticket#45),
      and the git hooks are git's authority
  U9  text that would get past the gh shim (gh-ticket#45), read as raw text like the backstop (quotes ignored,
      heredoc bodies included): (c1) the shim's marker GH_TICKET_INNER named anywhere, a word character before it
      included (-S<name>, X<name>; gh-ticket#53), when no word character follows it; (c2) gh named by a path, a run
      of text (cut at whitespace, ; & | ( ) < >, quotes and backquotes) ending in /gh in any case, except a path to
      the shim (shim/gh) and gh's own folders (~/.config/gh, ~/.local/share/gh, ~/.local/state/gh, ~/.cache/gh);
      (c3) text that sets PATH and names gh: PATH= or PATH+= at a word start, export, typeset, declare, local or
      readonly naming PATH in the same simple command, or zsh's path=(, path+=( and path[, in a text that also names
      gh or gh-ticket as a word, any case (at the start, or after whitespace, ; & | ( / a quote or a backquote; not
      high, ghost, gh_ or .gh). A PATH set alone, and reading $PATH, are allowed. It speaks after
      the parse's U1 to U6 and P rules and the backstop, and before U7 and U8
  U10 text that would hide an agent session from the git hooks (gh-ticket#57), read as raw text like U9, heredoc
      bodies included, backslash-newlines joined: (c1) a session marker (SESSION_MARKERS, the names pre-push and
      reference-transaction read) named anywhere, quotes ignored, a word character before it included, when no word
      character follows it, reads included; (c2) a command started with the environment cleared, read from shlex's
      POSIX words (a quoted value one word, an empty one kept, each word holding whitespace lexed again, to depth 4):
      an env word (by basename, any case) whose option run holds -, -i, a prefix of --ignore-environment from --i, a
      short cluster with i before a value-taking letter (u C S P L U), or an -S value doing so; an exec word whose
      option run holds a cluster with c (-a takes a value). Both option runs read past a redirection. It fails
      closed: a text or word shlex cannot read, or an error in the scan, goes to a cautious fallback over SHIM_RUN's
      runs that consumes no value; a crash anywhere else in this hook still runs U10 before failing open; an error
      inside U10 is one stderr line naming it. It speaks after U9 and before U7 and U8
How the text is read (gh-ticket#40, gh-ticket#44): every text is parsed (no fast path, so g\\h is
gh), and a backslash-newline is joined outside single quotes (a cd so joined adds a candidate).
Shell reserved words (if, then, do, !) are structure; every
word whose basename is gh or git (any case) is checked from there, behind any runner (nice,
timeout, sudo -u x, ssh host); a shell word anywhere is read with its own options, and its -c
operand checked as a script, as is env's split string (-S STR, -SSTR, --split-string=STR) at any
index, and a here-string or heredoc fed to a shell; a script or split string behind xargs keeps
xargs's placeholders (U7); a here-string (<<<EOF) is not a heredoc, and a word is a redirection
only when its operator is unquoted; { and } split commands only as words (the group command), so
xargs -I {} keeps its placeholder. A cd inside a structure, a script, a split string, behind a
wrapper (env cd) or a runner, or spelled CD, adds a folder to check, never moves there. The cost:
a forbidden shape typed unquoted as another command's arguments (echo gh pr merge) is refused
too: quote it. No word is exempt, a shell's data after its -c script included (bash -c '...' _
git commit), and any -S STR is read as a split string (git log -S 'git push --force' is
refused). After the parse, a raw-text backstop (gh only) refuses a pipeline
(backslash-newlines joined, then split at ; && || & and newlines, never at |, ignoring quotes,
heredoc bodies included) whose case-insensitive whole words name gh, pr and merge
or create (U6), or gh, ticket, merge and a --no-codex prefix (U5), whatever its shape: put such
text in a file, or search with the Grep tool. Its refusal speaks before U7's and U8's. The backstop skips
only those four U6 help lines.
PR rules, only in the opted-in repositories (hooks/opt-in.txt next to this file, plus the
repository a per-repo copy is committed in), unless the file git-policy-off exists in the
repository's common git dir:
  P1  commit, rebase, cherry-pick, am, revert, and a merge or pull that is not a fast-forward (--ff-only, or
      pull with pull.ff=only), on main or develop
  P2  a push that names no refspec ("name the refspec": git push -u origin <branch>), whatever the
      config would send; a push that would update main or develop (creating develop while origin
      lacks it is allowed)
  P3  a new branch (checkout/switch -b -B -c -C --create --force-create --orphan, branch, branch
      -c -C -m -M, worktree add, stash branch) not named (fix|feat|chore|worker)/<digits>-<slug>,
      (probe|spike|wip)/<slug>, or worktree-<slug> (Claude Code's worktree isolation)
Fails open: a crash is logged to ~/.cache/gh-ticket/git-policy.log and exits 1, which Claude Code
treats as non-blocking; U10 runs on the text first, so its refusal still exits 2. While the directory ~/.cache/gh-ticket/capture exists, every raw payload
is written there (payload-NNN.json), the way the test fixtures were captured. Tests:
hooks/tests/git-policy-tests.py (GIT_POLICY_TEST_CRASH=1 forces a crash there).
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

OWNER = "eturea"
INTEGRATION = ("main", "develop")
PROTECTED_BRANCHES = ("fix/v115-restore-reseeds-stock-pool",)
MARKERS = re.compile(r"do[ _-]*not[ _-]*push|local[ _-]*only", re.IGNORECASE)
BRANCH_OK = re.compile(r"^(fix|feat|chore|worker)/\d+-[A-Za-z0-9._-]+$|^(probe|spike|wip)/[A-Za-z0-9._/-]+$"
                       r"|^worktree-[A-Za-z0-9._-]+$")       # worktree-agent-<hex>: Claude Code's worktree isolation
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix",
                       "--config-env", "--list-cmds", "--attr-source"}
RESERVED = {"!", "if", "then", "elif", "else", "fi", "while", "until", "do", "done", "esac", "function"}   # guard.py's CONTROL, no braces
SHELLS = {"bash", "sh", "zsh", "dash"}
# git subcommands check_git reads: fed by xargs, their words cannot be read (U7)
RULED = {"branch", "update-ref", "worktree", "commit", "rebase", "reset", "push", "merge", "pull", "cherry-pick", "am",
         "revert", "checkout", "switch", "stash"}
VAR = r"[A-Za-z_][A-Za-z0-9_]*=.*"
# merge and pull options that take the next word, pull's fetch-side ones included (git fetch --help);
# -S, --gpg-sign, --log, --rebase and --recurse-submodules attach theirs with = and take no separate word
MERGE_LONG_WITH_VALUE = ("--message", "--file", "--strategy", "--strategy-option", "--cleanup", "--into-name",
                         "--server-option", "--upload-pack", "--depth", "--deepen", "--shallow-since", "--shallow-exclude",
                         "--negotiation-tip", "--refmap", "--jobs", "--filter")
MERGE_OPTS_WITH_VALUE = {"-m", "-F", "-s", "-X", "-o", "-j", *MERGE_LONG_WITH_VALUE}


def merge_opt_takes_value(a):
    """-m, --message, and any unique abbreviation git accepts (--mess); never an --opt=value form."""
    if a in MERGE_OPTS_WITH_VALUE:
        return True
    return a.startswith("--") and len(a) >= 3 and "=" not in a and any(o.startswith(a) for o in MERGE_LONG_WITH_VALUE)
PUSH_OPTS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec", "--recurse-submodules"}
# --signed[=(yes|no|if-asked)] takes its value attached only: a standalone --signed consumes nothing.
HERE = Path(__file__).resolve().parent
LOG = Path.home() / ".cache/gh-ticket/git-policy.log"


class Deny(Exception):
    def __init__(self, rule, reason):
        super().__init__(f"{rule}: {reason}")
        self.rule, self.reason = rule, reason


# ---------------------------------------------------------------- command text -> segments

def strip_heredocs(text):
    """Drop heredoc bodies; a body fed to a shell (bash <<EOF) becomes a here-string, read as a script (N7).
    A here-string (<<<EOF) is not a heredoc (N4)."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        m = re.search(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        if not m:
            out.append(line); i += 1; continue
        j = i + 1
        while j < len(lines) and lines[j].strip() != m.group(2):
            j += 1
        fed = any(os.path.basename(w).lower() in SHELLS for w in re.split(r"[\s|;&(){}]+", line[:m.start()]))
        body = " <<<" + shlex.quote("\n".join(lines[i + 1:j])) + " " if fed else " "
        out.append(line[:m.start()] + body + line[m.end():])
        i = j + 1
    return "\n".join(out)


WORD_EDGE = " \t\r\n;&|()"
CASE_LEAD = {"!", "if", "then", "elif", "else", "while", "until", "do"}   # reserved words a case statement may follow


def split_segments(text):
    """Split on &&, ||, ;, |, &, newlines, ( ) and $( ) outside quotes; on { and } only where one stands as a word
    (the group-command words), so xargs -I {} and {a,b} stay words; and at ${ and its closing }, as before.
    -> [(segment, starts, joins)] (gh-ticket#44). starts when the segment begins a command: after a separator, a
    group's ( or {, or a $( (its body), and after the ) of a $( or $(( that an assignment or a redirection held
    before the command word (X=$(date) "$G" ...), when a new word follows. Not after any other ) or }, inside ${ },
    or inside $(( )), where the cut leaves a command's tail, a parameter's text or an arithmetic operand: the U8 head
    rules read only the first kind. joins: the indexes of the words a backslash-newline was joined into.
    A case statement (gh-ticket#48): in case WORD in ... esac, a pattern list up to its ) (an optional leading (, one
    word, | and one word more), after the in or after ;; ;& ;;&, starts no command; the command after its ) does. The
    cuts and the parens stack stay as before; only those flags change. Anything else where a pattern list stands puts
    every flag back and ends the case reading for the rest of the text, which then splits as before; so do a comment
    anywhere, and a $( ${ <( >( or backquote in a pattern, quoted or not (Codex C1, C2)."""
    segs, cur, i, q, param = [], [], 0, None, 0
    parens, starts, joins = [], True, set()             # open parens: ("sub" $( | "arith" $(( and its inner ( |
                                                        # "group" (, whether the command word is still to come)
    # cases: the open case statements, innermost last: depth (len(parens) where its words are read), mode ("pattern"
    # or "body"), at (where the pattern's text starts in cur), lead (a ( or | was read), seen (its first word was
    # read). held: (segment index, flag as before) for a pattern list's segments until its ) confirms them. today:
    # the flag the segment being built had before; word_pos: a reserved word is read there (not after a ) ); probe:
    # this segment may still open a case or close one (esac); off: the case reading ended.
    cases, held, off, today, word_pos, probe = [], [], False, True, True, True

    def cut(next_starts, next_today=None, next_word_pos=True):
        nonlocal cur, starts, joins, today, word_pos, probe
        if starts != today:
            held.append((len(segs), today))
        segs.append(("".join(cur), starts, joins)); cur = []; starts = next_starts; joins = set()
        today, word_pos, probe = next_starts if next_today is None else next_today, next_word_pos, True

    def put_back():                                     # a pattern list that was not one keeps the flags as before
        nonlocal starts
        for k, t in held:
            segs[k] = (segs[k][0], t, segs[k][2])
        held.clear(); starts = today

    def stop():
        nonlocal off
        put_back(); cases.clear(); off = True

    def join():                                         # a backslash-newline joined into word k of this segment
        so_far = "".join(cur)
        k = len(words_as_written(so_far))
        joins.add(k if not so_far or so_far[-1] in " \t\r\n" else k - 1)
    while i < len(text):
        ch = text[i]
        if q:
            if q == '"' and not off and (ch == "`" or text.startswith(("$(", "${"), i)) and cases \
                    and cases[-1]["depth"] == len(parens) and cases[-1]["mode"] == "pattern":
                stop()                                  # a substitution in a pattern runs: no pattern (Codex C2)
            if ch == "\\" and q == '"' and i + 1 < len(text):
                if text[i + 1] != "\n":                 # a backslash-newline is joined, as the shell joins it
                    cur.append(text[i:i + 2])
                else:
                    join()
                i += 2; continue
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in ("'", '"'):
            q = ch; cur.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < len(text):
            if text[i + 1] != "\n":                     # gi\<newline>t is git (gh-ticket#44)
                cur.append(text[i:i + 2])
            else:
                join()
            i += 2; continue
        in_arith = bool(parens) and parens[-1][0] == "arith"
        if ch == "#" and not off and (i == 0 or text[i - 1] in " \t\r\n;&|()<>"):
            stop()                                      # a comment: case reading ends here (Codex C1)
        ctx = cases[-1] if cases and cases[-1]["depth"] == len(parens) else None
        word_end = ch in " \t\r\n;&|()<>" and text[i - 1:i] not in ("", " ", "\t", "\r", "\n")
        if probe and not off and word_end and not (ctx and ctx["mode"] == "pattern"):
            w = words_as_written("".join(cur))
            lead = next((k for k, x in enumerate(w) if x not in CASE_LEAD), len(w))
            if ctx and w == ["esac"]:                   # the body's esac closes its case
                cases.pop(); probe = False
            elif not (starts and word_pos and not param and not in_arith) or len(w) > 8 or w[lead:lead + 1] not in ([], ["case"]):
                probe = False
            elif len(w) - lead >= 3:
                probe = False
                if len(w) - lead == 3 and w[-1] == "in" and ch in " \t\r\n(":
                    cases.append({"depth": len(parens), "mode": "pattern", "at": len(cur), "lead": False, "seen": False})
                    continue                            # read ch again, in the pattern list
        if not off and ctx and ctx["mode"] == "pattern":
            if word_end and not ctx["lead"] and not ctx["seen"]:
                alt = words_as_written("".join(cur[ctx["at"]:]))
                ctx["seen"] = bool(alt)
                if alt == ["esac"]:                     # esac where a pattern stands closes the case
                    put_back(); cases.pop(); probe = False
                    continue                            # read ch again, outside it
            if ch in "\n(|)":
                alt = words_as_written("".join(cur[ctx["at"]:]))
                before = not alt and not ctx["lead"]    # nothing of this pattern read yet
                if ch == "\n" and before:
                    cut(False, True); ctx["at"] = 0
                    i += 1; continue
                if ch == "(" and before:                # the optional leading (, pushed as before
                    parens.append(("group", False)); ctx.update(depth=len(parens), lead=True)
                    cut(False, True); ctx["at"] = 0
                    i += 1; continue
                if ch == "|" and len(alt) == 1 and not text.startswith("||", i):
                    cut(False, True); ctx.update(at=0, lead=True)
                    i += 1; continue
                if ch == ")" and len(alt) == 1:         # the pattern list is confirmed; a command starts after it
                    if parens:
                        parens.pop()                    # popped as before
                    ctx.update(depth=len(parens), mode="body")
                    cut(True); held.clear()
                    i += 1; continue
                stop()
            elif ch in ";&{}`" or text.startswith(("$(", "${", "<(", ">("), i):
                stop()
        elif not off and ctx and ctx["mode"] == "body":
            if ch == ";" and not param and not in_arith and text.startswith((";;", ";&"), i):
                cut(False, True); ctx.update(mode="pattern", at=0, lead=False, seen=False)
                i += 3 if text.startswith(";;&", i) else 2
                continue
            if ch == ")":                               # closes what holds the case: read as before from here
                stop()
        if text.startswith("$(", i):
            pending = False                             # U8: a head word the substitution builds (gh-ticket#44)
            if starts and not param:
                pending = substitution_head("".join(cur))
            arith = text.startswith("$((", i)
            parens.append(("arith" if arith else "sub", pending))
            cut(not arith); i += 2; continue
        if ch == "&" and ((cur and cur[-1] in (">", "<")) or text.startswith("&>", i)):
            cur.append(ch); i += 1; continue          # a redirection (2>&1, >&2, &>file), not a separator
        opens_param = closes_param = False
        if ch == "{" and i > 0 and text[i - 1] == "$":
            param += 1; opens_param = True              # ${x}git: split as before, at the ${ and its }
        elif ch == "}" and param:
            param -= 1; closes_param = True
        elif ch in "{}" and not ((i == 0 or text[i - 1] in WORD_EDGE) and (i + 1 == len(text) or text[i + 1] in WORD_EDGE)):
            cur.append(ch); i += 1; continue            # inside a word: -I{}, {}, {a,b}
        if ch in "&|;\n(){}":
            if ch == "(":
                parens.append(("arith" if in_arith else "group", False))
                nxt = not in_arith
            elif ch == ")":                             # what follows a ) is a tail or an operand, not a command,
                pending = parens.pop()[1] if parens else False   # unless an assignment or a redirection held the $(
                nxt = pending and (i + 1 == len(text) or text[i + 1] in " \t")   # and a new word follows it
            elif opens_param or closes_param or ch == "}":
                nxt = False                             # a parameter's text, or the tail after its } or a group's }
            else:
                nxt = not in_arith and not param
            cut(nxt, next_word_pos=ch != ")")
            i += 2 if text.startswith("&&", i) or text.startswith("||", i) else 1
            continue
        cur.append(ch); i += 1
    cut(False)
    put_back()                                          # a pattern list the text ends in was not one
    return [(s.strip(), st, js) for s, st, js in segs if s.strip()]


REDIRECT = re.compile(r"^\d*(>>|>&|<&|&>|>|<)(.*)$")
REDIRECT_AS_WRITTEN = re.compile(REDIRECT.pattern, re.S)   # a word as written: its quoted target may span lines (N7)


def words_as_written(seg):
    """seg's words with their quotes kept, split as shlex.split splits them: at whitespace outside quotes."""
    words, cur, q, i = [], [], None, 0
    while i < len(seg):
        ch = seg[i]
        if q:
            if ch == "\\" and q == '"' and i + 1 < len(seg):
                cur.append(seg[i:i + 2]); i += 2; continue
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in ("'", '"'):
            q = ch; cur.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < len(seg):
            cur.append(seg[i:i + 2]); i += 2; continue
        if ch in " \t\r\n":
            if cur:
                words.append("".join(cur)); cur = []
            i += 1
            continue
        cur.append(ch); i += 1
    if cur:
        words.append("".join(cur))
    return words


def decode(word):
    """One written word lexed alone -> its shlex word, or None when it is not exactly one word."""
    try:
        r = shlex.split(word)
    except ValueError:
        return None
    return r[0] if len(r) == 1 else None


def aligned_words(line):
    """-> (decoded words, written words, aligned) (D5). Aligned: shlex succeeds, both lists have the same length,
    and each written word, lexed alone, gives its decoded word. When not, both lists are line.split()."""
    try:
        raw, written = shlex.split(line), words_as_written(line)
        if len(raw) == len(written) and all(decode(w) == r for w, r in zip(written, raw)):
            return raw, written, True
    except ValueError:
        pass
    raw = line.split()
    return raw, raw, False


def tokens(seg):
    """-> (shlex words, the same words as written, aligned) without redirections, dropped from both lists alike: a
    word is one only when its operator is unquoted as written, so a quoted bash -c operand starting with < stays a
    word."""
    return kept_tokens(seg)[:3]


def kept_tokens(seg):
    """tokens(), plus each kept word's index among the segment's words before redirections were dropped."""
    raw, written, aligned = aligned_words(seg)
    out, wout, kept, skip = [], [], [], False
    for k, t in enumerate(raw):                         # drop redirections and their targets
        if skip:
            skip = False; continue
        m = REDIRECT_AS_WRITTEN.match(written[k]) if aligned else REDIRECT.match(t)
        if m:
            skip = m.group(2) == ""                     # "> file": the target is the next token
            continue
        out.append(t); wout.append(written[k]); kept.append(k)
    return out, wout, aligned, kept


# U8 (gh-ticket#44): a command word git-policy cannot read. QPATH is the one spelling with an expansion that is read:
# a plain variable in double quotes, then literal path parts ("$W"/gh-ticket, "${W}"/bin/x, "$W/x/gh").
LIT = r"[A-Za-z0-9._+@%:,=-]+"
NAME = r"(?:[A-Za-z_][A-Za-z0-9_]*|\{[A-Za-z_][A-Za-z0-9_]*\})"
QPATH = re.compile(rf'"\${NAME}"(?:/{LIT})+|"\${NAME}(?:/{LIT})+"')
GLOB = re.compile(r"[*?\[]|\{[^{}]*(?:,|\.\.)[^{}]*\}")      # a glob character or a brace list {a,b} {a..b}
HEAD_U8 = ('the command word {} is spelled through expansion, substitution, a glob or quoting git-policy cannot read: '
           'write the command name literally; a path may start with "$VAR"/ (the variable in double quotes) or ~/, '
           'or assign the variable a literal path once, earlier in the same command')
GIT_SUB_U8 = "{} stands where git's subcommand is, and git-policy cannot read it (U1 to U4, P1 to P3): write it literally"


def unquoted(written):
    """The characters of a written word outside quotes, with $'...' and backslash escapes removed."""
    out, i, q = [], 0, None
    while i < len(written):
        c = written[i]
        if q:
            if c == "\\" and q == '"':
                i += 2; continue
            if c == q:
                q = None
            i += 1
            continue
        if c == "\\":
            i += 2; continue
        if c == "$" and written[i + 1:i + 2] == "'":
            q = "'"; i += 2; continue
        if c in "'\"":
            q = c; i += 1; continue
        out.append(c); i += 1
    return "".join(out)


def unreadable(word, written, aligned):
    """D4: a word git-policy cannot read as the shell will run it. Not aligned (D5): it holds $, a backquote, a quote,
    a backslash, a glob character or a brace list. Aligned: its decoded form holds $ or a backquote and it is not
    QPATH as written; or outside quotes it holds a glob character (the words [ and [[ aside) or a brace list; or it
    is zsh's =cmd."""
    if not aligned:
        return bool(re.search(r"[$`'\"\\*?\[]", word) or GLOB.search(word))
    if ("$" in word or "`" in word) and not QPATH.fullmatch(written):
        return True
    if word not in ("[", "[[") and GLOB.search(unquoted(written)):
        return True
    return bool(re.match(r"=[A-Za-z_./~]", word))


def substitution_head(seg):
    """U8 at an unquoted $( where split_segments cuts, in a segment that starts a command (gh-ticket#44): the cut
    leaves the words after the substitution as the apparent command, so the word the substitution builds is checked
    here, before the cut loses it. seg: the segment's text so far. Refused: the $( starts or continues the head word
    (nothing but reserved words, VAR= prefixes and wrappers before it), or a literal git head's subcommand word. Not
    refused: an assignment's value (X=$(...)), a redirection's target, or any later word; split_segments skips an
    operand of $(( )) and the text inside ${ }. -> True when the $( is an assignment's value or a redirection's
    target before the command word, which is then still to come after its )."""
    in_word = seg[-1:] not in ("", " ", "\t", "\r", "\n")         # the $( continues the last word written
    written = words_as_written(seg)
    words = tokens(seg)[0]
    if written:
        m = REDIRECT_AS_WRITTEN.match(written[-1])
        if m and (in_word or m.group(2) == ""):
            return not unwrap(words)
    if in_word and words and re.fullmatch(VAR, words[-1]):
        return not unwrap(words)
    cmds = unwrap(words)
    if cmds and cmds[0][0] != "cmd":
        return
    toks = cmds[0][1] if cmds else []
    shown = (written[-1] if in_word and written else "") + "$(...)"
    if not toks or in_word and len(toks) == 1:
        raise Deny("U8", HEAD_U8.format(shown[:60]))
    if os.path.basename(toks[0]).lower() == "git":                 # D11, git's half
        sub = parse_git(toks[:-1] + [toks[-1] + "$()"] if in_word else toks + ["$()"], "/")[1]
        if "$()" in sub:
            raise Deny("U8", GIT_SUB_U8.format(shown[:60]))
    return False


# gh-ticket#91: each wrapper's options that take the next word as their value, short letters and long names. env's
# -S and --split-string stay out: their value is a command line (N3b), read where it stands.
WRAPPER_VALUES = {
    "env": ("uC", ("--unset", "--chdir")),
    "sudo": ("ugCDprtUTR", ("--user", "--group", "--close-from", "--chdir", "--prompt", "--role", "--type",
                            "--other-user", "--command-timeout", "--chroot", "--host")),
    "time": ("of", ("--output", "--format")),
    "exec": ("a", ()),
    "caffeinate": ("tw", ()),
}


def takes_value(head, word):
    """True when the wrapper option word takes the next word as its value: a long name without =, or a short
    cluster whose last letter takes a value (sudo -nu USER); a value attached to the word (-uUSER) consumes none."""
    letters, longs = WRAPPER_VALUES.get(head, ("", ()))
    if word.startswith("--"):
        return word in longs
    for i, c in enumerate(word[1:], 1):
        if c in letters:
            return i == len(word) - 1
    return False


def unwrap(toks):
    """Drop reserved words (N1), VAR=x prefixes and wrappers -> [("cmd", toks, structured)], structured when a
    reserved word or a wrapper was dropped (a cd there adds a candidate: env cd runs no builtin); a
    `bash -c "..."` -> [("script", its text, None)]."""
    structured = False
    while toks:
        head = os.path.basename(toks[0])
        if toks[0] in RESERVED:
            toks, structured = toks[1:], True
        elif re.fullmatch(VAR, toks[0]):
            toks = toks[1:]
        elif head in ("env", "command", "time", "nohup", "sudo", "exec", "builtin", "caffeinate"):
            toks, structured = toks[1:], True              # a word holding whitespace, or env's -S, is a command line (N3b)
            while toks and (toks[0].startswith("-") and not re.search(r"\s", toks[0]) and not split_at(toks, 0)
                            or re.fullmatch(VAR, toks[0])):
                toks = toks[2:] if takes_value(head, toks[0]) else toks[1:]
        elif head in SHELLS and len(toks) >= 3 and toks[1] in ("-c", "-lc", "-ec", "-euc", "-exc"):
            return [("script", toks[2], None)]
        else:
            break
    return [("cmd", toks, structured)] if toks else []


def here_strings(seg):
    """A here-string fed to a shell (bash <<<'...', or a heredoc strip_heredocs turned into one) -> its script (N7)."""
    try:
        raw = shlex.split(seg)
    except ValueError:
        raw = seg.split()
    shell = next((w for w in raw if os.path.basename(w).lower() in SHELLS), None)
    if shell is None:
        return
    for i, w in enumerate(raw):
        if w == "<<<" and i + 1 < len(raw):
            yield ("script", raw[i + 1], shell)
        elif w.startswith("<<<") and len(w) > 3:
            yield ("script", w[3:], shell)


def commands(parts):
    """Yield (index, "cmd", tokens, (structured, written, aligned, starts, joined)) for every simple command in
    split_segments' parts, in order, wrappers unwrapped (index: the segment's; written: the same words as written;
    starts: split_segments' flag; joined: the head word was joined across a backslash-newline), and (index, "script",
    text, word) for a script a shell runs: a bash -c operand (word None) or a here-string to a shell."""
    for n, (seg, starts, joins) in enumerate(parts):
        toks, written, aligned, kept = kept_tokens(seg)
        for kind, payload, extra in unwrap(toks):         # unwrap drops a prefix only: written keeps the same tail
            k = len(written) - len(payload)
            yield (n, kind, payload, (extra, written[k:], aligned, starts, kept[k] in joins)) if kind == "cmd" \
                else (n, kind, payload, extra)
        for item in here_strings(seg):
            yield (n,) + item


# ---------------------------------------------------------------- R5: a variable head assigned a literal (gh-ticket#49)
# docs/plans/u8-variable-heads.md, revision 2. A variable command head ($S/tool, $PY, "$PY") is read as its value when
# the same text level assigns the name exactly once, unconditionally, to a literal, before any compound command. The
# resolution replaces only the head's U8 decision: the command is checked as written with the head's U8 off, then with
# the resolved head, and either refusal refuses (F5). Where the parser cannot be sure, nothing resolves and U8 stands.

PLAIN = r"[A-Za-z_][A-Za-z0-9_]*"
LITC = r"[A-Za-z0-9_./+@%:,=-]"
VAR_HEAD = re.compile(rf'(?P<q>"?)\$(?:(?P<n1>{PLAIN})|\{{(?P<n2>{PLAIN})\}})(?P<t1>(?:/{LIT})*)(?P=q)'
                      rf'(?P<t2>(?:/{LIT})*)')        # $N, "$N" or "${N}", then literal parts inside or after the quotes
LITERAL = re.compile(rf"({LITC}+)|\"({LITC}+)\"|'({LITC}+)'|(~/{LITC}*)")   # condition 8: one field, no glob
# condition 1 (F4): names the shell sets, ties to another name, or writes as a builtin's implicit destination
SHELL_NAMES = {
    "IFS", "PATH", "HOME", "PWD", "OLDPWD", "RANDOM", "SRANDOM", "SECONDS", "LINENO", "EPOCHSECONDS", "EPOCHREALTIME",
    "BASHPID", "PPID", "UID", "EUID", "SHLVL", "REPLY", "OPTARG", "OPTIND", "PS4", "CDPATH", "ENV", "BASH_ENV", "ZDOTDIR",
    "_",
    # implicit destinations: mapfile and readarray (MAPFILE), read, select, sysread, getln (REPLY), zselect (reply),
    # getopts (OPTARG OPTIND OPTERR), coproc with no name (COPROC, COPROC_PID), =~ and pcre_match (MATCH match ...)
    "MAPFILE", "COPROC", "reply", "OPTERR", "MATCH", "MBEGIN", "MEND", "match", "mbegin", "mend",
    # bash's other managed names
    "GROUPS", "FUNCNAME", "DIRSTACK", "PIPESTATUS", "HISTCMD", "COLUMNS", "LINES", "HOSTNAME", "HOSTTYPE", "MACHTYPE",
    "OSTYPE", "TMOUT", "MAILPATH", "MAIL", "SHELLOPTS", "GLOBIGNORE", "FIGNORE", "PS1", "PS2", "PS3",
    # zsh's managed and tied names (path is PATH, cdpath is CDPATH, and so on: assigning one writes the other)
    "ARGC", "argv", "status", "pipestatus", "path", "cdpath", "fpath", "FPATH", "manpath", "MANPATH", "mailpath",
    "module_path", "MODULE_PATH", "fignore", "psvar", "PSVAR", "watch", "WATCH", "zsh_eval_context", "ERRNO",
    "TTYIDLE", "TRY_BLOCK_ERROR", "TRY_BLOCK_INTERRUPT", "signals", "options", "parameters", "commands", "functions",
    "aliases", "builtins", "galiases", "saliases", "history", "historywords", "jobdirs", "jobstates", "jobtexts",
    "modules", "nameddirs", "reswords", "termcap", "terminfo", "userdirs", "widgets", "funcstack", "funcfiletrace",
    "funcsourcetrace", "functrace", "keymaps", "patchars", "sysparams", "errnos", "dis_aliases", "dis_builtins",
    "dis_functions", "dis_galiases", "dis_saliases", "dis_reswords", "dis_patchars", "CPUTYPE", "VENDOR", "LOGNAME",
    "USERNAME", "HOST", "TTY", "PROMPT", "PROMPT2", "PROMPT3", "PROMPT4", "RPROMPT", "RPS1", "TMPPREFIX"}
SHELL_PREFIXES = ("BASH", "ZSH", "COMP", "COPROC", "LC_")
# condition 5: a segment that starts with one of these (after any of COMPOUND_PASS), up to and including B, stops it
COMPOUND = {"if", "then", "else", "elif", "fi", "case", "esac", "for", "select", "while", "until", "do", "done",
            "function", "coproc", "repeat", "foreach", "end", "always"}
COMPOUND_PASS = {"!", "time", "nocorrect", "noglob"}
# condition 9: heads that may write a name the text does not spell (always, or with a computed word)
DYN_ALWAYS = {"source", ".", "autoload", "zmodload", "enable", "fc", "noglob", "nocorrect", "-", "emulate", "sched",
              "builtin", "command", "exec"}
DYN_CODE = {"eval", "trap", "alias"}
DYN_DECL = {"declare", "typeset", "local", "export", "readonly", "integer", "float", "private"}
DYN_NAMED = {"read", "mapfile", "readarray", "getopts", "unset", "vared", "zparseopts", "zstyle", "zformat",
             "zregexparse", "strftime", "zstat", "sysread", "zselect", "pcre_match", "getln", "compadd", "coproc",
             "select", "wait", "let"}
COMMENT = re.compile(r"(?<![^\s;&|()<>])#")            # a # at the text's start or after a blank or an operator
GIT_WORD = re.compile(r"(?<![A-Za-z0-9_.+-])(?:git|gh)(?![A-Za-z0-9_.+-])", re.I)
# Option (3), owner-dated (Q1, Q9): an unresolved plain-name head read as an unknown command with its literal tail
# kept, the gh shim covering it at run time, unless a git or gh word follows it (F8). None is off. The owner sets it to
# the date he verified eturea/workbench#85's shim on PATH, by a commit; the hook cannot see the shim.
VARIABLE_HEADS_SHIM = None
LEVELS = []                                            # the text levels being evaluated, innermost last; None: env's
                                                       # split string, which has no bindings
# The plain-text gate (Codex C1 to C5 on cfd99a9): R5 resolves only when the whole command text is plain. Fail closed:
# quotes are not read, and a word is matched with its quotes and backslashes removed.
NOT_PLAIN = re.compile(r"<<|\\\n|\$'|[`(){}]")         # a heredoc or here-string, a continuation, an ANSI-C quote, a
                                                       # backquote, a subshell, a group, $( ) or ${ }
WRITER_WORD = re.compile(r"(?<![A-Za-z0-9_])(?:eval|source|trap|alias)(?![A-Za-z0-9_])")
DOT_WORD = re.compile(r"(?:^|[;&|\n])[ \t]*\.(?![^ \t\n;&|])")             # . as a command word
SHELL_WORD = re.compile(r"(?<![A-Za-z0-9_.-])(?:bash|sh|zsh|dash)(?![A-Za-z0-9_.-])", re.I)
C_OPTION = re.compile(r"(?<!\S)-[A-Za-z]*c")                               # with a shell word: a -c script argument
SPLIT_OPTION = re.compile(r"(?<!\S)(?:-S|--split-string)")                 # env's split string
QUOTED_ASSIGN = re.compile(r"(?<![^\s;&|])[A-Za-z_][A-Za-z0-9_]*\+?=[^\s;&|]*['\"]")
NO_RESOLVE = {"cd", "pushd", "popd"}                   # a head resolving to one of these stays U8 (C3)


def plain(text):
    """The plain-text gate: no eval, source, ., trap or alias; no -c script argument to a shell and no env -S; no
    heredoc or here-string, continuation, $' or comment; no quote in an assignment word; and the only separators are
    ;, &&, || and a newline (a redirection's & is no separator)."""
    bare = re.sub(r"[\\'\"]", "", text)
    seps = re.sub(r"&&|\|\||[<>]&|&>", "", text)
    return not (NOT_PLAIN.search(text) or COMMENT.search(text) or QUOTED_ASSIGN.search(text) or re.search(r"[|&]", seps)
                or WRITER_WORD.search(bare) or DOT_WORD.search(bare) or SPLIT_OPTION.search(bare)
                or SHELL_WORD.search(bare) and C_OPTION.search(bare))


def level_gate(stripped):
    """The level gates (F2, F3): a comment the parser does not read, a backquote, a process substitution or an ANSI-C
    quote in the text the parser splits (heredoc bodies removed). Quotes are not read: a quoted # stops it too."""
    return bool(COMMENT.search(stripped)) or "`" in stripped or any(x in stripped for x in ("<(", ">(", "$'"))


def segment_marks(text):
    """split_segments' cuts (#48 changes only its starts flags), with each cut's separator and the nesting depth at
    each segment's start -> [(text, depth, separator)], END after the last."""
    segs, cur, i, q, param, brace, parens, depth = [], [], 0, None, 0, 0, [], 0

    def cut(sep):
        nonlocal cur, depth
        segs.append(("".join(cur), depth, sep)); cur = []
        depth = len(parens) + param + brace
    while i < len(text):
        ch = text[i]
        if q:
            if ch == "\\" and q == '"' and i + 1 < len(text):
                if text[i + 1] != "\n":
                    cur.append(text[i:i + 2])
                i += 2; continue
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in ("'", '"'):
            q = ch; cur.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < len(text):
            if text[i + 1] != "\n":
                cur.append(text[i:i + 2])
            i += 2; continue
        in_arith = bool(parens) and parens[-1] == "arith"
        if text.startswith("$(", i):
            arith = text.startswith("$((", i)
            parens.append("arith" if arith else "sub")
            cut("$((" if arith else "$("); i += 2; continue
        if ch == "&" and ((cur and cur[-1] in (">", "<")) or text.startswith("&>", i)):
            cur.append(ch); i += 1; continue
        opens_param = closes_param = False
        if ch == "{" and i > 0 and text[i - 1] == "$":
            param += 1; opens_param = True
        elif ch == "}" and param:
            param -= 1; closes_param = True
        elif ch in "{}" and not ((i == 0 or text[i - 1] in WORD_EDGE) and (i + 1 == len(text) or text[i + 1] in WORD_EDGE)):
            cur.append(ch); i += 1; continue
        if ch in "&|;\n(){}":
            if ch == "(":
                parens.append("arith" if in_arith else "group")
            elif ch == ")":
                if parens:
                    parens.pop()
            elif ch == "{" and not opens_param:
                brace += 1
            elif ch == "}" and not closes_param:
                brace = max(0, brace - 1)
            two = text.startswith("&&", i) or text.startswith("||", i)
            cut(text[i:i + 2] if two else ("${" if opens_param else "}p" if closes_param else ch))
            i += 2 if two else 1
            continue
        cur.append(ch); i += 1
    cut("END")
    return segs


def count_mentions(t, n):
    """-> (assignments n=, other mentions) of the whole name n in t; the reads $n and ${n} are left out."""
    a = o = 0
    for m in re.finditer(rf"(?<![A-Za-z0-9_]){re.escape(n)}(?![A-Za-z0-9_])", t):
        i, j = m.start(), m.end()
        if t[i - 1:i] == "$" and t[i - 2:i] != "$$":
            continue
        if t[i - 2:i] == "${" and t[j:j + 1] == "}":
            continue
        if t[j:j + 1] == "=" and t[j:j + 2] != "==":
            a += 1
        else:
            o += 1
    return a, o


def assignments(seg):
    """{name: [values as written]} when every word of the aligned segment is NAME=VALUE and it has no redirection,
    else {} (condition 3: one bare assignment statement; a prefix assignment is not one)."""
    words, written, aligned, kept = kept_tokens(seg)
    if not aligned or not written or len(kept) != len(aligned_words(seg)[0]):
        return {}
    out = {}
    for w, wr in zip(words, written):
        m = re.fullmatch(rf"({PLAIN})=(.*)", wr, re.S)
        if not (m and re.fullmatch(VAR, w, re.S)):
            return {}
        out.setdefault(m.group(1), []).append(m.group(2))
    return out


class Seg:
    __slots__ = ("text", "starts", "depth", "before", "after", "assigns", "compound")


class Level:
    """One text level: the top text, a shell's -c operand, or a here-string to a shell. Its bindings never cross
    levels. parts: split_segments' (a $( ) head's U8 is raised here, before any command is checked, as before)."""

    def __init__(self, text):
        self.text, self.stripped = text, strip_heredocs(text)
        self.parts = split_segments(self.stripped)
        self.cur, self._segs, self._dyn, self._ment = None, False, None, {}
        self.plain = not LEVELS and plain(text)        # the gate reads the whole text: the top level's

    def segs(self):
        """The segments with their separators and depth, read on the first resolution; None when the level does not
        resolve (a gate, or the parallel scan disagrees with split_segments' segment texts)."""
        if self._segs is False:
            self._segs = None if level_gate(self.stripped) else self._read()
        return self._segs

    def _read(self):
        raw = segment_marks(self.stripped)
        if [s.strip() for s, _, _ in raw if s.strip()] != [s for s, _, _ in self.parts]:
            return None
        segs, before = [], []
        for s, depth, sep in raw:
            if s.strip():
                g = Seg()
                g.text, g.starts, _ = self.parts[len(segs)]
                g.depth, g.before, g.after = depth, before, []
                if segs:
                    segs[-1].after = before
                lead = []
                for w in words_as_written(g.text):
                    if w not in COMPOUND and w not in COMPOUND_PASS:
                        break
                    lead.append(w)
                g.compound = any(w in COMPOUND for w in lead) or any(x in ("(", "{", "}") for x in before)
                g.assigns = assignments(g.text)
                segs.append(g)
                before = []
            before.append(sep)
        if segs:
            segs[-1].after = before
        return segs

    def mentions(self, n):
        """Condition 2 (F1): counted in two readings of the raw text (quoted text and heredoc bodies included): as
        written, and with every backslash-newline removed. Within a run of name characters the shell joins every
        continuation or none, so each mention the shell sees is in one reading or the other."""
        if n not in self._ment:
            self._ment[n] = [count_mentions(self.text, n), count_mentions(self.text.replace("\\\n", ""), n),
                             count_mentions(re.sub(r"[\\'\"]", "", self.text), n)]   # C1: C''MD is CMD
        return self._ment[n]

    def resolve(self, n, use, dyn=True):
        """-> the literal value of name n for a head in segment index use, or None."""
        if not (LEVELS and LEVELS[0] is not None and LEVELS[0].plain):   # the plain-text gate
            return None
        segs = self.segs()
        if segs is None or n in SHELL_NAMES or n.startswith(SHELL_PREFIXES):
            return None
        if any(a != 1 or o for a, o in self.mentions(n)):
            return None
        hits = [k for k, g in enumerate(segs) if n in g.assigns]
        if len(hits) != 1:
            return None
        b = hits[0]
        g = segs[b]
        if len(g.assigns[n]) != 1 or b >= use:          # condition 3 once; condition 4 before the use
            return None
        if any(x.compound for x in segs[:b + 1]) or g.depth:              # conditions 5 and 6
            return None
        if not g.starts or not set(g.after) <= {";", "\n", "&&", "END"} or not set(g.before) <= {";", "\n"}:
            return None                                 # condition 7
        m = LITERAL.fullmatch(g.assigns[n][0])
        if not m or dyn and self.dynamic():             # conditions 8 and 9
            return None
        return next(x for x in m.groups() if x is not None)

    def dynamic(self):
        """Condition 9: something at this level may assign a name the text does not spell."""
        if self._dyn is None:
            self._dyn = self._dynamic()
        return self._dyn

    def _dynamic(self):
        t = self.text
        if "${(" in t or "${!" in t or re.search(r"(?<![A-Za-z0-9_])IFS(?![A-Za-z0-9_])", t):
            return True
        for k, g in enumerate(self._segs):
            toks, written, aligned = tokens(g.text)
            for kind, payload, _ in unwrap(toks):
                if kind != "cmd" or not payload:
                    continue
                w = written[len(written) - len(payload):]
                head = os.path.basename(payload[0])
                m = VAR_HEAD.fullmatch(w[0]) if aligned else None
                if m:
                    v = self.resolve(m.group("n1") or m.group("n2"), k, dyn=False)
                    if v is not None:
                        head = os.path.basename(v + (m.group("t1") or "") + (m.group("t2") or ""))
                if head in DYN_ALWAYS:
                    return True
                rest, wrest = payload[1:], w[1:]

                def computed(x):
                    return "$" in x or "`" in x or not aligned
                if head in DYN_CODE and any(computed(x) for x in rest):
                    return True
                if head in DYN_NAMED and any(computed(x) or re.search(r"[*?\[{]", x) for x in rest):
                    return True
                if head in DYN_DECL:
                    for x, wx in zip(rest, wrest):
                        if x.startswith(("-", "+")):
                            if "n" in x[1:]:
                                return True
                            continue
                        if not aligned or not re.fullmatch(rf"{PLAIN}(?:\[[^\]]*\])?(?:\+?=.*)?", wx, re.S):
                            return True
                if head in ("printf", "print"):
                    for x in rest:
                        if x == "--":
                            break
                        if x.startswith("-"):
                            if "v" in x[1:]:
                                return True
                            continue
                        if computed(x):
                            return True
                        break
        return False


def git_follows(level):
    """(3)'s guard (F8, Q9): a git or gh word after the unresolved head, in the later segments of the top text, or
    anywhere in the top text when the head sits at another level (its cd would reach the caller's folders)."""
    top = LEVELS[0] if LEVELS else None
    if top is None:
        return True
    if level is top and level.cur is not None:
        rest = "\n".join(s for s, _, _ in top.parts[level.cur + 1:])
    else:
        rest = top.text
    return GIT_WORD.search(rest) is not None


# ---------------------------------------------------------------- repository state

class Repo:
    def __init__(self, base_cmd):
        self.base = base_cmd                       # ["git", "-C", dir, ...] locating the repo
        self.top = self._git("rev-parse", "--show-toplevel")
        self.ok = self.top is not None
        if self.ok:
            self.common = self._git("rev-parse", "--git-common-dir") or ""
            if not os.path.isabs(self.common):
                self.common = os.path.join(self.top, self.common)
            self.branch = self._git("symbolic-ref", "--short", "HEAD") or ""
            self.origin = self._git("config", "--get", "remote.origin.url") or ""

    def _git(self, *args):
        r = subprocess.run([*self.base, *args], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    def git(self, *args):
        return self._git(*args)

    def name(self):
        m = re.search(r"[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", self.origin)
        return (m.group(1), m.group(2)) if m else ("", "")

    def opted_in(self):
        owner, name = self.name()
        if owner.lower() == OWNER and name.lower() in opt_in_names():
            return True
        copy_root = HERE.parent.parent                   # <repo>/.claude/hooks/git-policy.py
        return HERE.name == "hooks" and HERE.parent.name == ".claude" and \
            os.path.realpath(copy_root) == os.path.realpath(self.top)

    def escaped(self):
        return os.path.exists(os.path.join(self.common, "git-policy-off"))

    def ref_exists(self, name):
        return self._git("rev-parse", "--verify", "-q", f"refs/heads/{name}") is not None or \
            self._git("rev-parse", "--verify", "-q", f"refs/remotes/origin/{name}") is not None


def opt_in_names():
    try:
        return {l.strip().lower() for l in (HERE / "opt-in.txt").read_text().splitlines()
                if l.strip() and not l.startswith("#")}
    except OSError:
        return set()


# ---------------------------------------------------------------- git command analysis

def absolute(path, cwd):
    path = os.path.expanduser(path)
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(cwd, path))


def parse_git(toks, cwd):
    """-> (locating base command, subcommand, args, config -c values)."""
    i, base, configs = 1, ["git"], []
    while i < len(toks):
        t = toks[i]
        if t == "-C" and i + 1 < len(toks):
            base += ["-C", absolute(toks[i + 1], cwd)]
            cwd = base[-1]; i += 2
        elif t == "-c" and i + 1 < len(toks):
            configs.append(toks[i + 1]); i += 2
        elif t.startswith("-c") and len(t) > 2 and "=" in t:
            configs.append(t[2:]); i += 1
        elif t == "--config-env" and i + 1 < len(toks):          # --config-env=<key>=<ENVVAR>: the key is set, like -c
            configs.append(toks[i + 1].split("=", 1)[0] + "=env"); i += 2
        elif t.startswith("--config-env="):
            configs.append(t[len("--config-env="):].split("=", 1)[0] + "=env"); i += 1
        elif t.startswith("--git-dir=") or t.startswith("--work-tree="):
            k, v = t.split("=", 1); base.append(k + "=" + absolute(v, cwd)); i += 1
        elif t in ("--git-dir", "--work-tree") and i + 1 < len(toks):
            base += [t + "=" + absolute(toks[i + 1], cwd)]; i += 2
        elif t in GIT_OPTS_WITH_VALUE and i + 1 < len(toks):
            i += 2
        elif t.startswith("-"):
            i += 1
        else:
            break
    if "-C" not in base and "--git-dir" not in " ".join(base) and "--work-tree" not in " ".join(base):
        base += ["-C", cwd]
    sub = toks[i] if i < len(toks) else ""
    return base, sub, toks[i + 1:], configs


def config_value(repo, configs, key, all_values=False):
    """A config value as the command would see it: a -c on the command line wins over the repository."""
    hits = [c.split("=", 1)[1] if "=" in c else "" for c in configs if c.split("=", 1)[0].lower() == key.lower()]
    if hits:
        return hits if all_values else hits[-1]
    v = repo.git("config", "--get-all" if all_values else "--get", key)
    if v is None:
        return [] if all_values else None
    return v.split("\n") if all_values else v


def effective_refspecs(repo, remote, refspecs, configs):
    """What a push sends, as refspecs, resolved from the command and the config with certainty."""
    if refspecs:
        return list(refspecs)
    configured = config_value(repo, configs, f"remote.{remote}.push", all_values=True)
    if configured:
        return [c for c in configured if c]
    default = (config_value(repo, configs, "push.default") or "simple").lower()
    if not repo.branch:
        raise Deny("U3", "a bare push on a detached HEAD: name the refspec")
    merge = repo.git("config", "--get", f"branch.{repo.branch}.merge")
    up_remote = repo.git("config", "--get", f"branch.{repo.branch}.remote")
    upstream = re.sub(r"^refs/heads/", "", merge) if merge else None
    if default == "current":
        return [f"{repo.branch}:{repo.branch}"]
    if default == "simple":
        if upstream and up_remote == remote and upstream != repo.branch:
            raise Deny("U3", f"push.default=simple with upstream {upstream}: git refuses this push; name the refspec")
        return [f"{repo.branch}:{repo.branch}"]
    if default == "upstream":
        if upstream and up_remote == remote:
            return [f"{repo.branch}:{upstream}"]
        raise Deny("U3", "push.default=upstream with no upstream on this remote: name the refspec")
    raise Deny("U3", f"push.default={default} sends an unpredictable set: name the refspec")


def push_sources(repo, remote, refspecs, tags):
    """The local sources a push would send: a list of rev names, or raise Deny when unresolvable."""
    sources = []
    for r in refspecs:
        r = r.lstrip("+")
        if "*" in r:
            raise Deny("U3", f"refspec {r!r} has a glob: name the refspec")
        src = r.split(":", 1)[0] if ":" in r else r
        if src == "":
            continue                                   # a deletion (U4 handles it)
        sources.append(src)
    if tags:
        sources.append("--tags")
    return sources


def push_positional(args):
    """-> (positional words, the --repo value): the remote and the refspecs as written."""
    positional, repo_opt, i = [], None, 0
    while i < len(args):
        a = args[i]
        if a in PUSH_OPTS_WITH_VALUE:
            if a == "--repo" and i + 1 < len(args):
                repo_opt = args[i + 1]
            i += 2; continue
        if a.startswith("--repo="):
            repo_opt = a.split("=", 1)[1]
        if a.startswith("-"):
            i += 1; continue
        positional.append(a); i += 1
    return positional, repo_opt


def check_push_text(args, configs):
    """U1 to U4 on the push's own words: no repository state, so they hold when none resolves (gh-ticket#62)."""
    force = any(a in ("-f", "--force", "--force-if-includes") or a.startswith("--force-with-lease") for a in args)
    if force or any(not a.startswith("-") and a.startswith("+") for a in args):
        raise Deny("U1", "force push is never allowed")
    if "--all" in args or "--mirror" in args or any("local-history" in a for a in args):
        raise Deny("U2", "local-history is never pushed, and --all or --mirror would carry it")
    no_verify = any(a.startswith("--no-ver") and "--no-verify".startswith(a) for a in args)   # git takes --no-veri, --no-verif too
    if no_verify or any(c.lower().startswith("core.hookspath") for c in configs):
        raise Deny("U3", "a push must run the pre-push hook: no --no-verify, no core.hooksPath override")
    if "--delete" in args or "-d" in args:
        raise Deny("U4", "deleting a remote branch needs the owner's yes; he runs it")
    if any(r.startswith(":") for r in push_positional(args)[0][1:]):
        raise Deny("U4", "a :branch refspec deletes the remote branch; the owner runs deletions")


def check_push(repo, args, configs, opted):
    tags = "--tags" in args or "--follow-tags" in args
    positional, repo_opt = push_positional(args)
    remote = positional[0] if positional else repo_opt or "origin"   # git: a positional remote wins over --repo
    if opted and not positional[1:]:
        raise Deny("P2", "a push in this repository names what it sends: git push -u origin <branch> (name the refspec; "
                         "the config's remote.<r>.push, push.default, pushRemote and pushDefault are not consulted)")
    refspecs = effective_refspecs(repo, remote, positional[1:], configs)
    if any(r.startswith(":") for r in refspecs):
        raise Deny("U4", "a :branch refspec deletes the remote branch; the owner runs deletions")
    sources = push_sources(repo, remote, refspecs, tags)
    for src in sources:
        short = re.sub(r"^refs/heads/", "", src)
        name = repo.branch if short == "HEAD" else short
        if name.startswith("wip/"):
            raise Deny("U3", f"{name} is a wip/* branch and is never pushed")
        if src == "--tags":
            rev = ["--tags"]
        else:
            if repo.git("rev-parse", "--verify", "-q", src) is None:
                raise Deny("U3", f"cannot resolve push source {src!r}: name the refspec")
            rev = [src]
        outgoing = (repo.git("rev-list", *rev, "--not", f"--remotes={remote}") or "").split()
        for sha in outgoing:
            msg = repo.git("log", "-1", "--format=%B", sha) or ""
            m = MARKERS.search(msg)
            if m:
                raise Deny("U3", f"commit {sha[:8]} is marked \"{m.group(0)}\" and is never pushed")
    return remote, refspecs, sources


def push_targets(repo, refspecs, sources):
    out = []
    for r in refspecs:
        r = r.lstrip("+")
        dst = r.split(":", 1)[1] if ":" in r else r
        dst = re.sub(r"^refs/heads/", "", dst)
        out.append(repo.branch if dst == "HEAD" else dst)
    return out


VALUE_FLAGS = {"push": "o", "branch": "ut", "checkout": "bB", "switch": "cC", "worktree": "bB"}


def split_short_flags(sub, args):
    """-uf -> -u -f (and -Df, -bq ...), a flag that takes a value last, so the value still follows it."""
    out = []
    for a in args:
        if re.fullmatch(r"-[A-Za-z]{2,}", a):
            letters, value_flags, tail = list(a[1:]), VALUE_FLAGS.get(sub, ""), []
            for k, c in enumerate(letters):                   # the first value-taking letter owns the rest: -owaffle is -o waffle
                if c in value_flags:
                    letters, tail = letters[:k], ["-" + c, a[k + 2:]] if a[k + 2:] else ["-" + c]
                    break
            out += ["-" + c for c in letters] + tail
        else:
            out.append(a)
    return out


def new_branch_names(sub, args):
    """Branch names a command would create (P3), or [] when it creates none."""
    names = []
    if sub in ("checkout", "switch"):
        for i, a in enumerate(args):
            if a in ("-b", "-B", "-c", "-C", "--create", "--force-create", "--orphan") and i + 1 < len(args):
                names.append(args[i + 1])
            elif a.startswith(("--orphan=", "--create=", "--force-create=")):
                names.append(a.split("=", 1)[1])
    elif sub == "branch":
        pos, i, skip = [], 0, {"-u", "--set-upstream-to", "-t", "--track", "--contains", "--no-contains",
                              "--merged", "--no-merged", "--points-at", "--format", "--sort", "--color", "--abbrev"}
        flags = set()
        while i < len(args):
            a = args[i]
            if a in skip:
                i += 2; continue
            if a.startswith("-"):
                flags.add(a); i += 1; continue
            pos.append(a); i += 1
        if flags & {"-m", "-M", "-c", "-C", "--move", "--copy"}:
            names = pos[-1:]                            # the new name is the last positional
        elif pos and not flags & {"-d", "-D", "--delete", "-l", "--list", "-a", "-r", "-v", "-vv", "--show-current",
                                   "--edit-description", "--unset-upstream"}:
            names = pos[:1]
    elif sub == "worktree" and args[:1] == ["add"]:
        rest = [a for a in args[1:]]
        if "-b" in rest or "-B" in rest:
            i = rest.index("-b") if "-b" in rest else rest.index("-B")
            if i + 1 < len(rest):
                names.append(rest[i + 1])
        elif "--detach" not in rest:
            pos = [a for a in rest if not a.startswith("-")]
            if len(pos) == 1:                           # add <path>: branch named after the path
                names.append(os.path.basename(pos[0].rstrip("/")))
    elif sub == "stash" and args[:1] == ["branch"] and len(args) > 1:
        names.append(args[1])
    return names


def check_git(toks, cwd):
    base, sub, args, configs = parse_git(toks, cwd)
    if not sub:
        return
    args = split_short_flags(sub, args)
    # U1 to U4 on the command's own words, before the repository is resolved: they fail closed (gh-ticket#62)
    if sub == "branch" and any(a in ("-d", "-D", "--delete") for a in args):
        raise Deny("U4", "deleting a branch needs the owner's yes; he runs it")
    if sub == "branch" and any(a in ("-m", "-M", "--move") for a in args):   # the hook refuses it too (gh-ticket#57)
        raise Deny("U4", "renaming a branch deletes its old name, which is the owner's: copy it with git branch -c OLD NEW "
                         "and name the old one in your report")
    if sub == "update-ref" and any(a in ("-d", "--delete") for a in args):
        raise Deny("U4", "removing a ref needs the owner's yes; he runs it")
    if sub == "worktree" and args[:1] == ["remove"] and any(a in ("--force", "-f") for a in args):
        raise Deny("U4", "git worktree remove --force discards a tree's changes; the owner runs it")
    if sub == "push":
        check_push_text(args, configs)
    repo = Repo(base)
    if not repo.ok:
        return
    on_protected = repo.branch in PROTECTED_BRANCHES
    names_protected = any(a in PROTECTED_BRANCHES for a in args)
    # U4 on repository state
    if sub == "commit" and "--amend" in args and on_protected:
        raise Deny("U4", f"amending on {repo.branch} needs the owner's yes")
    if sub == "rebase" and (on_protected or names_protected):
        raise Deny("U4", f"rebasing {repo.branch} needs the owner's yes")
    if sub == "reset" and "--hard" in args and on_protected:
        raise Deny("U4", f"reset --hard on {repo.branch} needs the owner's yes")
    opted = repo.opted_in() and not repo.escaped()
    push_info = None
    if sub == "push":
        push_info = check_push(repo, args, configs, opted)
    # PR rules
    if not opted:
        return
    on_integration = repo.branch in INTEGRATION
    if on_integration and sub in ("merge", "pull"):               # a fast-forward makes no commit: allowed
        def ff_flag(a):                                            # git takes unique abbreviations: --ff-o, --no-f
            if a == "--ff": return a
            if len(a) >= 5 and "--ff-only".startswith(a): return "--ff-only"
            if len(a) >= 6 and "--no-ff".startswith(a): return "--no-ff"
            return None
        last, skip = [], False                                     # git honours the last one given
        for a in args:
            if a == "--": break                                     # the end of the options: what follows is a ref
            if skip: skip = False; continue
            if merge_opt_takes_value(a): skip = True; continue    # the value is not a flag: -m --ff-only
            f = ff_flag(a)
            if f: last.append(f)
        if last:
            ff_only = last[-1] == "--ff-only"
        else:                                                      # pull.ff=only holds unless --rebase/--no-rebase overrides it
            def rebase_opt(a):                                     # -r, --reb[=mode], --no-reb and longer
                a = a.split("=", 1)[0]
                return a.startswith("-r") and not a.startswith("--") or \
                    (len(a) >= 5 and "--rebase".startswith(a)) or (len(a) >= 8 and "--no-rebase".startswith(a))   # -r, -r0, -rtrue
            mode = any(rebase_opt(a) for a in args)
            ff_only = sub == "pull" and not mode and (config_value(repo, configs, "pull.ff") or "").lower() == "only"
        if not ff_only:
            raise Deny("P1", f"{repo.branch} moves only by PR merge and a fast-forward (git pull --ff-only, "
                             "git merge --ff-only, or pull.ff=only)")
    if sub in ("commit", "rebase", "cherry-pick", "am", "revert") and on_integration:
        raise Deny("P1", f"no commits on {repo.branch}: work on an issue branch from gh ticket start N")
    if push_info:
        remote, refspecs, sources = push_info
        for t in push_targets(repo, refspecs, sources):
            if t in INTEGRATION:
                if t == "develop" and (repo.git("ls-remote", "--heads", remote, "develop") or "") == "":
                    continue                            # creating develop (the migration)
                raise Deny("P2", f"{t} moves only by PR merge: push an issue branch and open a PR with gh ticket pr N")
    for name in new_branch_names(sub, args):
        if repo.ref_exists(name):
            continue
        if not BRANCH_OK.match(name):
            raise Deny("P3", f"branch {name!r} is not an issue branch: use gh ticket start N "
                             "(or probe/, spike/, wip/ for work with no issue)")


def gh_words(args):
    """gh's words without -R/--repo and its value."""
    words, i = [], 0
    while i < len(args):
        if args[i] in ("-R", "--repo"):
            i += 2; continue
        if not (args[i].startswith("--repo=") or (args[i].startswith("-R") and len(args[i]) > 2)):   # -Rx, -R=x
            words.append(args[i])
        i += 1
    return words


def no_codex(w):
    """--no-codex, or a prefix of it at least 3 long: argparse takes a unique prefix (--n, --no, --no-c)."""
    return len(w) >= 3 and "--no-codex".startswith(w)


# U6's one exception (gh-ticket#30): four help lines, each the whole command text. HELP_TEXT reads the raw text,
# HELP_ARGV the head command's argv; both must agree, so no wrapper, prefix, quote, expansion, redirection or second
# command fits. gh help pr X is not one: a gh alias named help can shadow the built-in help (no alias shadows pr).
HELP_TEXT = re.compile(r"[ \t]*gh[ \t]+pr[ \t]+(?:merge|create)[ \t]+(?:--help|-h)[ \t]*")
HELP_ARGV = {("pr", "merge", "--help"), ("pr", "merge", "-h"), ("pr", "create", "--help"), ("pr", "create", "-h")}


def check_gh(toks, help_ok=False):
    args = toks[1:]
    words = gh_words(args)
    if words[:2] == ["ticket", "merge"] and any(no_codex(w) for w in words):
        raise Deny("U5", "gh ticket merge --no-codex is the owner's, from his own terminal: fix or answer the Codex findings "
                         "and rereview instead")
    if help_ok and toks[0] == "gh" and tuple(args) in HELP_ARGV:
        return                                                     # help_ok: the whole text is one help line, at the head
    if "pr" in args and {"create", "merge"} & set(args[args.index("pr") + 1:]):
        raise Deny("U6", "open and merge PRs with gh ticket pr N and gh ticket merge N, never gh pr create or gh pr merge "
                         "(every repository; gh ticket pushes, sets the base and the body, and merges in the right style)")


# ---------------------------------------------------------------- main

FED_XARGS = ("behind xargs", "stdin")
FED_ARGS = ("inside a script that reads its arguments", "those arguments")


def add(cwds, new):
    for c in new:
        if c not in cwds:
            cwds.append(c)


def feed(fed, source, prefix=()):
    """fed by one more source (FED_XARGS or FED_ARGS) -> (where, from, placeholder candidates). The candidates add
    up: a word after xargs in prefix, or the rest of an option word (-I{} gives {}, --replace=R gives R)."""
    cands = set(fed[2]) if fed else set()
    for w in prefix:
        cands.add(w)
        if w.startswith("-") and len(w) > 2:
            cands.add(w[2:])
        if "=" in w:
            cands.add(w.split("=", 1)[1])
    cands.discard("")
    return (source[0], source[1], frozenset(cands))


def check_fed(suffix, fed):
    """U7: a gh or git suffix whose argv is assembled from input the hook cannot read (fed, from feed()).
    Its deciding words must be visible: present, no $, and no placeholder candidate."""
    cands = fed[2]

    def visible(w):
        return bool(w) and "$" not in w and not any(c in w for c in cands)

    shape = None
    if os.path.basename(suffix[0]).lower() == "gh":
        words = gh_words(suffix[1:]) + [None, None]
        first, second = words[0], words[1]
        rule = "U5" if first == "ticket" else "U6" if first == "pr" else "U5, U6"
        if not visible(first):
            shape, what = "gh", "subcommand"
        elif first in ("pr", "ticket") and not visible(second):
            shape, what = f"gh {first}", "subcommand"
        elif first == "ticket" and second == "merge" or first == "pr" and second in ("create", "merge"):
            shape, what = f"gh {first} {second}", "options"
    else:
        sub, rule = parse_git(suffix, "/")[1], "U1 to U4, P1 to P3"
        if not visible(sub):
            shape, what = "git", "subcommand"
        elif sub in RULED:
            shape, what = f"git {sub}", "options"
    if shape:
        raise Deny("U7", f"{shape} {fed[0]} takes its {what} from {fed[1]}, which git-policy cannot read ({rule}): "
                         f"name the {what} on the command line")


def shell_operand(toks, k):
    """The index of the script operand of the shell word toks[k], read with the shell's own options, when they
    hold -c (N3), else None."""
    j, has_c = k + 1, False
    while j < len(toks):
        w = toks[j]
        if w in ("--", "-"):
            j += 1; break
        if w in ("--rcfile", "--init-file"):
            j += 2; continue
        if w.startswith("--"):
            j += 1; continue
        if w[:1] in ("-", "+"):
            has_c = has_c or (w[0] == "-" and "c" in w[1:])
            j += 1 + w[1:].count("o") + w[1:].count("O")      # -o, -euo pipefail: each o or O takes the next word
            continue
        break
    return j if has_c and j < len(toks) else None


def shell_scripts(toks):
    """{shell index: operand index} for each shell word with a -c operand (N3). Nothing is exempt from N2: a word
    that only looks like a shell (find -name bash) costs a needless operand read, never a hidden command."""
    scripts = {}
    for k, t in enumerate(toks):
        j = shell_operand(toks, k) if os.path.basename(t).lower() in SHELLS else None
        if j is not None:
            scripts[k] = j
    return scripts


def split_at(toks, k):
    """env's split string at toks[k] (-S STR, -SSTR, --split-string STR, --split-string=STR), at any index
    -> (STR, the index of the words after it), else None (N3b)."""
    w = toks[k]
    if w in ("-S", "--split-string"):
        return (toks[k + 1], k + 2) if k + 1 < len(toks) else None
    if w.startswith("--split-string="):
        return w[len("--split-string="):], k + 1
    if w.startswith("-S") and len(w) > 2:
        return w[2:], k + 1
    return None


def split_string(word, line, rest, structured, cwds, fed, wrest=None, aligned=True, starts=True):
    """N3b: env's split string re-lexed with the words after it (env appends them), checked as one command from a
    copy of the candidate cwds (env runs it: its cd never moves the caller); its folders join the caller's. wrest:
    the words after it as written; the command is aligned when the caller's words and the string's are (D5). starts:
    False when the word re-lexed is a tail's first word, not a command word: then the U8 head rules stay off."""
    inner, winner, ok = aligned_words(line)
    words, written = inner + rest, winner + (rest if wrest is None else wrest)
    sub = list(cwds)
    LEVELS.append(None)                                # R5: env's split string has no bindings
    try:
        for kind, payload, extra in unwrap(words):
            if kind == "script":
                script(payload, sub, word, fed)
            else:
                w = written[len(written) - len(payload):]
                within(word, lambda: check_command(payload, structured or extra, sub, fed, written=w,
                                                   aligned=aligned and ok, starts=starts))
    finally:
        LEVELS.pop()
    add(cwds, sub)


def within(word, fn):
    """Run fn; a refusal names the script string it was seen in."""
    if word is None:
        return fn()
    try:
        return fn()
    except Deny as d:
        raise Deny(d.rule, f'{d.reason}; seen inside a script string of "{word}", which git-policy reads as text') from None


def behind(toks, k, fn):
    """Run fn; a refusal names the runner the suffix toks[k:] was found behind (N2)."""
    try:
        fn()
    except Deny as d:
        raise Deny(d.rule, f'{d.reason}; seen behind "{shlex.join(toks[:k])[:60]}", a runner git-policy does not read') from None


def script(text, cwds, word, fed=None):
    """A script string a shell runs: checked from the current candidate cwds; the folders it reaches join them,
    since its cd never moves the caller (N1c). It keeps the caller's fed and placeholder candidates (an xargs -I
    placeholder is replaced inside it too); one that reads $@, $* or $0 to $9 is fed by its arguments (U7)."""
    sub = list(cwds)
    if re.search(r"\$\{?[@*0-9]", text):
        fed = feed(fed, FED_ARGS)
    within(word, lambda: evaluate(text, sub, fed))
    add(cwds, sub)


def check_command(toks, structured, cwds, fed, help_ok=False, written=None, aligned=True, starts=True, joined=False):
    """starts: the words begin a command (False for a tail, a parameter's text or an arithmetic operand that
    split_segments cut off): only then are the head and git's subcommand read for U8. joined: the head word was
    joined across a backslash-newline; a cd so spelled adds a candidate, as the parser read it before the join."""
    if not toks:
        return
    written = toks if written is None else written
    if re.search(r"\s", toks[0]):                                  # N3b: a head holding whitespace, env -S'...'
        line = re.sub(r"^(-[A-Za-z]|--[A-Za-z][A-Za-z0-9-]*=)", "", toks[0])
        split_string(toks[0], line, toks[1:], structured, cwds, fed, written[1:], aligned, starts)
        return
    if starts and unreadable(toks[0], written[0], aligned):        # D6: the head of every level (U8)
        var = VAR_HEAD.fullmatch(written[0]) if aligned else None
        if var:                                                    # R5 (gh-ticket#49): a plain name, literal parts
            level = LEVELS[-1] if LEVELS else None
            tail = (var.group("t1") or "") + (var.group("t2") or "")
            value = None
            if level is not None and level.cur is not None:
                value = level.resolve(var.group("n1") or var.group("n2"), level.cur)
            if value is not None and os.path.basename(value + tail).lower() in NO_RESOLVE:
                value = None                                       # C3: a cd, pushd or popd head stays U8
            if value is not None:                                # F5: as written with the head's U8 off, then
                check_command(toks, structured, cwds, fed, help_ok, written, aligned, False, joined)
                r = value + tail                                   # resolved, structured: a cd adds a candidate
                check_command([r] + toks[1:], True, cwds, fed, help_ok, [r] + written[1:], aligned, starts, joined)
                return
            if VARIABLE_HEADS_SHIM and not git_follows(level):     # (3), off until the owner's date
                s = "__var_head__" + tail
                check_command([s] + toks[1:], structured, cwds, fed, help_ok, [s] + written[1:], aligned, starts,
                              joined)
                return
        raise Deny("U8", HEAD_U8.format(written[0][:60]))
    head = os.path.basename(toks[0]).lower()
    if head == "cd":
        if len(toks) > 1:
            new = [absolute(toks[1], c) for c in cwds]
            if structured or os.path.basename(toks[0]) != "cd" or joined:   # a cd that may not run (N1c); CD is
                add(cwds, new)                                     # no builtin; cd\<newline> (gh-ticket#44)
            else:
                cwds[:] = []
                add(cwds, new)
        return
    if head == "git":
        for c in list(cwds):
            check_git(toks, c)
    elif head == "gh":
        check_gh(toks, help_ok and not structured and fed is None)   # the U6 help line: a head command only
    if fed and head in ("git", "gh"):
        check_fed(toks, fed)
    if starts and head == "git":                                   # D11, git's half: its subcommand must be read (U8)
        _, sub, args, _ = parse_git(toks, "/")                    # the value of -C or -c is skipped, as git skips it
        k = len(toks) - len(args) - 1
        if sub and unreadable(toks[k], written[k], aligned):
            raise Deny("U8", GIT_SUB_U8.format(written[k][:60]))
    shells = shell_scripts(toks)
    split = split_at(toks, 0)
    if split:                                                      # N3b at the head: env -S 'gh pr' merge 12
        split_string(split[0], split[0], toks[split[1]:], structured, cwds, fed, written[split[1]:], aligned)
    xargs_at = 0 if head == "xargs" else None
    for k in range(1, len(toks)):                                  # N2: gh and git behind any runner
        here = feed(fed, FED_XARGS, toks[xargs_at + 1:k]) if xargs_at is not None else fed
        if k in shells:                                            # N3: a shell's script operand, anywhere
            script(toks[shells[k]], cwds, toks[k], here)
        split = split_at(toks, k)
        if split:                                                  # N3b anywhere: xargs -I X env -S 'gh pr X 12'
            split_string(split[0], split[0], toks[split[1]:], structured, cwds, here, written[split[1]:], aligned)
        w = os.path.basename(toks[k]).lower()
        if w in ("git", "gh"):
            if head == "git" and toks[k - 1] in GIT_OPTS_WITH_VALUE or head == "gh" and toks[k - 1] in ("-R", "--repo"):
                continue
            suffix = toks[k:]
            if w == "git":
                behind(toks, k, lambda: [check_git(suffix, c) for c in list(cwds)])
            else:
                behind(toks, k, lambda: check_gh(suffix))
            if here:
                check_fed(suffix, here)
        elif w == "cd" and head not in ("git", "gh") and k + 1 < len(toks):
            add(cwds, [absolute(toks[k + 1], c) for c in cwds])   # behind a runner: a candidate, never a move
        if w == "xargs" and xargs_at is None:
            xargs_at = k
    if 0 in shells:
        script(toks[shells[0]], cwds, toks[0], fed)


def evaluate(text, cwds, fed=None, help_ok=False):
    """Check every command in the text from every candidate cwd; cwds, a list, is updated in place. help_ok (from main
    only, when the whole text is a HELP_TEXT line) reaches the head commands, never a script or a split string."""
    level = Level(text)                                # R5: the text level whose bindings its heads may read
    LEVELS.append(level)
    try:
        for n, kind, payload, extra in commands(level.parts):
            level.cur = n
            if kind == "script":
                script(payload, cwds, extra, fed)
            else:
                structured, written, aligned, starts, joined = extra
                check_command(payload, structured, cwds, fed, help_ok, written, aligned, starts, joined)
    finally:
        LEVELS.pop()
    return cwds


SCOPE = re.compile(r"&&|\|\||;|\n|(?<![<>&|])&(?![>&])")       # a pipeline: | does not split; quotes are ignored
WORD = re.compile(r"[a-z0-9_-]+")                              # whole words, - included: gh-ticket is not gh


def backstop(text):
    """The raw-text backstop (gh only): a pipeline of the raw text, heredoc bodies included, that names the words of
    a guarded gh action is refused whatever its shape, case-insensitively. A backslash-newline joins its lines first,
    quotes ignored, as a shell reading the string joins them (ssh host 'gh pr \\<newline>merge 12')."""
    for scope in SCOPE.split(text.lower().replace("\\\n", "")):
        words = set(WORD.findall(scope))
        if {"gh", "ticket", "merge"} <= words and any(no_codex(w) for w in words):
            raise Deny("U5", "this command line names gh, ticket, merge and --no-codex (or a prefix of it) in one pipeline, "
                             "and git-policy refuses such text whatever its shape: put the text in a file (global rule 9), "
                             "or search with the Grep tool")
        if {"gh", "pr"} <= words and words & {"merge", "create"}:
            raise Deny("U6", "this command line names gh, pr and merge (or create) in one pipeline, and git-policy "
                             "refuses such text whatever its shape: put the text in a file (global rule 9), or search "
                             "with the Grep tool")


SHIM_MARKER = re.compile(r"GH_TICKET_INNER(?![A-Za-z0-9_])")    # (c1): no left boundary, -S<name> too (gh-ticket#53)
SHIM_RUN = re.compile(r"[\s;&|()<>'\"`]+")                     # (c2): runs of text, cut where a shell word could end
GH_FOLDERS = ("/.config/gh", "/.local/share/gh", "/.local/state/gh", "/.cache/gh")
SETS_PATH = re.compile(r"(?<![A-Za-z0-9_$])PATH\+?="           # PATH= and PATH+=, never PYTHONPATH= or $PATH
                       r"|(?<![A-Za-z0-9_-])(?:export|typeset|declare|local|readonly)(?![A-Za-z0-9_-])"
                       r"[^;&|\n()]*?(?<![A-Za-z0-9_$])(?<!\$\{)PATH(?![A-Za-z0-9_])"
                       r"|(?<![A-Za-z0-9_$])path(?:\+?=\(|\[)")    # zsh's path array
GH_WORD = re.compile(r"(?:^|(?<=[\s;&|('\"`/]))gh(?:-ticket)?(?![A-Za-z0-9_.-])", re.I)   # (c3): gh or gh-ticket alone


def shim_text(text):
    """U9 (gh-ticket#45): raw text that would get past the gh shim, quotes ignored, heredoc bodies included."""
    if SHIM_MARKER.search(text):
        raise Deny("U9", "this command names GH_TICKET_INNER, the marker that lets gh-ticket's own gh calls past the gh "
                         "shim; only gh-ticket sets it: run gh ticket ..., and search for the name with the Grep or Read tool")
    for w in SHIM_RUN.split(text):
        low = w.lower()
        if low.endswith("/gh") and not (low.endswith("/shim/gh") or low == "shim/gh" or low.endswith(GH_FOLDERS)):
            raise Deny("U9", f"{w[:60]} names gh by a path, which skips the gh shim (gh-ticket#45): call it as gh")
    if SETS_PATH.search(text) and GH_WORD.search(text):    # the owner's ruling: a PATH set alone is allowed
        raise Deny("U9", "this command sets PATH and names gh, which can put the real gh ahead of the gh shim: set "
                         "PATH in a command that does not call gh")


SESSION_MARKERS = ("CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION")   # pre-push's SESSION, reference-transaction's session()
SESSION_NAME = re.compile("(?:" + "|".join(SESSION_MARKERS) + r")(?![A-Za-z0-9_])")   # (c1): no left boundary, as U9 (c1)
U10_DEPTH = 4                                                   # (c2): nested words are lexed again this deep
ENV_VALUE_LETTERS = "uCSPLU"                                    # env's short options that take a value
ENV_LONG_VALUE = ("--unset", "--chdir")                         # and its long ones (--split-string is read apart)
OPERATOR = re.compile(r"[();<>|&]+")                            # a token shlex's punctuation_chars makes
REDIRECTION = re.compile(r"[<>&]*[<>][<>&|]*")                  # > >> < << <<< <> >& <& &> &>> >|, never | & ;
FALLBACK_CUT = re.compile(r"&&|\|\|?|;|\n|[()]|(?<![<>&|])&(?![>&])")   # where a command ends, never inside 2>&1
U10_UNREADABLE = "(unreadable)"                                 # env_clears: the fallback refused a word it read
U10_C1 = (f"this command names {' or '.join(SESSION_MARKERS)}, the markers the git hooks read to tell an agent session "
          "from the owner's terminal (gh-ticket#57). A session never reads, sets or unsets them: search with the Grep or "
          "Read tool; a test that needs the owner's terminal clears them inside its test file; anything else that needs "
          "them gone is run from the owner's terminal")
U10_C2 = ("{} starts a command without the session markers the git hooks read (gh-ticket#57): drop one variable with "
          "env -u NAME, clear the environment inside a test file the suite runs, or run it from the owner's terminal")
U10_C2U = ("this text cannot be read to rule out env -i or exec -c (gh-ticket#57): write the script with the Write tool "
           "(not a heredoc, which is read the same way) and run it by path (bash /tmp/x.sh), or run it from the "
           "owner's terminal")


class Unreadable(Exception):
    """U10 (c2): shlex cannot read a text (an unbalanced quote), or a word is nested too deep: the fallback reads it."""


def u10_words(text):
    """The words of text as a POSIX shell splits them: a quoted value one word, an empty one kept, ; & | ( ) < > as
    tokens of their own, and no comment (# hides nothing). Raises Unreadable when shlex cannot read the text."""
    lex = shlex.shlex(text, posix=True, punctuation_chars=True)
    lex.whitespace_split, lex.commenters = True, ""
    try:
        return list(lex)
    except ValueError as e:
        raise Unreadable(str(e)) from None


def redirection_end(words, i):
    """The index after a redirection at words[i] (an fd number, the operator, its target), or i when there is none:
    the shell removes it before env or exec runs, so their option run reads past it."""
    k = i + 1 if words[i].isdigit() and i + 1 < len(words) and REDIRECTION.fullmatch(words[i + 1]) else i
    return k + 2 if REDIRECTION.fullmatch(words[k]) else i


def value_word(words, i):
    """An option's separate value at or after words[i], past any redirections (the shell removes them first): (the value,
    the index after it). Past the end, the value is empty."""
    while i < len(words) and redirection_end(words, i) != i:
        i = redirection_end(words, i)
    return (words[i], i + 1) if i < len(words) else ("", i)


def env_run(words, i, depth):
    """The clearing form in the option run of the env word before words[i], or None. The run ends at --, at an operator,
    or at the first word that is neither an option nor NAME=VALUE; a value-taking letter takes the rest of its word,
    else the whole next word, empty or not; an -S value's words continue the run."""
    while i < len(words):
        end = redirection_end(words, i)
        if end != i:
            i = end
            continue
        w = words[i]
        if w == "--" or OPERATOR.fullmatch(w):
            return None
        if w == "-":
            return "env -"
        if w.startswith("--"):
            name, eq, value = w.partition("=")
            if len(name) >= 3 and "--ignore-environment".startswith(name):
                return f"env {w}"
            if len(name) >= 3 and "--split-string".startswith(name):
                value, after = (value, i + 1) if eq else value_word(words, i + 1)
                return env_split(value, words[after:], depth)
            if not eq and len(name) >= 3 and any(o.startswith(name) for o in ENV_LONG_VALUE):
                i = value_word(words, i + 1)[1]
            else:
                i += 1
            continue
        if w.startswith("-"):
            for k, ch in enumerate(w[1:], 1):
                if ch == "i":
                    return f"env {w}"
                if ch in ENV_VALUE_LETTERS:
                    rest = w[k + 1:]
                    value, after = (rest, i + 1) if rest else value_word(words, i + 1)
                    if ch == "S":
                        return env_split(value, words[after:], depth)
                    i = after
                    break
            else:
                i += 1
            continue
        if re.fullmatch(VAR, w, re.S):
            i += 1
            continue
        return None
    return None


def env_split(value, rest, depth):
    """env -S VALUE: the split string's words continue env's option run, then the words after it."""
    if depth >= U10_DEPTH:
        raise Unreadable("an -S value nested too deep")
    return env_run(u10_words(value) + list(rest), 0, depth + 1)


def exec_run(words, i):
    """exec -c (bash and zsh) in the option run of the exec word before words[i], or None; -a takes the rest of its word,
    else the whole next word, empty or not."""
    while i < len(words):
        end = redirection_end(words, i)
        if end != i:
            i = end
            continue
        w = words[i]
        if w in ("-", "--") or not w.startswith("-"):
            return None
        for k, ch in enumerate(w[1:], 1):
            if ch == "c":
                return f"exec {w}"
            if ch == "a":
                i = i + 1 if w[k + 1:] else value_word(words, i + 1)[1]
                break
        else:
            i += 1
    return None


def env_clears(text, depth=0):
    """U10 (c2): the form (env -i, exec -c, ...) that starts a command in text with the environment cleared, or None, or
    U10_UNREADABLE when a nested word the lexer cannot read is refused by the fallback. An env word is any word whose
    basename is env, any case, a leading backslash dropped (env, /usr/bin/env, ENV); so is an exec word. Each word
    that holds whitespace (a shell's -c script, an -S value, any quoted string) is lexed and scanned again, to depth
    U10_DEPTH; a word deeper than that, or one the lexer cannot read, goes to the fallback. Raises Unreadable when the
    text itself cannot be read."""
    if depth == 0 and os.environ.get("GIT_POLICY_TEST_CRASH") == "u10-scan":
        raise RuntimeError("forced U10 scan failure for the test suite")
    words = u10_words(text)
    for i, w in enumerate(words):
        head = os.path.basename(w).lower()
        head = head[1:] if head.startswith("\\") else head
        form = env_run(words, i + 1, depth) if head == "env" else exec_run(words, i + 1) if head == "exec" else None
        if not form and re.search(r"\s", w):
            try:
                if depth >= U10_DEPTH:
                    raise Unreadable("a word nested too deep")
                form = env_clears(w, depth + 1)
            except Unreadable:
                form = u10_fallback(w)
        if form:
            return form
    return None


def env_clears_fallback(text):
    """U10 (c2), the cautious fallback for a text the lexer cannot read: SHIM_RUN's runs, consuming no option value. After
    an env word, up to the end of its command (; & | ( ) or a newline), a lone -, a short cluster holding i, or a
    prefix of --ignore-environment at least --i long refuses; after an exec word, a short cluster holding c. A lost
    boundary can only refuse more."""
    if os.environ.get("GIT_POLICY_TEST_CRASH") == "u10-fallback":
        raise RuntimeError("forced U10 fallback failure for the test suite")
    for command in FALLBACK_CUT.split(text):
        after_env = after_exec = False
        for w in SHIM_RUN.split(command):
            head = os.path.basename(w).lower()
            head = head[1:] if head.startswith("\\") else head
            # a short cluster refuses when its letters reach i (env) or c (exec) before anything else, an attached
            # value of any characters after it included (-iP/bin, -ca./name): the Codex review of gh-ticket#57
            if after_env and (w == "-" or re.match(r"-[A-Za-z0-9]*i", w)
                              or len(w) >= 3 and "--ignore-environment".startswith(w)):
                return True
            if after_exec and re.match(r"-[A-Za-z0-9]*c", w):
                return True
            after_env, after_exec = after_env or head == "env", after_exec or head == "exec"
    return False


def u10_fallback(text):
    """U10_UNREADABLE when the fallback refuses text, else None. An error in the fallback allows the text, with one
    stderr line naming U10 so the session reports it (the owner's option C)."""
    try:
        return U10_UNREADABLE if env_clears_fallback(text) else None
    except Exception as e:
        print(f"git-policy U10: internal error in the fallback ({type(e).__name__}: {e}); the text was allowed", file=sys.stderr)
        return None


def session_text(text):
    """U10 (gh-ticket#57): raw text that would hide an agent session from the git hooks, quotes ignored for (c1), heredoc
    bodies included, backslash-newlines joined. Fails closed: a text the lexer cannot read, or an error in the scan,
    goes to the cautious fallback, which can only refuse more; an error in U10 is one stderr line naming it."""
    text = text.replace("\\\n", "")
    if SESSION_NAME.search(text):
        raise Deny("U10", U10_C1)
    try:
        form = env_clears(text)
    except Unreadable:
        form = u10_fallback(text)
    except Exception as e:
        print(f"git-policy U10: internal error in the scan ({type(e).__name__}: {e}); the cautious fallback decided",
              file=sys.stderr)
        form = u10_fallback(text)
    if form == U10_UNREADABLE:
        raise Deny("U10", U10_C2U)
    if form:
        raise Deny("U10", U10_C2.format(form))


def main():
    raw = sys.stdin.read()
    capture = LOG.parent / "capture"
    if capture.is_dir():                               # the owner's switch: keep raw payloads for the fixtures
        import time
        (capture / f"payload-{time.time_ns()}-{os.getpid()}.json").write_text(raw)   # unique: hooks run concurrently
    data = json.loads(raw)
    if data.get("tool_name") not in ("Bash", "Monitor"):
        return 0
    text = (data.get("tool_input") or {}).get("command") or ""
    try:
        if os.environ.get("GIT_POLICY_TEST_CRASH") == "1":  # D1: every text is parsed, no fast path (g\\h is gh)
            raise RuntimeError("forced crash for the test suite")
        help_text = HELP_TEXT.fullmatch(text) is not None   # one of U6's four help lines, as the whole text (gh-ticket#30)
        try:
            evaluate(text, [data.get("cwd") or os.getcwd()], help_ok=help_text)
        except Deny as d:
            if d.rule in ("U7", "U8") and not help_text:
                backstop(text)                             # D10: the backstop's U5 or U6 speaks before U7 and U8
                shim_text(text)                            # and U9 before U7 and U8 (gh-ticket#45)
                session_text(text)                         # and U10 too (gh-ticket#57)
            raise
        if not help_text:
            backstop(text)
        shim_text(text)                                    # a help line holds no marker, /gh or PATH
        session_text(text)
        return 0
    except Deny:
        raise
    except Exception:                                      # U10 holds when the parser does not (gh-ticket#57): a
        session_text(text)                                 # refusal here exits 2; otherwise the crash fails open below
        raise


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Deny as d:
        print(f"git-policy {d.rule}: {d.reason}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:                             # fail open, but leave a trace
        try:
            LOG.parent.mkdir(parents=True, exist_ok=True)
            with LOG.open("a") as f:
                f.write(f"{type(e).__name__}: {e}\n")
        except OSError:
            pass
        print(f"git-policy: hook error, command allowed: {e}", file=sys.stderr)
        sys.exit(1)
