"""
The 15 words with the highest TF-IDF weight in one movie's plot summary, with your settings from
tfidf_settings.py.

    uv run python top_terms.py "Groundhog Day"
    uv run python top_terms.py "Groundhog Day (1993)"
    uv run python top_terms.py "the matrix"

The title can be the whole title or part of it, in any case. "The" can go first, as people say
it, even though the collection writes "Matrix, The (1999)". If more than one movie matches, it
lists them so that you can pick one.
"""

import argparse
import difflib
import re
import sys
from collections import Counter

import numpy as np

from retrieval import Problem, TfidfSearch, describe, load_movies, tfidf_settings

SHOWN = 15


def plain(title):
    """'Matrix, The (1999)' -> 'the matrix': lowercase, "The" first, no year or punctuation."""
    title = re.sub(r"\s*\(\d{4}\)\s*$", "", title)
    title = re.sub(r"^(.*), (The|A|An)$", r"\2 \1", title)
    return " ".join(re.findall(r"\w+", title.lower()))


def find(movies, text):
    """The movies whose title matches the text: the exact title if one has it, then the titles
    equal to it without the year, then the titles that contain it."""
    exact = [m for m in movies if m["title"].lower() == text.strip().lower()]
    if exact:
        return exact
    wanted = plain(text)
    same = [m for m in movies if plain(m["title"]) == wanted]
    if same:
        return same
    return [m for m in movies if wanted and wanted in plain(m["title"])]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("title", help="all or part of a movie title")
    args = parser.parse_args()
    try:
        movies = load_movies()
        settings = tfidf_settings()
        tfidf = TfidfSearch(movies, settings)
    except Problem as e:
        print(e)
        return 1

    found = find(movies, args.title)
    if not found:
        print(f'No movie title matches "{args.title}".')
        close = difflib.get_close_matches(plain(args.title), [plain(m["title"]) for m in movies], n=5)
        names = [m["title"] for m in movies if plain(m["title"]) in close]
        if names:
            print("Close ones: " + "; ".join(names[:5]))
        return 1
    if len(found) > 1:
        print(f'{len(found)} movies match "{args.title}". Run it again with the whole title of one:')
        for m in found[:20]:
            print(f"  {m['title']}")
        if len(found) > 20:
            print(f"  and {len(found) - 20} more")
        return 0

    movie = found[0]
    i = movies.index(movie)
    row = tfidf.matrix[i]
    order = np.argsort(-row.data, kind="stable")[:SHOWN]
    counts = Counter(tfidf.vectorizer.build_analyzer()(movie["overview"]))
    in_movies = np.bincount(tfidf.matrix.indices, minlength=len(tfidf.words))

    print(f"{movie['title']}: the {len(order)} words with the highest TF-IDF weight in its plot summary.")
    print()
    print(f"     {'word':<18}{'weight':>7}{'count here':>12}{'movies':>8}")
    for n, j in enumerate(order, 1):
        word = str(tfidf.words[row.indices[j]])
        print(f"{n:3}. {word:<18}{row.data[j]:7.3f}{counts[word]:12}{in_movies[row.indices[j]]:8,}")
    print()
    print(f"count here: how many times the word is in this plot summary. movies: how many of the "
          f"{len(movies):,} plot summaries have it.")
    print()
    print(f"The plot summary: {movie['overview']}")
    print()
    print(f"Your settings: {describe(settings)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
