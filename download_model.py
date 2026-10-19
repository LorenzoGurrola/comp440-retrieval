"""
Download the embedding model and check it against the plot-summary vectors that ship with this
repository.

    uv run python download_model.py

Setup runs this in the background. The model, all-MiniLM-L6-v2 (about 90 MB), goes into .model/
in this folder, which git ignores. Once it is there, running this again takes a few seconds and
needs no internet.

The check embeds five plot summaries and compares them with their rows in data/embeddings.npz.
They should match, because the shipped vectors were made with the same model.
"""

import contextlib
import io
import sys

import numpy as np

from retrieval import Problem, embed, load_model, load_movies, shipped_vectors

CHECKED = 5


def main():
    try:
        # Keep the download's progress bars and warnings out of the output; failures are
        # reported below in one line.
        with contextlib.redirect_stderr(io.StringIO()):
            model = load_model(download=True)
    except Exception as e:
        reason = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
        print(f"The embedding model did not download ({reason}). Check your internet "
              "connection, then run uv run python download_model.py again.")
        return 1
    try:
        movies = load_movies()
        shipped = shipped_vectors(movies)
    except Problem as e:
        print(f"The embedding model downloaded, but it couldn't be checked: {e}")
        return 1
    rows = np.linspace(0, len(movies) - 1, CHECKED).astype(int)
    fresh = embed(model, [movies[i]["overview"] for i in rows])
    similarity = (fresh * shipped[rows]).sum(axis=1)
    if similarity.min() < 0.999:
        off = int((similarity < 0.999).sum())
        print(f"The embedding model downloaded, but its numbers for {off} of {CHECKED} test movies "
              f"differ from the shipped ones (lowest cosine similarity {similarity.min():.3f}). "
              "Embedding search won't be right. Tell Shilad.")
        return 1
    print(f"The embedding model is ready: it matches the shipped vectors for {CHECKED} test movies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
