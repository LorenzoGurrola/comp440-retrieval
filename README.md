# COMP 440: Representing and Retrieving Knowledge

> **Draft, Oct 19.** Not ready for students yet. The scripts and data are still being built,
> and everything marked `[TBD]` is open.

**Fall 2026 · In class, Tuesday, October 20 · Individual · graded for good faith**
**Due by the end of class. Anything unfinished is due 8:00am Thursday, October 22.**

This activity is graded for good faith: do Parts 0 to 5 and give your answers in your own words.
There are no right answers here. A method that does badly on your movies is a result, not a
mistake. Questions go to `#comp440-f26`.

**When you are finished, complete the [Work Submission Form](https://forms.gle/mgKcnqzTGxNaGvteA), select "activity" and share the URL to your GitHub repo in the textbox.**

## Goals

* To see how keyword search (TF-IDF) and embedding search each represent a movie, and how each
  decides which movies match a question.
* To compare the two methods by reading their answers to questions you write, and by scoring
  them on a bank of about 550 questions.
* To find which kinds of questions each method handles well, and why. Thursday's class picks up
  from there with hybrid retrieval, which combines the two.

## Overview

On October 1 we scored the words in Wikipedia articles with TF-IDF and looked at GloVe word
embeddings. Today you'll use both ideas to search for movies.

The collection, `data/movies.jsonl`, is about 4,350 movies: the movies from HW1, plus the movies
that answer the real requests described below. Each line is one movie with its plot summary (its
"overview") from The Movie Database (TMDB):

```json
[TBD: one line of data/movies.jsonl]
```

The overviews are short (about 45 words is typical) and were written by TMDB's volunteer
contributors. You'll search them two ways:

* *TF-IDF* (term frequency, inverse document frequency) is keyword search. It gives each word
  in an overview a weight. A word weighs a lot when it appears in this overview and in few
  others: "Punxsutawney" appears in one overview, so it weighs a lot there, while "the" appears
  in nearly all of them and weighs almost nothing. A search weighs your question's words the
  same way and ranks the movies whose overviews share the most heavily weighted words with it.
* *Embedding search* turns your question and every overview into a list of numbers with a small
  language model ([TBD: model name]), then ranks the movies whose numbers are closest to your
  question's. It's the same idea as the GloVe word vectors from October 1, applied to whole
  sentences instead of single words.

The question bank, `data/questions.jsonl`, pairs each question with the one movie it's looking
for. It has two parts:

* About 100 written questions [TBD: who wrote them], in three kinds. For *Groundhog Day*:
  * "detail" names a character, a place or a specific thing: "the weatherman in Punxsutawney";
  * "reworded" tells the plot in other words: "a self-centered TV forecaster wakes up every
    morning to find it's still February 2nd";
  * "vague" is how you'd describe it to a friend: "a funny movie where a guy keeps reliving the
    same day".
* 450 real requests from people trying to name a movie they half remember, collected for the
  2023 Tip-of-the-Tongue track of TREC (the Text REtrieval Conference). They are usually several
  sentences long.

## How this activity works

1. Claude runs every command and explains anything you ask about: TF-IDF, embeddings, the code,
   the scores. Ask as often as you like.
2. You make the choices and the judgments: your predictions, the TF-IDF settings, your search
   questions, which answers to look at, and what the results mean.
3. Claude asks you one question at a time. Answer in a sentence or two, and Claude writes your
   answer into `WRITEUP.md` as you said it. You don't need to edit any file yourself.
4. Claude commits and pushes at the end of each part, so your work is saved on GitHub as you go.
5. In Parts 4 and 5 a comparison site opens in your browser. Keep it next to the terminal.

**When Shilad says class is ending, type `/save`.** Claude commits and pushes what you have and
tells you where you stopped. To go on later, open a terminal in this folder and start `claude`;
it finds where you left off.

Claude records a transcript of your sessions in `TRANSCRIPT.md` to share with Shilad. Work in
this repository's folder, since sessions anywhere else aren't recorded.

## The task

Six short parts, about 50 minutes in all. The minutes are a guide.

### Part 0. Setup and predictions · about 5 minutes

* Fork this repo, clone your fork, start `claude` in its folder, and type `/setup`.
* Claude starts installing the packages and downloading the embedding model in the background.
  [TBD: how long this takes on a laptop.]
* Claude asks your name, then two predictions: which method will do better on questions that
  name a character, a place or a thing, and which on vague descriptions, and why. A guess is
  fine. Claude commits them before any search runs; that is what makes them predictions.

### Part 1. Build the TF-IDF model · about 8 minutes

* `tfidf_settings.py` holds the settings that decide how TF-IDF weighs words. [TBD: the
  settings, in a line.]
* Claude explains each setting, one at a time. You choose each one and say why. There is no
  best answer; I'm interested in your reasons.

### Part 2. Top terms · about 7 minutes

* Pick **two or three** movies you know well. Nearly all of HW1's movies are in the collection.
* Claude runs `uv run python top_terms.py "<title>"` for each. It prints the words with the
  highest weight in that movie's overview. [TBD: expected output]
* What do the top terms get right and wrong about what makes each movie distinctive?

### Part 3. Your own searches · about 8 minutes

* Ask **at least three** questions of your own, for example about a movie you know, described
  without its title. Try more than one kind: a detail, the plot retold, something vague.
* Claude runs `uv run python search.py "<your question>"` for each. It prints the top movies by
  TF-IDF. [TBD: expected output]
* Did the movie you meant come up? What did TF-IDF get right and wrong?

### Part 4. The question bank · about 10 minutes

* Claude runs `uv run python evaluate.py --method tfidf`. It runs every question in the bank and
  says how often the right movie came out near the top: overall, for each kind, and for the
  written against the real questions. [TBD: expected output]
* Read the scores out in your own words.
* Claude opens the comparison site at http://localhost:8440. [TBD: what the site shows, in one
  line.] Look through some answers, especially the misses: questions where the right movie
  wasn't near the top.
* What do the misses you looked at have in common?

### Part 5. Embeddings · about 12 minutes

* Claude explains what a sentence embedding is. Say it back in a sentence or two of your own.
* Claude runs `uv run python evaluate.py --method embed`. Read its scores next to TF-IDF's.
* Reload the site: it now shows both methods. Where does each one win, and why? If you'd like,
  Claude reruns your Part 3 questions with both methods.
* Claude shows your Part 0 predictions as you wrote them. Which held, and which would you change?
* How might you combine the two methods? We'll pick this up on Thursday.

## What to submit

Your repository, pushed, with `WRITEUP.md` filled in and both question-bank runs in `results/`.

* When Part 5 is done, Claude runs `/checkpoint`. It lists anything still missing, then commits
  and pushes.
* Submit the [Work Submission Form](https://forms.gle/mgKcnqzTGxNaGvteA), choose "activity", and
  paste your repository's GitHub URL. Tell Claude when you have, and it will tell you you're
  finished.
* If you don't finish in class, finish by **8:00am Thursday, October 22**, and submit the form
  then. You only submit it once.

## AI guidelines

The class's
[AI agreements](https://docs.google.com/document/d/1JhAzzTbECGEE5IdOwabVJUh36YZ5DD6ozG_cvodqc9s/edit)
apply. In this activity Claude runs the code and explains it. Your predictions, settings,
reasons and answers are yours, and Claude writes them down as you said them. Your Part 3
questions must be your own words: a question Claude wrote would show how Claude describes movies,
not how you do.

## Rubric

Graded for good faith. A part is complete when its command has run and its slots in `WRITEUP.md`
hold your own words. I don't grade whether a prediction came true or whether your reading
matches mine. `uv run python run_all.py` lists what is still missing.

| Part | Complete when |
|---|---|
| 0. Setup and predictions | Your two predictions, committed before any search ran |
| 1. Build the TF-IDF model | Each setting chosen, with your reason |
| 2. Top terms | What TF-IDF gets right and wrong about two or three movies you know |
| 3. Your own searches | At least three questions of your own, and what TF-IDF got right and wrong |
| 4. The question bank | `results/tfidf.json`, the scores in your words, and what the misses have in common |
| 5. Embeddings | `results/embed.json`, an embedding in your words, the scores, where each method wins, your predictions revisited, and an idea for combining the two |

## Talk to me if...

**You'd rather not use Claude.** Talk to me; there is no grade effect.

**Claude, or something else, is down.** A reported problem never costs you points. Post in
`#comp440-f26`.

**Claude won't make your predictions, choose your settings, write your questions or say what a
result shows.** That's working as intended: those are the activity. It will explain anything,
as often as you ask.

## FAQ

FAQ: TBA (ask a question on Slack, `#comp440-f26`!)

## Data

* Movies: the 4,000 most-rated movies in MovieLens 32M, as shipped in HW1, plus the movies that
  answer the real requests. MovieLens is from GroupLens Research at the University of Minnesota
  (F. Maxwell Harper and Joseph A. Konstan, "The MovieLens Datasets: History and Context", ACM
  Transactions on Interactive Intelligent Systems, 2015).
* Overviews: [The Movie Database (TMDB)](https://www.themoviedb.org), from the copy at
  [ada-datadruids/full_tmdb_movies_dataset](https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset)
  on Hugging Face. This activity uses TMDB data but is not endorsed or certified by TMDB.
* Real requests: the TREC 2023 Tip-of-the-Tongue track. [TBD: link and licence.]
* Written questions: [TBD: who wrote them.]
* Embedding model: [TBD: name and link.]
