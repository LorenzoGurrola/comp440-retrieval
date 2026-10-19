# COMP 440: Representing and Retrieving Knowledge

> **Draft, Oct 19.** Not ready for students yet. The scripts and data are built and are being
> reviewed and tested.

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
  them on a bank of 518 questions.
* To find which kinds of questions each method handles well, and why. Thursday's class picks up
  from there with hybrid retrieval, which combines the two.

## Overview

On October 1 we scored the words in Wikipedia articles with TF-IDF and looked at GloVe word
embeddings. Today you'll use both ideas to search for movies.

The collection, `data/movies.jsonl`, is 4,309 movies: the movies from HW1, plus the movies
that answer the real requests described below. Each line is one movie with its plot summary (its
"overview") from The Movie Database (TMDB):

```json
{"id": 137, "movieId": 1265, "title": "Groundhog Day (1993)", "year": 1993, "genres": "Comedy, Fantasy, Romance", "overview": "A narcissistic TV weatherman, along with his attractive-but-distant producer, and his mawkish cameraman, is sent to report on Groundhog Day in the small town of Punxsutawney, where he finds himself repeating the same day over and over."}
```

The overviews are short (about 45 words is typical) and were written by TMDB's volunteer
contributors. You'll search them two ways:

* *TF-IDF* (term frequency, inverse document frequency) is keyword search. It gives each word
  in an overview a weight. A word weighs a lot when it appears in this overview and in few
  others: "Punxsutawney" appears in one overview, so it weighs a lot there, while "the" appears
  in nearly all of them and weighs almost nothing. A search weighs your question's words the
  same way and ranks the movies whose overviews share the most heavily weighted words with it.
* *Embedding search* turns your question and every overview into a list of numbers with a small
  language model (all-MiniLM-L6-v2), then ranks the movies whose numbers are closest to your
  question's. It's the same idea as the GloVe word vectors from October 1, applied to whole
  sentences instead of single words. The model runs with fastembed, a small open-source Python
  package that turns text into embeddings without needing PyTorch.

The question bank, `data/questions.jsonl`, pairs each question with the one movie it's looking
for. It has two parts:

* 100 written questions, drafted by Claude (an AI model), in three kinds. For *Groundhog Day*:
  * "detail" names a character, a place or a specific thing: "the weatherman in Punxsutawney";
  * "reworded" tells the plot in other words: "a self-centered TV forecaster wakes up every
    morning to find it's still February 2nd";
  * "vague" is how you'd describe it to a friend: "a funny movie where a guy keeps reliving the
    same day".
* 418 real requests from people trying to name a movie they half remember, used in the 2023
  Tip-of-the-Tongue track of TREC (the Text REtrieval Conference). They are usually several
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
  It downloads about 160 MB (the model is about 90 MB of it), so it can take a few minutes when
  the whole class downloads at once. You carry on meanwhile.
* Claude asks your name, then two predictions: which method will do better on questions that
  name a character, a place or a thing, and which on vague descriptions, and why. A guess is
  fine. Claude commits them before any search runs; that is what makes them predictions.

### Part 1. Build the TF-IDF model · about 8 minutes

* `tfidf_settings.py` holds the four settings that decide how TF-IDF weighs words: whether "Dog"
  and "dog" are one word, whether to leave out common words like "the", how many plot summaries
  a word must be in to count, and whether a word repeated in one summary counts less.
* Claude explains each setting, one at a time. You choose each one and say why. There is no
  best answer; I'm interested in your reasons.

### Part 2. Top terms · about 7 minutes

* Pick **two or three** movies you know well. Nearly all of HW1's movies are in the collection.
* Claude runs `uv run python top_terms.py "<title>"` for each. It prints the words with the
  highest weight in that movie's overview. Here are the first lines for *Groundhog Day*, with
  the starting settings:

  ```
  Groundhog Day (1993): the 15 words with the highest TF-IDF weight in its plot summary.

       word               weight  count here  movies
    1. mawkish             0.267           1       1
    2. groundhog           0.267           1       1
    3. punxsutawney        0.267           1       1
    4. day                 0.263           2     162
    5. weatherman          0.255           1       2
  ```

  It goes on to 15 words, says what each column means, and prints the plot summary and your
  settings.
* What do the top terms get right and wrong about what makes each movie distinctive?

### Part 3. Your own searches · about 8 minutes

* Ask **at least three** questions of your own, for example about a movie you know, described
  without its title. Try more than one kind: a detail, the plot retold, something vague.
* Claude runs `uv run python search.py "<your question>"` for each. It prints the top 10 movies
  by TF-IDF. Here are the first lines for one question, with the starting settings:

  ```
  Question: a heist on a train

  TF-IDF, top 10:
     1. 0.209  Dog Day Afternoon (1975)   matched: heist, on
     2. 0.196  Baby Driver (2017)   matched: heist
     3. 0.188  Reindeer Games (2000)   matched: heist
  ```

  The number is the score, the cosine similarity of the question and the plot summary: 1 is the
  most alike, and 0 means no word in common. "matched" lists your words that are also in that
  movie's summary, the one that adds the most to the score first.
* Did the movie you meant come up? What did TF-IDF get right and wrong?

### Part 4. The question bank · about 10 minutes

* Claude runs `uv run python evaluate.py --method tfidf`. It runs every question in the bank and
  says how often the right movie came out near the top: for the written questions, for each
  kind of them, and for the real requests. Its output looks like this, with numbers in the
  blanks. They depend on your settings, so I've left them out here:

  ```
  TF-IDF, with your settings: LOWERCASE = True, REMOVE_STOP_WORDS = False, MIN_MOVIES = 1, REPEATS_COUNT_LESS = False.
  Ran 518 questions against 4,309 movies in 2 seconds.

  TF-IDF put the right movie first for __ of 100 written questions and in the top 10 for __.
    Of the 34 detail questions, it put __ first and __ in the top 10.
    Of the 33 reworded questions, it put __ first and __ in the top 10.
    Of the 33 vague questions, it put __ first and __ in the top 10.
  It put the right movie first for __ of 418 real requests and in the top 10 for __.

  Saved every question's top 10 in results/tfidf.json. To look through them: uv run python site.py
  ```

* Read the scores out in your own words.
* Claude opens the comparison site at http://localhost:8765. It shows one question at a time:
  the right movie, where TF-IDF ranked it, and TF-IDF's top 10 with the words each one shares
  with the question. Look through some answers, especially the misses: questions where the right
  movie wasn't near the top. The Show menu can list only the misses.
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

* Movies: the 3,988 of HW1's 4,000 most-rated movies in MovieLens 32M that have a plot summary,
  plus 321 movies that answer the real requests. MovieLens is from GroupLens Research at the
  University of Minnesota (F. Maxwell Harper and Joseph A. Konstan, "The MovieLens Datasets:
  History and Context", ACM Transactions on Interactive Intelligent Systems, 2015). Its licence
  is in `data/LICENSE-movielens.txt`.
* Overviews: [The Movie Database (TMDB)](https://www.themoviedb.org), from the copy at
  [ada-datadruids/full_tmdb_movies_dataset](https://huggingface.co/datasets/ada-datadruids/full_tmdb_movies_dataset)
  on Hugging Face. This activity uses TMDB data but is not endorsed or certified by TMDB.
* Real requests: the [TREC 2023 Tip-of-the-Tongue track](https://trec-tot.github.io/guidelines-2023),
  which took them from Microsoft's MS-TOT dataset (Jaime Arguello, Adam Ferguson, Emery Fine,
  Bhaskar Mitra, Hamed Zamani and Fernando Diaz, "Tip of the Tongue Known-Item Retrieval: A Case
  Study in Movie Identification", CHIIR 2021). All 418 are in the
  [MS-TOT repository](https://github.com/microsoft/Tip-of-the-Tongue-Known-Item-Retrieval-Dataset-for-Movie-Identification),
  under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), and 399 of them are in
  the track organisers' [2025 release](https://zenodo.org/records/15356599), under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). `data/README.md` has the details.
* Written questions: drafted by Claude, an AI model made by Anthropic. Each was checked to have
  a single right answer in the collection and for words copied from that movie's summary.
  They're a draft until I've reviewed them.
* Embedding model: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
  (Apache 2.0 licence), in the copy that [fastembed](https://github.com/qdrant/fastembed)
  downloads, [Qdrant/all-MiniLM-L6-v2-onnx](https://huggingface.co/Qdrant/all-MiniLM-L6-v2-onnx).
