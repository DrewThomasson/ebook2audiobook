#!/usr/bin/env python3
"""SessionStart hook: report when the installed att-docs plugins are behind the repository.

Claude Code caches an installed plugin at the version it had when it was installed or last
updated, so a version bump that merges here changes nothing on a machine until someone runs
the update. This hook compares the version each att-docs plugin is installed at, for the
session's project, with the newest version it can learn about without a prompt or a long wait:

- the plugin.json files in the marketplace clone Claude Code keeps, and
- the newest v* release tag on the clone's origin, looked up with `git ls-remote` at most once
  every six hours and never with a credential prompt.

A plugin the project turns off in `enabledPlugins` is left out, since a repository that vendors
this one turns off att-docs and general. When a plugin is behind the hook prints one JSON
object, whose systemMessage the user sees and whose additionalContext the session reads, with
the commands that bring each plugin up to date in the scope it is installed in. It prints
nothing when every plugin is current or the newest version is unknown, and always exits 0,
since a version check must never hold up a session.

The hook runs from the voice plugin and is registered without run.sh. The voice plugin is the
one installed at user scope in every repository, a repository that vendors this one leaves it
on, and run.sh steps aside in a repository that registers its own voice hooks, which would
hide a version warning.

usage: plugin_version_check.py < hook payload

Environment: CLAUDE_CONFIG_DIR (default ~/.claude), CLAUDE_PROJECT_DIR (default the working
directory), CLAUDE_PLUGIN_DATA (where the tag lookup is cached; default the plugins folder).
"""
import json
import os
import re
import subprocess
import sys
import time

MARKETPLACE = "att-docs"
TAG_TTL = 6 * 60 * 60
GIT_WAIT = 3  # seconds the tag lookup may take
VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def version_key(text):
    """(major, minor, patch) for a version or v-prefixed tag, None for anything else."""
    m = VERSION.match(text) if isinstance(text, str) else None
    return tuple(int(g) for g in m.groups()) if m else None


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def project_paths(project, run=subprocess.run):
    """The paths an install for the project can be recorded under, in the order they count:
    the project itself, then its real path, then the main checkout when the project is a git
    worktree, which a worktree without a record of its own falls back to."""
    paths = [project, os.path.realpath(project)]
    try:
        out = run(["git", "-C", project, "rev-parse", "--path-format=absolute",
                   "--git-common-dir"], capture_output=True, text=True, timeout=GIT_WAIT,
                  check=True, stdin=subprocess.DEVNULL).stdout.strip()
        if os.path.basename(out) == ".git":
            paths.append(os.path.dirname(out))
    except (OSError, subprocess.SubprocessError):
        pass
    return list(dict.fromkeys(paths))


def installed_versions(plugins_dir, projects):
    """name -> (version, scope) the session's project runs. An entry for one of the project's
    paths (a local or project scope with its projectPath; the earlier path wins) beats the
    user scope one."""
    data = read_json(os.path.join(plugins_dir, "installed_plugins.json"))
    found = {}
    entries = data.get("plugins") if isinstance(data, dict) else None
    for key, installs in (entries if isinstance(entries, dict) else {}).items():
        name, _, market = key.partition("@")
        if market != MARKETPLACE or not isinstance(installs, list):
            continue
        own = user = None
        rank = len(projects)
        for e in installs:
            if not isinstance(e, dict) or version_key(e.get("version")) is None:
                continue
            if e.get("scope") == "user":
                user = (e["version"], "user")
            elif e.get("scope") in ("local", "project") and e.get("projectPath") in projects:
                if projects.index(e["projectPath"]) < rank:
                    rank = projects.index(e["projectPath"])
                    own = (e["version"], e["scope"])
        if own or user:
            found[name] = own or user
    return found


def turned_off(config, project, name):
    """True when the effective enabledPlugins value for the plugin is false: the first of the
    project's local settings, its shared settings and the user settings that names it decides."""
    key = "%s@%s" % (name, MARKETPLACE)
    for path in (os.path.join(project, ".claude", "settings.local.json"),
                 os.path.join(project, ".claude", "settings.json"),
                 os.path.join(config, "settings.json")):
        data = read_json(path)
        enabled = data.get("enabledPlugins") if isinstance(data, dict) else None
        if isinstance(enabled, dict) and key in enabled:
            return enabled[key] is False
    return False


def marketplace_source(plugins_dir):
    """(clone folder, ref the marketplace was added with or None, its GitHub repo or None)."""
    data = read_json(os.path.join(plugins_dir, "known_marketplaces.json"))
    entry = data.get(MARKETPLACE) if isinstance(data, dict) else None
    if not isinstance(entry, dict):
        return None, None, None
    source = entry.get("source") if isinstance(entry.get("source"), dict) else {}
    return entry.get("installLocation"), source.get("ref"), source.get("repo")


def clone_versions(clone):
    """name -> the version the marketplace clone's plugin.json holds."""
    found = {}
    base = os.path.join(clone or "", "plugins")
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return found
    for name in names:
        manifest = read_json(os.path.join(base, name, ".claude-plugin", "plugin.json"))
        if isinstance(manifest, dict) and version_key(manifest.get("version")):
            found[name] = manifest["version"]
    return found


def latest_tag(clone, cache_file, now, run=subprocess.run):
    """The newest v* release tag on the clone's origin, from the cache while it is fresh. A
    lookup that fails keeps the tag cached before it and is not repeated for the same period."""
    cached = read_json(cache_file)
    cached = cached if isinstance(cached, dict) else {}
    tag = cached.get("tag")
    checked = cached.get("checked")
    if isinstance(checked, (int, float)) and 0 <= now - checked < TAG_TTL:
        return tag
    if clone:
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        try:
            out = run(["git", "-C", clone, "ls-remote", "--tags", "--refs", "origin", "v*"],
                      capture_output=True, text=True, timeout=GIT_WAIT, env=env, check=True,
                      stdin=subprocess.DEVNULL).stdout
            tags = [t for t in (line.rpartition("refs/tags/")[2].strip()
                                for line in out.splitlines()) if version_key(t)]
            if tags:
                tag = max(tags, key=version_key)
        except (OSError, subprocess.SubprocessError):
            pass
    try:
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"checked": now, "tag": tag}, f)
    except OSError:
        pass
    return tag


def behind(installed, newest):
    """name -> (installed version, newest version, scope) for each plugin below the newest."""
    out = {}
    for name, (have, scope) in installed.items():
        want = newest.get(name)
        if want and version_key(have) < version_key(want):
            out[name] = (have, want, scope)
    return out


def message(late, pinned, repo, tag):
    names = sorted(late)
    lines = ", ".join("%s %s (now %s)" % (n, late[n][0], late[n][1]) for n in names)
    if pinned:
        steps = ["claude plugin marketplace remove %s" % MARKETPLACE,
                 "claude plugin marketplace add %s#%s" % (repo or "<owner>/<repo>", tag)]
        steps += ["claude plugin install %s@%s --scope %s" % (n, MARKETPLACE, late[n][2])
                  for n in names]
    else:
        steps = ["claude plugin marketplace update %s" % MARKETPLACE]
        steps += ["claude plugin update %s@%s --scope %s" % (n, MARKETPLACE, late[n][2])
                  for n in names]
    return ("Installed %s plugins are behind the repository: %s. Run, in order: %s. "
            "Then start a new session; skills added since the installed version are not "
            "listed until then." % (MARKETPLACE, lines, "; ".join(steps)))


def main():
    sys.stdin.read()
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    plugins_dir = os.path.join(config, "plugins")
    project = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    installed = {n: v for n, v in installed_versions(plugins_dir, project_paths(project)).items()
                 if not turned_off(config, project, n)}
    if not installed:
        return
    clone, ref, repo = marketplace_source(plugins_dir)
    newest = clone_versions(clone)
    cache = os.path.join(os.environ.get("CLAUDE_PLUGIN_DATA") or plugins_dir,
                         "att-docs-latest-tag.json")
    tag = latest_tag(clone, cache, time.time())
    if tag:
        # release-please writes the tag's version into every plugin.json, so one tag names
        # the newest version of each plugin the clone holds
        for name in newest:
            if version_key(newest[name]) < version_key(tag):
                newest[name] = tag.lstrip("v")
    late = behind(installed, newest)
    if late:
        label = tag or "v%s" % max((late[n][1] for n in late), key=version_key)
        text = message(late, ref is not None, repo, label)
        print(json.dumps({"systemMessage": text, "hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": text}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # a version check never holds up a session
        pass
