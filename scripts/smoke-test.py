#!/usr/bin/env python3
"""
smoke-test.py — skill-pipeline plugin static correctness checker
Spec: ${CLAUDE_PLUGIN_ROOT}/specs/smoke-test.md v1.0.0

Run from the plugin root:  python scripts/smoke-test.py
Machine-readable output:   python scripts/smoke-test.py --json

Exit codes:
  0 — all checks pass
  1 — one or more checks failed (violations present)
  2 — script error (missing dependency, unparseable source, etc.)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

# ── Helpers ──────────────────────────────────────────────────────────────────

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9._-]+)?$")
PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}"

def resolve_plugin_path(path_str: str, plugin_root: Path) -> Path:
    return Path(path_str.replace(PLUGIN_ROOT_VAR, str(plugin_root)))

def is_tty() -> bool:
    return sys.stdout.isatty()

def colorize(text: str, color: str) -> str:
    if not is_tty():
        return text
    codes = {"green": "\033[32m", "red": "\033[31m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"

def pass_tag():
    return colorize("PASS", "green")

def fail_tag():
    return colorize("FAIL", "red")

def find_skill_mds(plugin_root: Path) -> list[Path]:
    return sorted((plugin_root / "skills").glob("*/SKILL.md"))

def find_reference_files(plugin_root: Path) -> list[Path]:
    refs = []
    for f in (plugin_root / "references").rglob("*"):
        if f.is_file() and f.suffix in (".md", ".yaml", ".html", ".txt"):
            refs.append(f)
    for skill_dir in (plugin_root / "skills").iterdir():
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for f in refs_dir.rglob("*"):
                if f.is_file():
                    refs.append(f)
    return refs

def extract_vars_from_path(path_str: str) -> set[str]:
    # Match {var} but NOT ${var} (the latter is an env-variable reference, not a substitution)
    return set(re.findall(r"(?<!\$)\{([^}]+)\}", path_str))

# ── Check 1: Canonical-paths registry resolves ────────────────────────────────

def check1_registry(plugin_root: Path, registry: dict) -> dict:
    violations = []
    entries = registry.get("entries", [])

    for entry in entries:
        eid = entry.get("id", "<no-id>")
        path_str = entry.get("path", "")
        etype = entry.get("type", "")
        substitutions = set(entry.get("substitutions") or [])

        if etype == "plugin-shared":
            resolved = resolve_plugin_path(path_str, plugin_root)
            if not resolved.exists():
                violations.append({
                    "id": eid,
                    "error": "plugin-shared file does not exist",
                    "detail": path_str,
                })
        elif etype in ("skill-artifact", "state-file"):
            if os.path.isabs(path_str):
                violations.append({"id": eid, "error": "absolute path in skill-artifact", "detail": path_str})
            if "\\" in path_str:
                violations.append({"id": eid, "error": "backslash in path", "detail": path_str})

        path_vars = extract_vars_from_path(path_str)
        if path_vars != substitutions:
            missing_subs = path_vars - substitutions
            extra_subs = substitutions - path_vars
            if missing_subs:
                violations.append({"id": eid, "error": f"vars in path not listed in substitutions: {missing_subs}", "detail": path_str})
            if extra_subs:
                violations.append({"id": eid, "error": f"substitutions listed but not in path: {extra_subs}", "detail": path_str})

    return {"id": "canonical-paths", "count": len(entries), "violations": violations}

# ── Check 2: SKILL.md frontmatter valid ──────────────────────────────────────

def parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    fm_text = text[3:end].strip()
    return yaml.safe_load(fm_text)

def check2_frontmatter(plugin_root: Path) -> dict:
    violations = []
    skill_mds = find_skill_mds(plugin_root)

    for skill_md in skill_mds:
        rel = skill_md.relative_to(plugin_root)
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            violations.append({"file": str(rel), "line": 1, "error": "frontmatter missing or unparseable"})
            continue
        if "name" not in fm:
            violations.append({"file": str(rel), "line": 1, "error": "missing required key: name"})
        if "description" not in fm:
            violations.append({"file": str(rel), "line": 1, "error": "missing required key: description"})
        if "metadata" in fm:
            meta = fm["metadata"] or {}
            version = str(meta.get("version", "")) if isinstance(meta, dict) else ""
            if not SEMVER_RE.match(version):
                violations.append({"file": str(rel), "line": 1, "error": f"metadata.version not valid semver: {version!r}"})

    return {"id": "frontmatter", "count": len(skill_mds), "violations": violations}

# ── Check 3: Citations resolve ────────────────────────────────────────────────

CITATION_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`'\">]+)")

def check3_citations(plugin_root: Path) -> dict:
    violations = []
    files_to_scan = find_skill_mds(plugin_root) + find_reference_files(plugin_root)

    for fpath in files_to_scan:
        rel = fpath.relative_to(plugin_root)
        try:
            text = fpath.read_text(encoding="utf-8")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for m in CITATION_RE.finditer(line):
                suffix = m.group(1)
                # Strip trailing markdown punctuation
                suffix = suffix.rstrip(".,;:)'\"")
                resolved = plugin_root / suffix
                if not resolved.exists():
                    violations.append({
                        "file": str(rel),
                        "line": lineno,
                        "error": "cite target does not exist",
                        "detail": f"{PLUGIN_ROOT_VAR}/{suffix}",
                    })

    return {"id": "citations-resolve", "violations": violations}

# ── Check 4: Forbidden-string scan ───────────────────────────────────────────

# These patterns indicate regression in any SKILL.md or reference file.
# Use backtick-context patterns to avoid flagging explanatory text.
FORBIDDEN = [
    (re.compile(r"design-doc-\["), "slug-suffix drift: design-doc-["),
    (re.compile(r"qa-template\.docx"), "wrong extension: qa-template.docx"),
    (re.compile(r"design-doc-\{skill-name\}"), "unresolved template form: design-doc-{skill-name}"),
    (re.compile(r'C:\\\\'), "absolute Windows path literal: C:\\"),
    # Only flag /sessions/ when used as an actual path with content (not just the prefix in explanatory text).
    # e.g. `/sessions/foo/bar.md` → fail; `(containing `/sessions/`)` → skip.
    (re.compile(r"`/sessions/[^`\s]+"), "absolute path citation starting with /sessions/"),
    (re.compile(r"~/\.claude/"), "absolute path: ~/.claude/"),
]

# Bare references/<filename.ext> not preceded by ${CLAUDE_PLUGIN_ROOT}/ or a dir component.
# Only look in single-line backtick spans to avoid false positives in prose.
BARE_REF_IN_BACKTICK = re.compile(r"`([^`\n]*?)references/([a-zA-Z0-9_\-]+\.[a-zA-Z]+)([^`\n]*?)`")
SAFE_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/references/")

# Convention-documentation files that intentionally show before/after examples of
# forbidden patterns — excluded from check 4 to avoid false positives.
CHECK4_CONVENTION_DOCS = {
    "references/pipeline-directory-map.md",
    "references/skill-writing-patterns.md",
    "skills/skill-calibrator/SKILL.md",  # documents the forbidden patterns as check definitions
}

def check4_forbidden(plugin_root: Path) -> dict:
    violations = []
    files_to_scan = find_skill_mds(plugin_root) + find_reference_files(plugin_root)
    specs_dir = plugin_root / "specs"

    for fpath in files_to_scan:
        # Exclude spec files (they explain the forbidden patterns)
        if fpath.is_relative_to(specs_dir):
            continue
        rel = fpath.relative_to(plugin_root)
        rel_posix = rel.as_posix()
        # Exclude convention-documentation files that show before/after examples by design
        if rel_posix in CHECK4_CONVENTION_DOCS:
            continue
        try:
            text = fpath.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            for pat, label in FORBIDDEN:
                if pat.search(line):
                    violations.append({"file": rel_posix, "line": lineno, "error": label, "detail": line.strip()[:120]})

        # Scan for bare references/<filename> in single-line backtick spans
        for m in BARE_REF_IN_BACKTICK.finditer(text):
            prefix = m.group(1)  # text before references/ inside the backtick span
            # Skip if span contains ${CLAUDE_PLUGIN_ROOT}/references (correct Form A)
            if SAFE_REF_RE.search(m.group(0)):
                continue
            # Skip if references/ is preceded by a directory component making it Form B
            # e.g. `handoff-sesh/references/foo.md` — prefix ends with "/"
            if prefix.endswith("/"):
                continue
            lineno = text[:m.start()].count("\n") + 1
            violations.append({
                "file": rel_posix,
                "line": lineno,
                "error": "bare references/<filename> missing ${CLAUDE_PLUGIN_ROOT} prefix",
                "detail": m.group(0)[:80],
            })

    return {"id": "forbidden-strings", "violations": violations}

# ── Check 5: Registry citation discipline ────────────────────────────────────

REGISTRY_SECTION_RE = re.compile(r"^## Canonical Paths Registry", re.MULTILINE)
REGISTRY_ID_RE = re.compile(r"-\s+`([a-z][a-z0-9\-]*)`")

def check5_registry_discipline(plugin_root: Path, registry: dict) -> dict:
    violations = []
    registry_ids = {e["id"] for e in registry.get("entries", [])}
    skill_mds = find_skill_mds(plugin_root)

    for skill_md in skill_mds:
        rel = skill_md.relative_to(plugin_root)
        text = skill_md.read_text(encoding="utf-8")
        m = REGISTRY_SECTION_RE.search(text)
        if not m:
            continue
        # Extract the section content until next ##
        section_start = m.end()
        next_section = re.search(r"^##", text[section_start:], re.MULTILINE)
        section_text = text[section_start: section_start + next_section.start()] if next_section else text[section_start:]

        listed_ids = REGISTRY_ID_RE.findall(section_text)
        for rid in listed_ids:
            if rid not in registry_ids:
                lineno = text[:m.start()].count("\n") + 1
                violations.append({
                    "file": str(rel),
                    "line": lineno,
                    "error": f"registry id not found in canonical-paths.yaml: {rid!r}",
                    "detail": f"listed in ## Canonical Paths Registry section",
                })

    return {"id": "registry-discipline", "violations": violations}

# ── Check 6: Plugin manifest sanity ──────────────────────────────────────────

VERSION_IN_CLAUDE_MD = re.compile(r"Current version:\s+\*\*([0-9]+\.[0-9]+\.[0-9]+[^\*]*)\*\*")

def check6_manifest(plugin_root: Path) -> dict:
    violations = []
    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"

    if not manifest_path.exists():
        return {"id": "manifest", "violations": [{"file": ".claude-plugin/plugin.json", "line": 0, "error": "file does not exist"}]}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"id": "manifest", "violations": [{"file": ".claude-plugin/plugin.json", "line": 0, "error": f"JSON parse error: {e}"}]}

    plugin_version = manifest.get("version", "")
    if not SEMVER_RE.match(plugin_version):
        violations.append({"file": ".claude-plugin/plugin.json", "line": 0, "error": f"version not valid semver: {plugin_version!r}"})

    # Check CLAUDE.md version matches
    claude_md = plugin_root / "CLAUDE.md"
    if claude_md.exists():
        text = claude_md.read_text(encoding="utf-8")
        m = VERSION_IN_CLAUDE_MD.search(text)
        if m:
            claude_version = m.group(1).strip()
            if claude_version != plugin_version:
                violations.append({
                    "file": "CLAUDE.md",
                    "line": text[:m.start()].count("\n") + 1,
                    "error": f"version mismatch: plugin.json={plugin_version!r}, CLAUDE.md={claude_version!r}",
                })
        else:
            violations.append({"file": "CLAUDE.md", "line": 0, "error": "could not find version line matching 'Current version: **X.Y.Z**'"})

    return {"id": "manifest", "plugin_version": plugin_version, "violations": violations}

# ── Runner ────────────────────────────────────────────────────────────────────

def load_registry(plugin_root: Path) -> dict:
    registry_path = plugin_root / "references" / "canonical-paths.yaml"
    if not registry_path.exists():
        print(f"ERROR: registry not found at {registry_path}", file=sys.stderr)
        sys.exit(2)
    try:
        return yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"ERROR: failed to parse canonical-paths.yaml: {e}", file=sys.stderr)
        sys.exit(2)

def run_all_checks(plugin_root: Path, registry: dict) -> list[dict]:
    results = []
    results.append(check1_registry(plugin_root, registry))
    results.append(check2_frontmatter(plugin_root))
    results.append(check3_citations(plugin_root))
    results.append(check4_forbidden(plugin_root))
    results.append(check5_registry_discipline(plugin_root, registry))
    results.append(check6_manifest(plugin_root))
    return results

def check_status(result: dict) -> str:
    return "pass" if not result["violations"] else "fail"

def print_human(plugin_root: Path, registry: dict, results: list[dict], plugin_version: str):
    print(f"smoke-test.py - skill-pipeline v{plugin_version}")
    print("-" * 45)
    labels = [
        "Canonical-paths registry resolves",
        "SKILL.md frontmatter valid",
        "Citations resolve",
        "Forbidden-string scan",
        "Registry citation discipline",
        "Plugin manifest sanity",
    ]
    total_violations = 0
    fail_count = 0
    for i, (result, label) in enumerate(zip(results, labels), 1):
        status = check_status(result)
        count = result.get("count", len(result["violations"]))
        count_str = f"({count} {'entries' if i == 1 else 'files' if i == 2 else 'violations' if status == 'fail' else 'ok'})" if count else ""
        tag = pass_tag() if status == "pass" else fail_tag()
        print(f"[{i}/6] {label:<34} {tag} {count_str}")
        if status == "fail":
            fail_count += 1
            for v in result["violations"]:
                total_violations += 1
                loc = f"{v.get('file', '')}:{v.get('line', '')}" if v.get("file") else ""
                print(f"          {loc}")
                print(f"            error: {v['error']}")
                if "detail" in v:
                    print(f"            detail: {v['detail']}")
    print()
    if fail_count == 0:
        print(colorize(f"Result: PASS", "green"))
    else:
        print(colorize(f"Result: FAIL ({total_violations} violation(s) across {fail_count} check(s))", "red"))

def print_json(results: list[dict], plugin_version: str):
    output = {
        "version": plugin_version,
        "checks": [{"id": r["id"], "status": check_status(r), "violations": r["violations"]} for r in results],
        "overall": "pass" if all(check_status(r) == "pass" for r in results) else "fail",
    }
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description="smoke-test.py — skill-pipeline static checker")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON output")
    parser.add_argument("--root", default=".", help="plugin root directory (default: current directory)")
    args = parser.parse_args()

    plugin_root = Path(args.root).resolve()
    if not (plugin_root / ".claude-plugin" / "plugin.json").exists():
        print(f"ERROR: not a plugin root (no .claude-plugin/plugin.json): {plugin_root}", file=sys.stderr)
        sys.exit(2)

    registry = load_registry(plugin_root)
    results = run_all_checks(plugin_root, registry)

    manifest_path = plugin_root / ".claude-plugin" / "plugin.json"
    try:
        plugin_version = json.loads(manifest_path.read_text(encoding="utf-8")).get("version", "unknown")
    except Exception:
        plugin_version = "unknown"

    if args.json:
        print_json(results, plugin_version)
    else:
        print_human(plugin_root, registry, results, plugin_version)

    overall_pass = all(check_status(r) == "pass" for r in results)
    sys.exit(0 if overall_pass else 1)

if __name__ == "__main__":
    main()
