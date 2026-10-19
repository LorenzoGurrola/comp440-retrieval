"""
The code the activity's commands share: the movies and questions, the two search methods, and the
score sentences. You don't run this file; top_terms.py, search.py, evaluate.py and site.py
import it.

    TF-IDF      scikit-learn's TfidfVectorizer, with your choices from tfidf_settings.py.
    Embeddings  the all-MiniLM-L6-v2 model, run by the fastembed package. The plot summaries'
                vectors ship in data/embeddings.npz, so only your questions are embedded here.

Both methods score a question against every plot summary with the cosine similarity of their
vectors, and list the movies from the highest score down.
"""

import json
import runpy
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent
MOVIES = REPO / "data" / "movies.jsonl"
QUESTIONS = REPO / "data" / "questions.jsonl"
VECTORS = REPO / "data" / "embeddings.npz"
SETTINGS_FILE = REPO / "tfidf_settings.py"
RESULTS = REPO / "results"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_DIR = REPO / ".model"  # download_model.py puts the model here; .gitignore keeps it out of git

TOP = 10     # how many movies each method shows
DEPTH = 100  # how far down its list evaluate.py looks for the right movie
NAMES = {"tfidf": "TF-IDF", "embed": "Embeddings"}
KINDS = {
    "detail": "Written question that names a character, place or thing",
    "reworded": "Written question that tells the plot in other words",
    "vague": "Written question, the way you'd describe the movie to a friend",
    "real": "Real request from someone trying to name a half-remembered movie",
}


class Problem(Exception):
    """Something went wrong that the student can do something about. The message says what."""


def read_jsonl(path):
    if not path.exists():
        raise Problem(f"{path.relative_to(REPO)} is missing. Tell Shilad.")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_movies():
    return read_jsonl(MOVIES)


def load_questions():
    return read_jsonl(QUESTIONS)


# ---------------------------------------------------------------------------------------------
# TF-IDF

SETTINGS = ["REMOVE_STOP_WORDS", "MIN_MOVIES", "REPEATS_COUNT_LESS"]


def tfidf_settings():
    """The three choices in tfidf_settings.py, read from the file every time."""
    try:
        values = runpy.run_path(str(SETTINGS_FILE))
    except SyntaxError as e:
        raise Problem(f"tfidf_settings.py has a mistake on line {e.lineno}: {e.msg}.")
    settings = {}
    for name in SETTINGS:
        if name not in values:
            raise Problem(f"tfidf_settings.py has no {name}. Put the line back.")
        settings[name] = values[name]
    for name in ["REMOVE_STOP_WORDS", "REPEATS_COUNT_LESS"]:
        if not isinstance(settings[name], bool):
            raise Problem(f"In tfidf_settings.py, {name} must be True or False.")
    if type(settings["MIN_MOVIES"]) is not int or settings["MIN_MOVIES"] < 1:
        raise Problem("In tfidf_settings.py, MIN_MOVIES must be a whole number, 1 or more.")
    return settings


def describe(settings):
    """'REMOVE_STOP_WORDS = False, MIN_MOVIES = 1, ...', as the settings file writes them."""
    return ", ".join(f"{name} = {value}" for name, value in settings.items())


class TfidfSearch:
    """TF-IDF over the plot summaries: one row of word weights per movie. Words are always
    lowercased, so "Dog" and "dog" are one word."""

    key, name = "tfidf", "TF-IDF"

    def __init__(self, movies, settings):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.movies, self.settings = movies, settings
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english" if settings["REMOVE_STOP_WORDS"] else None,
            min_df=settings["MIN_MOVIES"],
            sublinear_tf=settings["REPEATS_COUNT_LESS"],
        )
        try:
            self.matrix = self.vectorizer.fit_transform([m["overview"] for m in movies])
        except ValueError:
            raise Problem(f"No word is in {settings['MIN_MOVIES']} or more plot summaries, so "
                          "TF-IDF has no words left. Lower MIN_MOVIES in tfidf_settings.py.")
        self.words = self.vectorizer.get_feature_names_out()
        self.asked = None

    def scores(self, questions):
        """One row per question: its cosine similarity with every movie, 0 if they share no
        word. The rows of TfidfVectorizer's output already have length 1, so the cosine
        similarity is a dot product."""
        self.asked = self.vectorizer.transform(questions)  # kept for matched()
        return (self.asked @ self.matrix.T).toarray()

    def matched(self, q, i):
        """The words that question q of the last scores() call shares with movie i, the word
        that adds the most to the score first."""
        both = self.asked[q].multiply(self.matrix[i]).tocsr()
        order = np.argsort(-both.data, kind="stable")
        return [str(self.words[j]) for j in both.indices[order]]

    def ignored(self, question):
        """The question's words that count for nothing because the vocabulary leaves them out:
        stop words if you remove them, words in fewer than MIN_MOVIES summaries, and words no
        summary uses. (Single letters, like "a", are never words to TF-IDF.)"""
        tokenize = self.vectorizer.build_tokenizer()
        words = tokenize(self.vectorizer.build_preprocessor()(question))
        return [w for w in dict.fromkeys(words) if w not in self.vectorizer.vocabulary_]


# ---------------------------------------------------------------------------------------------
# Embeddings

def load_model(download=False):
    """The embedding model. Unless download is True, it only loads what download_model.py has
    already put in .model/, so it never waits on the network."""
    from fastembed import TextEmbedding
    from loguru import logger

    logger.disable("fastembed")  # fastembed logs its own errors; we print a plainer one
    try:
        return TextEmbedding(MODEL, cache_dir=str(MODEL_DIR), local_files_only=not download)
    except ValueError:
        if download:
            raise
        raise Problem("The embedding model isn't downloaded yet. Run: "
                      "uv run python download_model.py")


def embed(model, texts):
    """Each text as 384 numbers, scaled to length 1 so that a dot product is the cosine
    similarity. The model reads only the first 256 word pieces of a text."""
    return np.array(list(model.embed(texts, batch_size=32)), dtype=np.float32)


def shipped_vectors(movies):
    """The plot summaries' vectors from data/embeddings.npz, one row per movie, in the order of
    data/movies.jsonl."""
    if not VECTORS.exists():
        raise Problem("data/embeddings.npz is missing. Tell Shilad.")
    shipped = np.load(VECTORS)
    if list(shipped["ids"]) != [m["id"] for m in movies]:
        raise Problem("data/embeddings.npz doesn't match data/movies.jsonl. Tell Shilad.")
    return shipped["vectors"]


class EmbedSearch:
    """Embedding search: the question's vector against every plot summary's vector."""

    key, name = "embed", "Embeddings"

    def __init__(self, movies):
        self.movies = movies
        self.vectors = shipped_vectors(movies)
        self.model = load_model()

    def scores(self, questions):
        return embed(self.model, questions) @ self.vectors.T

    def cut_off(self, question):
        """True if the question is longer than the 256 word pieces the model reads, so that
        the model never saw its end."""
        return bool(self.model.model.tokenizer.encode(question).overflowing)


# ---------------------------------------------------------------------------------------------
# Ranking, used by search.py, evaluate.py and site.py

def search(method, questions, answer_ids=None):
    """Rank the movies for each question. Returns one dict per question:

        "top"   the first TOP movies, each {"id", "title", "score"}, and for TF-IDF "matched":
                the question's words that are also in that movie's plot summary.
        "rank"  (only with answer_ids) where the right movie is in the list, 1 for first, or
                None when it is not in the first DEPTH.

    Ties keep the order of data/movies.jsonl. TF-IDF lists only the movies that share a word
    with the question: all the others score 0, so their order would mean nothing."""
    ids = np.array([m["id"] for m in method.movies])
    scores = method.scores(questions)
    found = []
    for q, row in enumerate(scores):
        order = np.argsort(-row, kind="stable")[:DEPTH]
        if method.key == "tfidf":
            order = order[row[order] > 0]
        top = []
        for i in order[:TOP]:
            hit = {"id": int(ids[i]), "title": method.movies[i]["title"], "score": round(float(row[i]), 4)}
            if method.key == "tfidf":
                hit["matched"] = method.matched(q, i)
            top.append(hit)
        result = {"top": top}
        if answer_ids is not None:
            where = np.flatnonzero(ids[order] == answer_ids[q])
            result["rank"] = int(where[0]) + 1 if len(where) else None
            if method.key == "tfidf":
                answer = np.flatnonzero(ids == answer_ids[q])
                result["answer_matched"] = method.matched(q, answer[0]) if len(answer) else []
        found.append(result)
    return found


def ordinal(n):
    """1 -> '1st', 2 -> '2nd', 13 -> '13th'."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def rank_words(rank):
    return ordinal(rank) if rank else f"not in the top {DEPTH}"


# What evaluate.py, search.py and site.py say when a question is longer than the model reads.
CUT_OFF = ("The embedding model reads only about the first 200 words of a question, so it "
           "ignored the end of {}.")


def counts(group):
    """(how many questions, how many have the right movie first, how many in the top 10)."""
    first = sum(r["rank"] == 1 for r in group)
    top = sum(r["rank"] is not None and r["rank"] <= TOP for r in group)
    return len(group), first, top


def score_sentences(name, rows, per_kind=False):
    """Plain sentences for one method's results: the written questions, then each kind of
    written question when per_kind is True, then the real requests. Embeddings are "they"."""
    they = "they" if name == NAMES["embed"] else "it"
    written = [r for r in rows if r["kind"] != "real"]
    real = [r for r in rows if r["kind"] == "real"]
    lines = []
    if written:
        n, first, top = counts(written)
        lines.append(f"{name} put the right movie first for {first} of {n:,} written questions "
                     f"and in the top {TOP} for {top}.")
    if written and per_kind:
        for kind in dict.fromkeys(r["kind"] for r in written):
            n, first, top = counts([r for r in written if r["kind"] == kind])
            lines.append(f"  Of the {n:,} {kind} questions, {they} put {first} first and {top} in "
                         f"the top {TOP}.")
    if real:
        n, first, top = counts(real)
        start = they.capitalize() if written else name
        lines.append(f"{start} put the right movie first for {first} of {n:,} real requests and "
                     f"in the top {TOP} for {top}.")
    return lines


def read_results(key):
    """results/<key>.json as a dict, or None if evaluate.py hasn't written it."""
    path = RESULTS / f"{key}.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)
