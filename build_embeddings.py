"""
Rebuild data/embeddings.npz: the embedding of every plot summary in data/movies.jsonl.

    uv run python build_embeddings.py

You don't need to run this. The file ships with the repository, so that you only embed your
questions, not 4,000 plot summaries. Shilad reruns it whenever data/movies.jsonl changes.

It embeds each plot summary on its own, without the title: with the title added, the model leaned
toward movies whose titles share a word with the question. The file holds two arrays: "ids", the
movies' TMDB ids in the order of data/movies.jsonl, and "vectors", one row of 384 numbers per
movie.
"""

import sys
import time

import numpy as np

from retrieval import VECTORS, Problem, embed, load_model, load_movies


def main():
    try:
        movies = load_movies()
    except Problem as e:
        print(e)
        return 1
    model = load_model(download=True)
    start = time.time()
    # Embedding texts of similar length together saves time, so sort by length, then put the
    # rows back in the order of data/movies.jsonl.
    order = np.argsort([len(m["overview"]) for m in movies], kind="stable")
    vectors = np.empty((len(movies), 384), dtype=np.float32)
    vectors[order] = embed(model, [movies[i]["overview"] for i in order])
    ids = np.array([m["id"] for m in movies])
    np.savez(VECTORS, ids=ids, vectors=vectors)
    print(f"Wrote data/embeddings.npz: {len(movies):,} plot summaries, "
          f"384 numbers each, in {time.time() - start:.0f} seconds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
