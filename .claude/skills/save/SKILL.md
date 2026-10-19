---
name: save
description: Save the student's work when class ends or they have to stop - refresh TRANSCRIPT.md, commit what they have as "Save work in progress", push, and say where they stopped and when the rest is due. Use when the student types /save, says class is ending, or says they have to go.
---

1. If they have given an answer you haven't written into `WRITEUP.md` yet, write it in first,
   under the writing rules in `CLAUDE.md`, and show the slot.
2. Run `python3 dump_transcript.py`. If it fails on their machine, say so and go on.
3. Stage the files by name (see "Commits" in `CLAUDE.md`). If anything is staged, commit it with
   the subject exactly `Save work in progress`. Then run `git push` (if it says there is no
   upstream branch, `git push -u origin HEAD`). If the push fails, say what the error means in
   one line, and ask them to show it to Shilad or post it in `#comp440-f26` before they leave.
4. If Part 5 is done, run the `checkpoint` skill instead of item 5.
5. Say, in three lines or fewer: the part and step they stopped at; that the rest is due 8:00am
   Thursday, October 22, with the form submitted once, when they finish; and that to go on, they
   open a terminal in this folder and start `claude`, which finds where they left off.
