#!/usr/bin/env python3
"""git-policy: a Claude Code PreToolUse hook on Bash and Monitor that enforces the branch model.

It is the early warning; the git hooks (pre-commit, pre-push, reference-transaction) are the
authority. Reads the hook payload on stdin, finds every git and gh command in the Bash command text,
and denies (exit 2, one line on stderr naming the rule) when one breaks a rule. Policy is decided
from the repository the command acts on: `git -C X`, `--git-dir`, `--work-tree`, else the last
`cd X` earlier in the chain, else the payload's cwd. Not inside a repository: allowed.

Universal rules, every repository:
  U1  push with --force, -f, --force-with-lease, --force-if-includes, or a + refspec
  U2  push naming local-history, or --all or --mirror
  U3  push with --no-verify or -c core.hooksPath=; a push of a wip/* branch; a push whose outgoing
      commits carry "do not push" or "local only"; a push whose source cannot be resolved from the
      command and the config with certainty ("name the refspec"): a bare push follows
      remote.<r>.push, else push.default (simple, current, upstream; matching and nothing are
      refused). Grouped short flags (-uf, -Df) are split before every check.
  U4  branch deletion and ref removal (branch -d/-D, push --delete, a :X refspec, update-ref -d,
      worktree remove --force); commit --amend, rebase, reset --hard, branch -m/-M on or naming a
      protected branch (PROTECTED_BRANCHES)
  U5  gh ticket merge --no-codex: the owner's, from his own terminal
  U6  any gh invocation whose words include pr followed by create or merge, wherever the flags
      sit: use gh ticket pr / gh ticket merge
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
treats as non-blocking. While the directory ~/.cache/gh-ticket/capture exists, every raw payload
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
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", line)
        out.append(line[:m.start()] + " " + line[m.end():] if m else line)
        if m:
            i += 1
            while i < len(lines) and lines[i].strip() != m.group(2):
                i += 1
        i += 1
    return "\n".join(out)


def split_segments(text):
    """Split on &&, ||, ;, |, &, newlines and ( ) { } $( ) outside quotes."""
    segs, cur, i, q = [], [], 0, None
    while i < len(text):
        ch = text[i]
        if q:
            if ch == "\\" and q == '"' and i + 1 < len(text):
                cur.append(text[i:i + 2]); i += 2; continue
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in ("'", '"'):
            q = ch; cur.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < len(text):
            cur.append(text[i:i + 2]); i += 2; continue
        if text.startswith("$(", i):
            segs.append("".join(cur)); cur = []; i += 2; continue
        if ch == "&" and ((cur and cur[-1] in (">", "<")) or text.startswith("&>", i)):
            cur.append(ch); i += 1; continue          # a redirection (2>&1, >&2, &>file), not a separator
        if ch in "&|;\n(){}":
            segs.append("".join(cur)); cur = []
            i += 2 if text.startswith("&&", i) or text.startswith("||", i) else 1
            continue
        cur.append(ch); i += 1
    segs.append("".join(cur))
    return [s.strip() for s in segs if s.strip()]


REDIRECT = re.compile(r"^\d*(>>|>&|<&|&>|>|<)(.*)$")


def tokens(seg):
    try:
        raw = shlex.split(seg)
    except ValueError:
        raw = seg.split()
    out, skip = [], False
    for t in raw:                                       # drop redirections and their targets
        if skip:
            skip = False; continue
        m = REDIRECT.match(t)
        if m:
            skip = m.group(2) == ""                     # "> file": the target is the next token
            continue
        out.append(t)
    return out


def unwrap(toks):
    """Drop VAR=x prefixes and wrappers; a `bash -c "..."` yields its own segments."""
    while toks:
        head = os.path.basename(toks[0])
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", toks[0]):
            toks = toks[1:]
        elif head in ("env", "command", "time", "nohup", "xargs", "sudo", "exec", "builtin", "caffeinate"):
            toks = toks[1:]
            while toks and (toks[0].startswith("-") or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", toks[0])):
                toks = toks[1:]
        elif head in ("bash", "sh", "zsh", "dash") and len(toks) >= 3 and toks[1] in ("-c", "-lc", "-ec", "-euc", "-exc"):
            return [("inner", toks[2])]
        else:
            break
    return [("cmd", toks)] if toks else []


def commands(text):
    """Yield (tokens) for every simple command in the text, in order, wrappers unwrapped."""
    for seg in split_segments(strip_heredocs(text)):
        for kind, payload in unwrap(tokens(seg)):
            if kind == "inner":
                yield from commands(payload)
            else:
                yield payload


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


def check_push(repo, args, configs, opted):
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
    tags = "--tags" in args or "--follow-tags" in args
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
    repo = Repo(base)
    if not repo.ok:
        return
    on_protected = repo.branch in PROTECTED_BRANCHES
    names_protected = any(a in PROTECTED_BRANCHES for a in args)
    # U4
    if sub == "branch" and any(a in ("-d", "-D", "--delete") for a in args):
        raise Deny("U4", "deleting a branch needs the owner's yes; he runs it")
    if sub == "update-ref" and any(a in ("-d", "--delete") for a in args):
        raise Deny("U4", "removing a ref needs the owner's yes; he runs it")
    if sub == "worktree" and args[:1] == ["remove"] and any(a in ("--force", "-f") for a in args):
        raise Deny("U4", "git worktree remove --force discards a tree's changes; the owner runs it")
    if sub == "branch" and any(a in ("-m", "-M", "--move") for a in args) and (on_protected or names_protected):
        raise Deny("U4", f"renaming {repo.branch or 'a protected branch'} needs the owner's yes")
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


def check_gh(toks, cwd):
    args = toks[1:]
    words, i = [], 0                                   # the words without gh's -R/--repo and its value
    while i < len(args):
        if args[i] in ("-R", "--repo"):
            i += 2; continue
        if not (args[i].startswith("--repo=") or (args[i].startswith("-R") and len(args[i]) > 2)):   # -Rx, -R=x
            words.append(args[i])
        i += 1
    if words[:2] == ["ticket", "merge"] and "--no-codex" in words:
        raise Deny("U5", "gh ticket merge --no-codex is the owner's, from his own terminal: fix or answer the Codex findings "
                         "and rereview instead")
    if "pr" in args and {"create", "merge"} & set(args[args.index("pr") + 1:]):
        raise Deny("U6", "open and merge PRs with gh ticket pr N and gh ticket merge N, never gh pr create or gh pr merge "
                         "(every repository; gh ticket pushes, sets the base and the body, and merges in the right style)")


# ---------------------------------------------------------------- main

def evaluate(text, cwd):
    for toks in commands(text):
        if not toks:
            continue
        head = os.path.basename(toks[0])
        if head == "cd" and len(toks) > 1:
            cwd = absolute(toks[1], cwd)
        elif head == "git":
            check_git(toks, cwd)
        elif head == "gh":
            check_gh(toks, cwd)


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
    if "git" not in text and "gh" not in text:
        return 0                                       # fast path, no parsing
    if os.environ.get("GIT_POLICY_TEST_CRASH") == "1":
        raise RuntimeError("forced crash for the test suite")
    evaluate(text, data.get("cwd") or os.getcwd())
    return 0


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
