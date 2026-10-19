"""
The check Claude Code runs before a Bash command Claude runs that mentions a commit or one of the
activity's commands (.claude/settings.json, a PreToolUse hook). Two rules:

1. Predictions come first. top_terms.py, search.py, evaluate.py and site.py are stopped until a
   commit whose whole subject is "Part 0 done" exists, because a prediction made after seeing
   results is not a prediction.
2. A part is done when its slots are filled. A "Part N done" commit is stopped while a slot
   under "## Part N" in WRITEUP.md still reads XXXX, and the slots are named.

Exit code 2 stops the command and shows Claude the message; exit code 0 lets it run. It reads
WRITEUP.md with run_all.py's slot reader, so the two always agree on what a blank slot is. It
uses only Python's standard library and runs with python3, so it works before setup installs
the packages. Nothing in this file changes.
"""

import json
import re
import sys

from run_all import REPO, WRITEUP, blank_slots, subjects

# A run of one of the four scripts (reading one, as with cat, is fine).
SCRIPTS = re.compile(r"\b(?:python3?|uv run)\b[^;&|\n]*\b(top_terms|search|evaluate|site)\.py\b")
GIT_COMMIT = re.compile(r"\bgit\b[^;&|\n]*\bcommit\b")
PART_DONE = re.compile(r"\bPart (\d+) done\b")


def stop(lines):
    print("\n".join(lines), file=sys.stderr)
    return 2


def main():
    # The instructor's copy sits next to planning/ in comp440-retrieval-sim; nothing is guarded there.
    if (REPO.parent / "planning").is_dir():
        return 0
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    except (ValueError, AttributeError):
        return 0

    if SCRIPTS.search(command) and "Part 0 done" not in {s for _, s in subjects()}:
        return stop([
            "Not run: nothing searches or scores before the Part 0 predictions are committed.",
            "Ask for the two Part 0 predictions, write them into WRITEUP.md, and commit them as "
            "\"Part 0 done\" (the setup skill does this). Then run the command again.",
        ])

    if GIT_COMMIT.search(command):
        part = PART_DONE.search(command)
        if part and WRITEUP.exists():
            n = int(part.group(1))
            labels = blank_slots().get(n, [])
            if labels:
                return stop(
                    [f"Not committed: these Part {n} slots in WRITEUP.md still read XXXX:"]
                    + [f"  - {label}" for label in labels]
                    + ["Ask the student for each missing answer, write it in, read WRITEUP.md "
                       "back, then commit again."])
    return 0


if __name__ == "__main__":
    sys.exit(main())
