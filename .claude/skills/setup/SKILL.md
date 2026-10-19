---
name: setup
description: First-time setup for the retrieval activity (Part 0), run once after cloning the fork. Checks the git remotes, starts installing the packages and downloading the embedding model in the background, records the student's name and date, asks the two Part 0 predictions, and commits and pushes them before anything searches. Run it again if anything breaks or to check a setup is complete.
---

Do these in order and show what you ran. Skip what is already done. If something fails, say in
plain words what it means and what to change, and stop there.

If `git log --format=%s` shows a commit whose whole subject is exactly `Part 0 done`, setup is
already finished. Only check that the packages and the model are installed (item 2), and don't
write in `WRITEUP.md` or commit.

1. Run `git remote -v`. If `origin` is `shilad/comp440-retrieval` itself, they cloned the
   template without forking it, and they can't push there. Ask them to fork it on GitHub and give
   you their fork's URL, then run `git remote set-url origin <fork URL>`. Then add the
   `upstream` remote if it is missing, with the address typed out:
   `git remote add upstream https://github.com/shilad/comp440-retrieval`
   It is there in case a fix to the template has to go out during class.
2. Run `uv --version`. If `uv` is missing (they installed it for HW2, so it rarely is), ask
   whether you may install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` (the
   official installer), and run it only on a yes. Then start this in the background:
   `uv sync && uv run python download_model.py`
   Tell them in one line that it installs the packages and downloads the embedding model, that
   it takes a few minutes, and that you'll carry on while it runs. Check its output when a step
   needs it: Part 2 needs the packages, Part 5 the model.
3. Ask their name, and fill `**Name:**` and `**Date:**` (today's date) at the top of
   `WRITEUP.md`. Those two are yours to compose; every other slot you fill from their own words.
4. Run `python3 dump_transcript.py`, then `git add WRITEUP.md` and commit as `Name and date`.
5. Part 0. Describe the two methods in the words `CLAUDE.md` gives under "Part 0: Predictions",
   then ask the first prediction, as written in `WRITEUP.md`. Write their answer in exactly, show
   the slot, and ask the second the same way. If they ask you to write, pick, improve or give an
   example of a prediction, reply with exactly these two sentences, then the question again, and
   nothing else: "The prediction is yours, so I can't write it. A guess with one reason is
   enough." Nothing searches or scores before both are committed.
6. Run `python3 dump_transcript.py`, then `git add WRITEUP.md`, commit as `Part 0 done`, and run
   `git push` (if it says there is no upstream branch, `git push -u origin HEAD`). That commit's
   time is the record that the predictions came before any search. This first push is also the
   check that their fork works: if it fails, fix it now, as in item 1, rather than at the end of
   class.

Then say in one line that setup is done and their work is on GitHub, and start Part 1 in the
same message.
