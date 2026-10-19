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
"""

import argparse
import datetime
import json
import sys
import time

from retrieval import (CUT_OFF, DEPTH, MODEL, NAMES, RESULTS, TOP, EmbedSearch, Problem,
                       TfidfSearch, describe, load_movies, load_questions, score_sentences,
                       search, tfidf_settings)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--method", choices=["tfidf", "embed"], required=True,
                        help="which method to run the questions with")
    args = parser.parse_args()
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
    took = "under a second" if seconds < 1 else f"{seconds:.0f} seconds"
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
