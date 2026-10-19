"""
Check the activity and say what is still missing.

    uv run python run_all.py

It checks five things, in well under a minute once setup is done:

1. The commands run: a tiny TF-IDF search and one movie's top terms, with your settings. Their
   output is kept back. Each gets one line: "ran" and how long it took, or "stopped:" and the
   last line it printed, which says why.
2. The predictions came first: a commit whose subject is "Part 0 done" exists. It also says
   whether that commit came before the first commit of anything in results/.
3. Both question-bank runs exist: results/tfidf.json (Part 4) and results/embed.json (Part 5).
4. No slot in WRITEUP.md still reads XXXX: the name and date, and every "### ..." slot under
   each "## Part N" heading.
5. Your work is saved: WRITEUP.md, tfidf_settings.py, results/ and TRANSCRIPT.md are committed,
   and no commit is waiting to be pushed. It doesn't contact GitHub; it compares with the last
   push this laptop knows about.

The exit code is 0 when nothing is missing and everything is pushed, and 1 otherwise. Presence
and form only: nothing here says whether an answer is right. It uses only Python's standard
library, so guard.py can borrow its slot reader before the packages are installed. Nothing in
this file changes.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
WRITEUP = REPO / "WRITEUP.md"
MOVIES = REPO / "data" / "movies.jsonl"
FORM = "https://forms.gle/mgKcnqzTGxNaGvteA"
MARKER = "XXXX"

# The files the activity hands in. Claude stages exactly these, by name.
HANDED_IN = ["WRITEUP.md", "tfidf_settings.py", "results", "TRANSCRIPT.md"]

# The question-bank runs: file -> how to make it.
RESULTS = {
    "results/tfidf.json": "Part 4 writes it with `uv run python evaluate.py --method tfidf`",
    "results/embed.json": "Part 5 writes it with `uv run python evaluate.py --method embed`",
}

# Commands that must exist, beyond the two run below.
OTHER_SCRIPTS = ["download_model.py", "evaluate.py", "site.py", "tfidf_settings.py"]

TINY_QUESTION = "a man and his dog"
PART = re.compile(r"^## Part (\d+)")
SLOT = re.compile(r"^### (.+)$")
BOLD = re.compile(r"^\*\*(.+?):\*\*(.*)$")
BLANK = re.compile(re.escape(MARKER) + r"\s*(\(.*\))?", re.S)


def slots(text=None):
    """Every slot in WRITEUP.md, in order, as [part, label, answer].

    Two shapes, the same ones the course's simulator reads: a "**Label:** answer" line (the name
    and date, above the parts, have part None), and a "### Label" heading whose answer is the
    first paragraph below it. A slot is blank when its answer is empty, XXXX, or XXXX followed by
    a note in brackets."""
    if text is None:
        text = WRITEUP.read_text(encoding="utf-8")
    lines = text.splitlines()
    found, part, inside = [], None, False
    for i, line in enumerate(lines):
        heading = PART.match(line)
        if heading:
            part, inside = int(heading.group(1)), False
            continue
        slot = SLOT.match(line)
        if slot:
            below = []
            for nxt in lines[i + 1:]:
                if nxt.lstrip().startswith("#"):
                    break
                if nxt.strip():
                    below.append(nxt.strip())
                elif below:
                    break
            found.append([part, slot.group(1).strip(), " ".join(below)])
            inside = True
            continue
        if line.lstrip().startswith("#"):
            inside = False
        bold = BOLD.match(line.strip())
        if bold and not inside:
            found.append([part, bold.group(1).strip(), bold.group(2).strip()])
    return found


def is_blank(answer):
    return not answer or bool(BLANK.fullmatch(answer))


def blank_slots():
    """Part number (None for the name and date) -> the labels of its slots still blank."""
    blank = {}
    for part, label, answer in slots():
        if is_blank(answer):
            blank.setdefault(part, []).append(label)
    return blank


def git(*args):
    """A git command's output, or None if it failed."""
    p = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)
    return p.stdout if p.returncode == 0 else None


def subjects():
    """Every commit subject on this branch, oldest first, as (hash, subject)."""
    out = git("log", "--reverse", "--format=%H%x09%s") or ""
    return [tuple(line.split("\t", 1)) for line in out.splitlines() if "\t" in line]


def run(args):
    """Run one of the activity's scripts with this Python, output kept back. Returns its exit
    code, its last line of output and the seconds it took."""
    start = time.perf_counter()
    try:
        p = subprocess.run([sys.executable, *args], cwd=REPO, capture_output=True, text=True,
                           timeout=120)
        code, out = p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        code, out = 1, "it took longer than two minutes"
    last = next((line.strip() for line in reversed(out.splitlines()) if line.strip()), "")
    return code, last, time.perf_counter() - start


def first_title():
    """The title of the first movie in data/movies.jsonl, or None."""
    try:
        with open(MOVIES, encoding="utf-8") as f:
            return json.loads(f.readline()).get("title")
    except (OSError, ValueError, AttributeError):
        return None


def check_commands(missing):
    print("== The commands ==")
    for script in ["search.py", "top_terms.py", *OTHER_SCRIPTS]:
        if not (REPO / script).exists():
            missing.append(f"{script} is not in the repository. Tell Shilad.")
    checks = [("search.py (a tiny TF-IDF search)", ["search.py", TINY_QUESTION, "--method", "tfidf"])]
    title = first_title()
    if title:
        checks.append(("top_terms.py (one movie)", ["top_terms.py", title]))
    else:
        missing.append("data/movies.jsonl is missing or unreadable, so top_terms.py was not run.")
    for name, args in checks:
        if not (REPO / args[0]).exists():
            print(f"  {name}: not run, the script is missing")
            continue
        code, last, seconds = run(args)
        if code == 0:
            print(f"  {name}: ran, {seconds:.1f} s")
        else:
            print(f"  {name}: stopped: {last or f'exit code {code}'}")
            missing.append(f"{name} stopped. Ask Claude to run {args[0]} and show you why.")


def check_order(missing, notes):
    log = subjects()
    done = [i for i, (_, s) in enumerate(log) if s == "Part 0 done"]
    if not done:
        missing.append("No commit \"Part 0 done\" yet. It is made once your two predictions are in.")
        return
    touched = git("log", "--reverse", "--format=%H", "--", "results") or ""
    first = touched.split()[0] if touched.split() else None
    hashes = [h for h, _ in log]
    if first and first in hashes and hashes.index(first) < done[0]:
        notes.append("results/ was committed before \"Part 0 done\": the predictions came after a "
                     "question-bank run. This can't be changed now; it is only noted.")


def check_results(missing):
    for path, how in RESULTS.items():
        f = REPO / path
        if not f.exists():
            missing.append(f"{path} is not there yet. {how}.")
            continue
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            missing.append(f"{path} is not readable JSON. {how}; run that again.")
        if git("check-ignore", "-q", path) is not None:   # exit 0 means git ignores it
            missing.append(f"{path} is ignored by .gitignore, so it can't be handed in. Tell Shilad.")


def check_slots(missing):
    if not WRITEUP.exists():
        missing.append("WRITEUP.md is missing.")
        return
    for part, labels in blank_slots().items():
        where = "Name and date" if part is None else f"Part {part}"
        for label in labels:
            missing.append(f"{where}: still {MARKER}: {label}")


def check_saved():
    """Lines saying what is not yet committed or pushed; empty when everything is saved."""
    lines = []
    status = git("status", "--porcelain", "--", *HANDED_IN)
    if status is None:
        return ["This folder is not a git repository, so nothing here is saved on GitHub."]
    changed = sorted({line[3:].strip() for line in status.splitlines() if line.strip()})
    if changed:
        lines.append(f"Not committed yet: {', '.join(changed)}")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if ahead is None:
        branch = (git("rev-parse", "--abbrev-ref", "HEAD") or "main").strip()
        ahead = git("rev-list", "--count", f"origin/{branch}..HEAD")
    if ahead is None:
        lines.append("Not pushed yet, as far as this laptop knows: run git push.")
    elif int(ahead.strip() or 0):
        n = int(ahead.strip())
        lines.append(f"{n} commit{'' if n == 1 else 's'} not pushed yet: run git push.")
    return lines


def main():
    missing, notes = [], []
    check_commands(missing)
    check_order(missing, notes)
    check_results(missing)
    check_slots(missing)

    print("\n== What is missing ==")
    for line in missing:
        print(f"  {line}")
    if not missing:
        print("  Nothing.")
    for line in notes:
        print(f"  Note: {line}")

    print("\n== Saved on GitHub ==")
    unsaved = check_saved()
    for line in unsaved:
        print(f"  {line}")
    if not unsaved:
        print("  Everything is committed and pushed.")

    n = len(missing)
    print(f"\n{n} thing{'' if n == 1 else 's'} missing.")
    if not missing:
        first = "Your work is pushed, so submit" if not unsaved else "Commit and push your work, then submit"
        print(f"{first} the Work Submission Form, {FORM}: choose \"activity\" and paste "
              "your repository's GitHub URL into the textbox.")
    return 0 if not missing and not unsaved else 1


if __name__ == "__main__":
    sys.exit(main())
