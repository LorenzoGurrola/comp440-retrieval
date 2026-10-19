"""
Run every question in data/questions.jsonl with one method, save the answers, and print the
scores.

    uv run python evaluate.py --method tfidf
    uv run python evaluate.py --method embed

Each question has one right movie. For each question this records where that movie landed in the
method's list (1 is first; null when it isn't in the first 100) and the method's top 10. It writes
everything to results/tfidf.json or results/embed.json, which you commit with your work, and
site.py shows them. TF-IDF uses your settings from tfidf_settings.py.

The scores count how often the right movie came first and how often it was in the top 10, for the
written questions (and each kind of them) and for the real requests separately.

    uv run python evaluate.py --show w026
    uv run python evaluate.py --show w026 tot-train-220

--show runs nothing. It prints what the saved results say for each question id you give, the
same things the comparison site shows for it: the question, the right movie and its plot
summary, where each method put it, and each method's top 10.
"""

import argparse
import datetime
import json
import sys
import textwrap
import time

from retrieval import (CUT_OFF, DEPTH, KINDS, MODEL, NAMES, RESULTS, TOP, EmbedSearch, Problem,
                       TfidfSearch, describe, load_movies, load_questions, rank_words,
                       read_results, score_sentences, search, tfidf_settings)


def wrap(text, indent="  "):
    return textwrap.fill(" ".join(text.split()), width=96, initial_indent=indent,
                         subsequent_indent=indent)


def show(ids):
    """Print the saved results for each question id: what the site's page for it shows."""
    results = {key: r for key in NAMES if (r := read_results(key))}
    if not results:
        print("No question-bank results yet. Run: uv run python evaluate.py --method tfidf")
        return 1
    try:
        movies = {m["id"]: m for m in load_movies()}
    except Problem as e:
        print(e)
        return 1
    if "tfidf" in results:
        try:
            if results["tfidf"]["settings"] != tfidf_settings():
                print("Your TF-IDF settings changed after results/tfidf.json was made, so these "
                      "TF-IDF results are from the old settings. To update them: "
                      "uv run python evaluate.py --method tfidf")
                print()
        except Problem as e:
            print(e)
            print()
    by_id = {key: {q["id"]: q for q in r["questions"]} for key, r in results.items()}
    failed = False
    for qid in ids:
        runs = {key: by_id[key][qid] for key in results if qid in by_id[key]}
        if not runs:
            print(f'No question in the bank has the id "{qid}". Ids look like w026 or '
                  "tot-train-220.")
            print()
            failed = True
            continue
        q = next(iter(runs.values()))
        movie = movies.get(q["answer_id"])
        ranks = ", ".join(f"{NAMES[key] if n == 0 else NAMES[key].lower()} "
                          f"{rank_words(runs[key]['rank'])}" for n, key in enumerate(runs))
        print(f"{qid}: {KINDS.get(q['kind'], q['kind'])}")
        print(wrap(q["question"]))
        print()
        print(f"The right movie: {q['answer_title']}")
        print(f"Where the right movie landed: {ranks}.")
        if movie:
            print(wrap(f"Its plot summary: {movie['overview']}", indent=""))
        if "tfidf" in runs:
            shared = runs["tfidf"].get("answer_matched") or []
            print(f"The question's words in its plot summary: {', '.join(shared) or 'none'}.")
        if runs.get("embed", {}).get("cut_off"):
            print(CUT_OFF.format("this one"))
        for key, run in runs.items():
            print()
            print(f"{NAMES[key]}, top {TOP}:")
            for n, hit in enumerate(run["top10"], 1):
                words = f"   matched: {', '.join(hit['matched'])}" if "matched" in hit else ""
                right = "   [the right movie]" if hit["id"] == q["answer_id"] else ""
                print(f"{n:4}. {hit['score']:.3f}  {hit['title']}{right}{words}")
            if key == "tfidf" and len(run["top10"]) < TOP:
                shares = ("No plot summary shares" if not run["top10"]
                          else f"Only {len(run['top10'])} plot summaries share")
                print(f"      {shares} a word with this question.")
        print()
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--method", choices=["tfidf", "embed"],
                        help="which method to run the questions with")
    parser.add_argument("--show", nargs="+", metavar="ID",
                        help="run nothing; print the saved results for these question ids, "
                             "like w026")
    args = parser.parse_args()
    if args.show:
        return show(args.show)
    if not args.method:
        parser.error("say which method to run: --method tfidf or --method embed")
    try:
        movies, questions = load_movies(), load_questions()
        if args.method == "tfidf":
            settings = tfidf_settings()
            method = TfidfSearch(movies, settings)
            print(f"TF-IDF, with your settings: {describe(settings)}.")
        else:
            method = EmbedSearch(movies)
            settings = {"model": MODEL}
            print(f"Embedding {len(questions):,} questions. This can take a minute.")
    except Problem as e:
        print(e)
        return 1

    start = time.time()
    texts = [q["question"] for q in questions]
    found = search(method, texts, [q["answer_id"] for q in questions])
    rows = []
    for q, result in zip(questions, found):
        row = {k: q[k] for k in ["id", "kind", "question", "answer_id", "answer_title"]}
        row["rank"] = result["rank"]
        if "answer_matched" in result:
            row["answer_matched"] = result["answer_matched"]
        if args.method == "embed":
            row["cut_off"] = method.cut_off(q["question"])
        row["top10"] = result["top"]
        rows.append(row)

    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{args.method}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "method": args.method,
            "name": NAMES[args.method],
            "settings": settings,
            "made": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "movies": len(movies),
            "rank_note": f"rank is the right movie's place in the list, 1 for first, or null if "
                         f"it is not in the first {DEPTH}",
            "questions": rows,
        }, f, indent=1, ensure_ascii=False)
        f.write("\n")

    seconds = time.time() - start
    whole = round(seconds)
    took = "under a second" if seconds < 1 else f"{whole} second{'' if whole == 1 else 's'}"
    print(f"Ran {len(rows):,} questions against {len(movies):,} movies in {took}.")
    print()
    for line in score_sentences(NAMES[args.method], rows, per_kind=True):
        print(line)
    cut = []
    for label, group in [("written questions", [r for r in rows if r["kind"] != "real"]),
                         ("real requests", [r for r in rows if r["kind"] == "real"])]:
        n = sum(bool(r.get("cut_off")) for r in group)
        if n:
            cut.append(f"{n} of the {len(group):,} {label}")
    if cut:
        print()
        print(CUT_OFF.format(" and ".join(cut)))
    print()
    print(f"Saved every question's top {TOP} in {path.relative_to(RESULTS.parent)}. "
          "To look through them: uv run python site.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
