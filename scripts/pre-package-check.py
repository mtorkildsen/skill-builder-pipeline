#!/usr/bin/env python3
"""
pre-package-check.py — skill-pipeline pre-package validation gate
Run from the plugin root before every packaging step.

Delegates structural checks to smoke-test.py --json, then adds:
  - plugin.json version === CLAUDE.md version
  - every SKILL.md that has metadata.version uses valid semver

Exit codes:
  0 — all checks pass
  1 — one or more checks failed
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9._-]+)?$")
VERSION_IN_CLAUDE_MD = re.compile(r"Current version:\s+\*\*([0-9]+\.[0-9]+\.[0-9]+[^\*]*)\*\*")

def is_tty():
    return sys.stdout.isatty()

def colorize(text, color):
    if not is_tty():
        return text
    codes = {"green": "\033[32m", "red": "\033[31m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"

def ok(label):
    return f"  {colorize('PASS', 'green')}  {label}"

def fail(label, detail=""):
    suffix = f" -- {detail}" if detail else ""
    return f"  {colorize('FAIL', 'red')}  {label}{suffix}"


def run_smoke_test(plugin_root: Path) -> tuple[bool, list[str]]:
    """Run smoke-test.py --json and return (passed, violation_messages)."""
    script = plugin_root / "scripts" / "smoke-test.py"
    if not script.exists():
        return False, ["smoke-test.py not found at scripts/smoke-test.py"]

    result = subprocess.run(
        [sys.executable, str(script), "--json", "--root", str(plugin_root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode == 2:
        return False, [f"smoke-test.py exited with error: {result.stderr.strip()}"]

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return False, [f"smoke-test.py produced invalid JSON: {result.stdout[:200]}"]

    messages = []
    for check in data.get("checks", []):
        for v in check.get("violations", []):
            loc = f"{v.get('file', '')}:{v.get('line', '')}" if v.get("file") else ""
            messages.append(f"{check['id']} | {loc} | {v.get('error', '')} | {v.get('detail', '')}")

    return data.get("overall") == "pass", messages


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm_text = text[3:end].strip()
    try:
        return yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None


def check_version_alignment(plugin_root: Path) -> tuple[bool, list[str]]:
    """Check plugin.json version == CLAUDE.md version, and every SKILL.md semver."""
    issues = []

    # Load plugin.json version
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        plugin_version = manifest.get("version", "")
    except Exception as e:
        return False, [f"Cannot read plugin.json: {e}"]

    # Load CLAUDE.md version
    claude_md = plugin_root / "CLAUDE.md"
    claude_version = None
    if claude_md.exists():
        text = claude_md.read_text(encoding="utf-8")
        m = VERSION_IN_CLAUDE_MD.search(text)
        if m:
            claude_version = m.group(1).strip()

    if claude_version is None:
        issues.append("CLAUDE.md: version line not found (expected: Current version: **X.Y.Z**)")
    elif claude_version != plugin_version:
        issues.append(f"Version mismatch: plugin.json={plugin_version!r} vs CLAUDE.md={claude_version!r}")

    # Check every SKILL.md with metadata.version
    for skill_md in sorted((plugin_root / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            continue
        meta = fm.get("metadata")
        if not isinstance(meta, dict):
            continue
        version = str(meta.get("version", "")) if meta else ""
        if version and not SEMVER_RE.match(version):
            rel = skill_md.relative_to(plugin_root).as_posix()
            issues.append(f"{rel}: metadata.version is not valid semver: {version!r}")

    return len(issues) == 0, issues


def main():
    plugin_root = Path(".").resolve()
    if not (plugin_root / ".claude-plugin" / "plugin.json").exists():
        print(f"ERROR: run from plugin root (no .claude-plugin/plugin.json found)", file=sys.stderr)
        sys.exit(1)

    # Load version for header
    try:
        plugin_version = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text())["version"]
    except Exception:
        plugin_version = "unknown"

    print(f"pre-package-check.py - skill-pipeline v{plugin_version}")
    print("-" * 50)

    all_passed = True

    # --- Step 1: Smoke test (structural checks) ---
    print("Running smoke-test.py --json ...")
    smoke_passed, smoke_msgs = run_smoke_test(plugin_root)
    if smoke_passed:
        print(ok("smoke-test: all 6 structural checks pass"))
    else:
        all_passed = False
        print(fail("smoke-test: violations found"))
        for msg in smoke_msgs:
            print(f"    {msg}")

    # --- Step 2: Version alignment ---
    va_passed, va_issues = check_version_alignment(plugin_root)
    if va_passed:
        print(ok("version alignment: plugin.json == CLAUDE.md, all SKILL.md semver valid"))
    else:
        all_passed = False
        print(fail("version alignment"))
        for issue in va_issues:
            print(f"    {issue}")

    print()
    if all_passed:
        print(colorize("Result: PASS - safe to package", "green"))
    else:
        print(colorize("Result: FAIL - fix violations before packaging", "red"))

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
