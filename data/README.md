# The data

This folder holds the data for the activity. You don't need to edit anything here.

| File | What it holds |
|---|---|
| `movies.jsonl` | The collection: 4,309 movies, one per line, each with its plot summary. |
| `questions.jsonl` | The question bank: 518 questions, one per line, each with the one movie it is looking for. |
| `LICENSE-movielens.txt` | The MovieLens licence. It must be included with any data built from MovieLens. |

## movies.jsonl

Each line is one movie. Here is *Groundhog Day*:

```json
{"id": 137, "movieId": 1265, "title": "Groundhog Day (1993)", "year": 1993, "genres": "Comedy, Fantasy, Romance", "overview": "A narcissistic TV weatherman, along with his attractive-but-distant producer, and his mawkish cameraman, is sent to report on Groundhog Day in the small town of Punxsutawney, where he finds himself repeating the same day over and over."}
```

`id` is the movie's id at The Movie Database (TMDB), and it's how a question names its answer.
`movieId` is the movie's id in MovieLens, the ratings data from HW1, or `null` for a movie that
wasn't in HW1. `overview` is TMDB's plot summary, the text you'll search.

The first 3,988 lines are the HW1 movies that have a summary, in the same order as HW1 (most
rated first). The other 321 lines are the answers to the real requests (below) that weren't
already in HW1, sorted by title. The two groups differ in a few small ways:

* HW1's titles are MovieLens titles, which move a leading "The" to the end ("Matrix, The
  (1999)"). The added movies use TMDB's title, which for a few films is in the original language.
* HW1's genres use MovieLens's names ("Sci-Fi", "Children") and the added movies use TMDB's
  ("Science Fiction", "Family"). Seven movies have no genres.
* Six HW1 titles have no year in them, so their `year` is `null`.

## questions.jsonl

Each line is one question, in this shape:

```
{"id": "<id>", "kind": "<kind>", "question": "<the question>", "answer_id": <id of the answer in movies.jsonl>, "answer_title": "<its title in movies.jsonl>"}
```

There are two kinds of question, written questions first:

* 100 written questions (ids `w001` to `w100`), in three kinds: "detail", "reworded" and "vague".
  The activity's README says what each kind means. They were drafted by Claude, from what it
  knows about the films. Claude checked that each has one right movie in the collection and
  doesn't copy words from that movie's summary. If one seems wrong, tell me.
* 418 real requests (`kind` "real", ids starting with `tot-`) from people trying to name a movie
  they half remember. They are as people wrote them, spelling and all; each joins the post's
  title and its text. People posted them on iRememberThisMovie.com between 2013 and 2018, and
  the TREC (Text REtrieval Conference) 2023 Tip-of-the-Tongue track used 450 of them, each
  with the Wikipedia page of its answer. A script matched each answer to TMDB, through its IMDb
  id where it had one, and every uncertain match was checked by hand. 32 of the 450 are left
  out: 31 because the answer is a TV series or a single TV episode, which TMDB doesn't list as a
  movie, and one because the answer's TMDB entry has no summary.

A content note: some real requests describe violence, including violence against children, or
sexual content, sometimes in detail. So do a few of the added movies' summaries. You're welcome
to skip any you'd rather not read.

## Sources and credit

* Plot summaries for every movie, and the titles, years and genres of the added movies, come from
  [TMDB](https://www.themoviedb.org). This activity uses TMDB data but is not endorsed or
  certified by TMDB.
* HW1's movies (their ids, titles and genres) come from MovieLens 32M, from GroupLens Research
  at the University of Minnesota: F. Maxwell Harper and Joseph A. Konstan. 2015. "The MovieLens
  Datasets: History and Context." *ACM Transactions on Interactive Intelligent Systems* 5(4),
  19:1-19:19. <https://doi.org/10.1145/2827872>. The licence is in `LICENSE-movielens.txt`. In
  short: research use only, no commercial use, no endorsement by the University of Minnesota or
  GroupLens, and anything built from it is shared under the same terms.
* The real requests come from the
  [TREC 2023 Tip-of-the-Tongue track](https://trec-tot.github.io/guidelines-2023), which took them
  from Microsoft's MS-TOT dataset: Jaime Arguello, Adam Ferguson, Emery Fine, Bhaskar Mitra, Hamed
  Zamani and Fernando Diaz. 2021. "Tip of the Tongue Known-Item Retrieval: A Case Study in Movie
  Identification." *CHIIR 2021*. <https://doi.org/10.1145/3406522.3446021>.
  * What is known about the licence: the track's 2023 guidelines name none. The
    [MS-TOT repository](https://github.com/microsoft/Tip-of-the-Tongue-Known-Item-Retrieval-Dataset-for-Movie-Identification),
    which contains all 418 requests here, grants its content under
    [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The track's organisers
    republished 399 of the 418 under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
    in their 2025 release at <https://zenodo.org/records/15356599>, which includes the 2023 dev
    requests along with most of the 2023 training and test requests. Neither source says anything
    about the rights of the people who wrote the posts.
* The written questions were drafted by Claude, as described above.
