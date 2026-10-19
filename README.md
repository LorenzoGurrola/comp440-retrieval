# COMP 440: Representing and Retrieving Knowledge

> **Draft, Oct 19.** Not ready for students yet. The scripts and data are still being built,
> and everything marked `[TBD]` is open.

**Fall 2026 · In class, Tuesday, October 20 · [TBD: individual or pairs] · graded for good faith**
**Due by the end of class, 2:50pm Central**

This activity is graded for good faith: do Parts 0 to 3 and write your answers in your own words.
There are no right answers here. A method that does badly on your movies is a result, not a
mistake. Questions go to `#comp440-f26`.

**When you are finished, complete the [Work Submission Form](https://forms.gle/mgKcnqzTGxNaGvteA), select "activity" and share the URL to your GitHub repo in the textbox.**

## Goals

* To see how keyword search (TF-IDF and BM25) and embedding search rank the same movies for the
  same request, and why they differ.
* To measure both methods on descriptions you write of movies you know.
* To pool the class's results and find which kinds of requests each method handles well.
  Thursday's class picks up from there with hybrid retrieval, which combines the two.

## Overview

On October 1 we scored the words in Wikipedia articles with TF-IDF and looked at GloVe word
embeddings. Today you'll use both ideas to search.

The collection is the movies from HW1 that have a plot summary on The Movie Database (TMDB):
3,988 of the 4,000. Each movie is one line of `data/movies.jsonl`:

```json
{"movieId": 1265, "title": "Groundhog Day (1993)", "genres": "Comedy, Fantasy, Romance", "n_ratings": 7297, "overview": "A narcissistic TV weatherman, along with his attractive-but-distant producer, and his mawkish cameraman, is sent to report on Groundhog Day in the small town of Punxsutawney, where he finds himself repeating the same day over and over."}
```

`movieId` is the same id you used in HW1, and `overview` is the text both methods search. The
overviews are short (about 45 words is typical) and were written by TMDB's volunteer
contributors.

You'll search the overviews two ways:

* *Keyword search* scores a movie by the words its overview shares with your request. We'll use
  BM25, the version most search engines start from. It is TF-IDF with two changes: a word that
  appears ten times doesn't count ten times as much as one that appears once, and a long
  overview doesn't win just for being long.
* *Embedding search* turns your request and every overview into a list of 384 numbers with a
  small language model (`all-MiniLM-L6-v2`), then ranks the movies whose numbers are closest to
  yours. It is the same idea as the GloVe neighbors from October 1, applied to whole sentences
  instead of single words.

## Working together and AI

[TBD: individual or pairs.] The class's
[AI agreements](https://docs.google.com/document/d/1JhAzzTbECGEE5IdOwabVJUh36YZ5DD6ozG_cvodqc9s/edit)
apply. You are welcome to have Claude run the commands for you and explain the code. Please write
the requests and the answers in `WRITEUP.md` yourself, though. In Part 2 the class is measuring
how people describe movies, and descriptions written by Claude would measure Claude instead.

## The task

Parts 0 to 3, about 50 minutes together [TBD: confirm against the class plan]. The minutes are a
guide.

### Part 0. Setup and predictions · about 5 minutes

#### Step 1: Get the repository

* Fork this repo and clone your fork.
* Run `uv sync` to install the packages. [TBD: setup command]
* Run `uv run python search.py --setup`. It downloads the embedding model (about 90 MB) and
  loads the collection. [TBD: how long this takes on a laptop.] Start it now and do Step 2
  while it runs.

#### Step 2: Predict

In `WRITEUP.md`, answer each in a line:

* For a request that names a character, like "Hannibal Lecter", which method do you expect to do
  better? Why?
* For a vague description, like "a sad movie about a dog", which one? Why?

### Part 1. One request, two rankings · about 10 minutes

#### Step 1: Run the starter requests

* `uv run python search.py "Hannibal Lecter"`
* `uv run python search.py "a sad movie about a dog"`
* `uv run python search.py "a guy keeps reliving the same day"`

Each prints the top 10 movies from each method side by side. [TBD: expected output, from the
activity's code.]

* What does each method get right and wrong?
* Pick a keyword result that seems wrong. Which words in the request did it match? [TBD: an
  `--explain` option that prints the words that scored.]

#### Step 2: Try your own requests

* Try **at least three** requests of your own: a name, a vague description, and anything else
  you are curious about.
* Do the results match your predictions from Part 0? What surprised you?

### Part 2. Describe movies you know · about 20 minutes

A search works when it finds the thing you meant. Because you know which movie you meant, you
can measure this: the *rank* of that movie in each method's list. Rank 1 is perfect.

#### Step 1: Pick your movies

* Pick **at least three** movies you know well. The ten you chose in HW1 are a good place to
  start.
* Check that each is in the collection: `uv run python find.py --title "groundhog"` prints
  matching titles and their ids.

#### Step 2: Describe each movie twice

Without using its title, write two requests for each movie in `WRITEUP.md`:

* A "detail" request: the most specific thing you remember, like a character, a place or an
  object ("the weatherman in Punxsutawney").
* A "vague" request: how you'd describe it to a friend who hasn't seen it ("a guy keeps
  reliving the same day").

#### Step 3: Find where your movie lands

* `uv run python find.py "the weatherman in Punxsutawney" --target 1265` prints the movie's rank
  under each method, or "not in the top 100".
* Record each rank in the table in `WRITEUP.md`.
* Add your rows to the class sheet. [TBD: link to the class sheet.]
* Which method found your movies more often? Was there a pattern in how you worded the requests
  each one won?

### Part 3. The class's results · about 10 minutes

[TBD: Shilad leads a short discussion of the class sheet.]

Then answer two questions in `WRITEUP.md`:

* The overviews were written by TMDB volunteers, and the words they chose decide what keyword
  search can find. Find one of your requests where the overview's wording, more than the method,
  decided the result.
* If you were building search for this collection, would you use one method or both? If both,
  how would you combine their two lists? We'll pick this up on Thursday.

## What to submit

Your repository, with `WRITEUP.md` filled in: your predictions, your Part 1 notes, the Part 2
table, and your Part 3 answers. Share its URL through the
[Work Submission Form](https://forms.gle/mgKcnqzTGxNaGvteA) by the end of class.

## Follow-ups (optional, not graded)

[TBD: for example, real requests from people trying to name a movie they half remember, where
keyword search does better; or writing your own scoring function, as on October 1.]

## FAQ

FAQ: TBA (ask a question on Slack, `#comp440-f26`!)

## Data

* Movies: the 4,000 most-rated movies in MovieLens 32M, as shipped in HW1. MovieLens is from
  GroupLens Research at the University of Minnesota (F. Maxwell Harper and Joseph A. Konstan,
  "The MovieLens Datasets: History and Context", ACM Transactions on Interactive Intelligent
  Systems, 2015).
* Overviews: [The Movie Database (TMDB)](https://www.themoviedb.org), from the copy at
  [ada-datadruids/full_tmdb_movies_dataset](https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset)
  on Hugging Face. This activity uses TMDB data but is not endorsed or certified by TMDB.
* Embedding model: [`sentence-transformers/all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
