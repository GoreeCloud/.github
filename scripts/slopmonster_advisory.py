#!/usr/bin/env python3
"""Summarize SlopMonster findings on tracked, public-facing prose.

Read-only. Return 0 for healthy or flagged text; 2 for scanner/runtime errors.
A calling GitHub Actions step uses continue-on-error so neither can block merges.
"""
from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Iterable

EXCLUDED_SEGMENTS = frozenset({
    ".git", ".github", ".slopmonster-upstream", ".goreecloud-advisory",
    "node_modules", "vendor", "third_party", "third-party", "dist", "build",
    "coverage", ".venv", "venv", "target", "generated", "site-packages",
})
MAX_FILES = 50
MAX_FILE_BYTES = 128 * 1024


def eligible(name: str) -> bool:
    """Limit scans to human-visible Markdown and selected HTML; never follow '..'."""
    path = Path(name)
    if not name or path.is_absolute() or ".." in path.parts:
        return False
    if any(segment in EXCLUDED_SEGMENTS for segment in path.parts):
        return False
    suffix = path.suffix.lower()
    return suffix == ".md" or (suffix == ".html" and (
        len(path.parts) == 1 and path.name.lower() == "index.html"
        or len(path.parts) > 1 and path.parts[0].lower() == "docs"
    ))


def git_names(root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, check=False, timeout=30,
    )
    if result.returncode:
        raise RuntimeError("git failed to enumerate review files")
    return [os.fsdecode(name) for name in result.stdout.split(b"\x00") if name]


def candidates(root: Path, base_sha: str, full_audit: bool) -> tuple[list[str], int, bool]:
    """Always review the README; otherwise restrict to a bounded tracked-file set.

    When the comparison base is absent/unreachable, fall back to tracked docs
    instead of silently reporting only README while skipping changed prose.
    """
    enumeration_failed = False
    names: set[str] = set()
    if (root / "README.md").is_file():
        names.add("README.md")
    valid_base = (re.fullmatch(r"[0-9a-fA-F]{40}", base_sha) is not None
                  and set(base_sha) != {"0"})
    if not full_audit and valid_base:
        try:
            all_names = git_names(root, "diff", "-z", "--name-only",
                                  "--diff-filter=ACMR", f"{base_sha}...HEAD")
        except (OSError, subprocess.TimeoutExpired, RuntimeError):
            full_audit = True
    else:
        full_audit = True
    if full_audit:
        try:
            all_names = git_names(root, "ls-files", "-z", "--", "*.md", "*.html")
        except (OSError, subprocess.TimeoutExpired, RuntimeError):
            all_names = []
            enumeration_failed = True
    names.update(name for name in all_names if eligible(name))
    ordered = sorted(names, key=lambda n: (n.lower() != "readme.md", n.lower()))
    return ordered[:MAX_FILES], max(0, len(ordered) - MAX_FILES), enumeration_failed


def scan(root: Path, checker: Path, names: Iterable[str]) -> tuple[list[tuple[str, str, str]], int]:
    rows: list[tuple[str, str, str]] = []
    skipped = 0
    for name in names:
        path = root / name
        if not eligible(name) or path.is_symlink():
            skipped += 1
            continue
        try:
            # Reject symlinked parent directories as well as symlinked files.
            if not path.resolve(strict=True).is_relative_to(root.resolve()):
                skipped += 1
                continue
            if not path.is_file():
                skipped += 1
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                skipped += 1
                continue
            result = subprocess.run(
                [sys.executable, str(checker), str(path)], cwd=root,
                capture_output=True, text=True, errors="replace", timeout=8,
                check=False,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            # SlopMonster returns 1 both for writing findings and for some
            # invalid inputs. Require its score line before calling a result
            # a finding or a clean scan; failures must not masquerade as either.
            score = re.search(
                r"(?m)^\s*score\s+([0-5])/5\s+(CLEAN|needs a cleanse)\s*$",
                result.stdout,
            )
            if "deslop: no visible copy to score" in output:
                state = "No visible prose"
            elif score and result.returncode == 0 and score.group(1) == "5" and score.group(2) == "CLEAN":
                state = "Clear"
            elif score and result.returncode == 1 and int(score.group(1)) < 5 and score.group(2) == "needs a cleanse":
                state = "Review suggested"
            else:
                state = "Scorer error"
        except FileNotFoundError:
            skipped += 1
            continue
        except (OSError, subprocess.TimeoutExpired) as exc:
            state, output = "Scorer error", str(exc)
        rows.append((name, state, output[:2500]))
    return rows, skipped


def format_summary(rows: list[tuple[str, str, str]], skipped: int, checker_present: bool,
                   enumeration_failed: bool = False) -> str:
    lines = [
        "## SlopMonster editorial advisory", "",
        "Writing-pattern suggestions only, not proof of AI authorship, accuracy, or security. "
        "No AI-model API or automatic rewriting is used.", "",
        "| File | Result |", "| --- | --- |",
    ]
    for name, state, _ in rows:
        safe_name = html.escape(name, quote=True).replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
        lines.append(f"| <code>{safe_name}</code> | {state} |")
    if not rows:
        lines.append("| — | No eligible prose files checked |")
    clear = sum(state == "Clear" for _, state, _ in rows)
    review = sum(state == "Review suggested" for _, state, _ in rows)
    errors = sum(state == "Scorer error" for _, state, _ in rows) + int(not checker_present)
    empty = sum(state == "No visible prose" for _, state, _ in rows)
    lines += ["", f"Scanned {len(rows)} file(s); clear: {clear}; review suggested: {review}; "
              f"no visible prose: {empty}; scanner errors: {errors}; skipped: {skipped}.", "",
              "This is advisory. No score can block a merge.", ""]
    if skipped:
        lines += ["**Partial coverage:** one or more files were skipped because of "
                  "repository safety limits or the bounded review size. Do not "
                  "interpret these results as a complete clean bill of health.", ""]
    if not checker_present:
        lines += ["**Scorer error:** pinned SlopMonster source was not found.", ""]
    if enumeration_failed:
        lines += ["**Incomplete scan:** Git could not enumerate tracked prose files. "
                  "Any README result is partial, not a clean repository result.", ""]
    if clear + review == 0:
        lines += ["**No verified prose scan:** no file produced a valid SlopMonster "
                  "writing score. This run cannot serve as successful pilot "
                  "acceptance evidence.", ""]
    for name, state, output in rows:
        if state != "Clear":
            lines += ["<details><summary>" + html.escape(name) + " — " + state + "</summary>",
                      "", "<pre>" + html.escape(output, quote=True) + "</pre>",
                      "", "</details>", ""]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--all", action="store_true", help="Audit all tracked eligible prose")
    parser.add_argument("--summary-file", type=Path)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    checker = args.checker.resolve()
    selected, dropped, enumeration_failed = candidates(root, args.base_sha, args.all)
    present = checker.is_file()
    rows, skipped = scan(root, checker, selected) if present else ([], 0)
    report = format_summary(rows, skipped + dropped, present, enumeration_failed)
    print(report)
    if args.summary_file:
        with args.summary_file.open("a", encoding="utf-8") as output:
            output.write(report)
    # Advisory writing findings are never blocking. A genuinely unavailable
    # review is different: it must not emit the success-only acceptance step.
    # In particular, all-empty, all-skipped and no-eligible-file runs are not
    # evidence that the pinned upstream scorer actually evaluated any prose.
    scored = sum(state in ("Clear", "Review suggested") for _, state, _ in rows)
    return 2 if (not present or enumeration_failed or scored == 0 or any(
        state == "Scorer error" for _, state, _ in rows)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
