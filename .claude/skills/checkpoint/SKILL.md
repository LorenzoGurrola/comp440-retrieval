---
name: checkpoint
description: The end of the retrieval activity. Run it once, after Part 5 is committed, or earlier if the student asks what is missing. Runs run_all.py, names the slots still blank, refreshes TRANSCRIPT.md, commits and pushes, gives the submission form, and says the finish line once the student says they have submitted.
---

Run it once, after `Part 5 done`. If the student asks earlier what is missing, do steps 1 and 2
only, and then go back to the current step.

1. Run `uv run python run_all.py` and paste its output in full: every line, copied into your
   reply. Don't say whether any number looks right.
2. Name, one line each, every slot it lists as still `XXXX`, and ask what each needs; don't
   suggest wording. Fill each from their answer under the writing rules in `CLAUDE.md`. If
   something else is missing (a results file, a command that stopped), say what it means and fix
   it, then run `uv run python run_all.py` again and paste it.
3. Run `python3 dump_transcript.py` and paste its last line. It says how many sessions are in
   `TRANSCRIPT.md` and whether this session is one of them. If the script fails on their
   machine, say so and go on: it costs them nothing.
4. If anything handed in is not committed, stage it by name (see "Commits" in `CLAUDE.md`) and
   commit it as `Save work in progress`. Run `git push`. The "Saved on GitHub" part of
   `run_all.py`'s output should now hold nothing; if a push failed, say what the error means.
5. Give them the form in these words: complete the
   [Work Submission Form](https://forms.gle/mgKcnqzTGxNaGvteA), choose "Activity submission",
   and in its box write "Representing and Retrieving Knowledge" and your repository's GitHub
   URL. Give them that URL, from `git remote get-url origin`, written as an https://github.com/
   address. Ask whether they have submitted it, and wait.
6. When they say they have, run `python3 dump_transcript.py` once more and `git push`. Only then
   say the finish line, `YOU ARE FINISHED!`, in bold on a line of its own. Never say it before
   they tell you they have submitted.

Nothing here is a judgment about the work. Presence and form only.
