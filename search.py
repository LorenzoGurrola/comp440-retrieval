"""
The top 10 movies for a question of yours.

    uv run python search.py "a guy keeps reliving the same day"
    uv run python search.py "a guy keeps reliving the same day" --method embed
    uv run python search.py "a guy keeps reliving the same day" --method both

TF-IDF is the default, with your settings from tfidf_settings.py. For each TF-IDF result it lists
the words of your question that are also in that movie's plot summary, the word that adds the
most to the score first. The score is the cosine similarity of the question's vector and the plot
summary's vector: 1 is the most alike, and for TF-IDF, 0 means no word in common.
"""

import argparse
import sys

from retrieval import TOP, EmbedSearch, Problem, TfidfSearch, load_movies, search, tfidf_settings


def show(method, question):
    """Print one method's top 10 for the question."""
    hits = search(method, [question])[0]["top"]
    print(f"{method.name}, top {TOP}:")
    for n, hit in enumerate(hits, 1):
        words = f"   matched: {', '.join(hit['matched'])}" if "matched" in hit else ""
        print(f"{n:4}. {hit['score']:.3f}  {hit['title']}{words}")
    if method.key == "tfidf":
        if len(hits) < TOP:
            shares = "No plot summary shares" if not hits else f"Only {len(hits)} plot summaries share"
            print(f"      {shares} a word with your question.")
        ignored = method.ignored(question)
        if ignored:
            more = f" and {len(ignored) - 15} more" if len(ignored) > 15 else ""
            print(f"      Not in TF-IDF's vocabulary, so ignored: {', '.join(ignored[:15])}{more}")
    if method.key == "embed" and method.cut_off(question):
        print("      The model reads only the first 256 word pieces of a question (about 200 "
              "words), so it ignored the end of this one.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("question", help="what you are looking for, in quotes")
    parser.add_argument("--method", choices=["tfidf", "embed", "both"], default="tfidf",
                        help="which method to search with (default: tfidf)")
    args = parser.parse_args()
    question = " ".join(args.question.split())
    if not question:
        print("The question is empty. Put it in quotes after search.py.")
        return 1

    words = question.split()
    print(f"Question: {question if len(words) <= 25 else ' '.join(words[:25]) + ' ...'}")
    print()
    failed = False
    movies = None
    for key in ["tfidf", "embed"] if args.method == "both" else [args.method]:
        try:
            movies = movies or load_movies()
            method = TfidfSearch(movies, tfidf_settings()) if key == "tfidf" else EmbedSearch(movies)
            show(method, question)
        except Problem as e:
            print(e)
            failed = True
        print()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
