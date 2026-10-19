"""
The comparison site: your question-bank results one question at a time, and a search box.

    uv run python site.py              # opens http://localhost:8765 in your browser
    uv run python site.py --no-open    # only prints the address
    uv run python site.py --port 9000  # another port

It shows only the methods you have run with evaluate.py: TF-IDF after
`evaluate.py --method tfidf`, and embeddings beside it after `evaluate.py --method embed`. Reload
the page after a new run. The search box uses tfidf_settings.py as it is now. The site runs until
you press Ctrl-C.

Every page is plain HTML made below, so it works without JavaScript; site/style.css styles it.
"""

import argparse
import html
import re
import sys
import threading
import traceback
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from retrieval import (CUT_OFF, DEPTH, KINDS, NAMES, REPO, TOP, EmbedSearch, Problem,
                       TfidfSearch, counts, load_movies, rank_words, read_results, search,
                       tfidf_settings)

PORT = 8765
STYLE = REPO / "site" / "style.css"
SHORT = 60     # a longer question shows its first SHORT words, and the rest behind "Show the rest"
MATCHED = 8    # a "Matched" list shows this many words, then "and N more"
ROWS = [("Detail", "detail"), ("Reworded", "reworded"), ("Vague", "vague"), ("Real requests", "real")]
PING = "comp440-retrieval site"

MOVIES = {}    # TMDB id -> movie, filled in main()
lock = threading.Lock()
cache = {}     # the search methods, built on first use


def esc(text):
    return html.escape(str(text))


def link(**params):
    return "/?" + urlencode(params)


# ---------------------------------------------------------------------------------------------
# What the page shows

def bank():
    """The results files that exist, and the questions they share, in the bank's order. Each
    question is (question, {method: that method's answer})."""
    results = {key: r for key in NAMES if (r := read_results(key))}
    if not results:
        return results, []
    by_id = {key: {q["id"]: q for q in r["questions"]} for key, r in results.items()}
    first = next(iter(results.values()))["questions"]
    questions = [(q, {key: by_id[key][q["id"]] for key in results})
                 for q in first if all(q["id"] in by_id[key] for key in results)]
    return results, questions


def in_top(answer):
    return answer["rank"] is not None and answer["rank"] <= TOP


def better(runs, a, b):
    """True if method a put the right movie in its top 10 and higher than method b did."""
    rank_b = runs[b]["rank"] or DEPTH + 1
    return in_top(runs[a]) and runs[a]["rank"] < rank_b


def choices(methods):
    """The dropdown: (value, label, explanation or None, test on a question's answers)."""
    found = [
        ("all", "All questions", None, lambda q, runs: True),
        ("written", "Written questions", None, lambda q, runs: q["kind"] != "real"),
        ("real", "Real requests", None, lambda q, runs: q["kind"] == "real"),
    ]
    if len(methods) == 1:
        key, name = methods[0], NAMES[methods[0]]
        found.append((f"{key}_missed", f"{name} missed", f"Questions where the right movie is not "
                      f"in {name}'s top {TOP}.", lambda q, runs: not in_top(runs[key])))
    elif len(methods) == 2:
        found += [
            ("tfidf_better", "TF-IDF did better", f"Questions where TF-IDF put the right movie in "
             f"its top {TOP}, and higher than embeddings did.",
             lambda q, runs: better(runs, "tfidf", "embed")),
            ("embed_better", "Embeddings did better", f"Questions where embeddings put the right "
             f"movie in their top {TOP}, and higher than TF-IDF did.",
             lambda q, runs: better(runs, "embed", "tfidf")),
            ("both_missed", "Both missed", f"Questions where neither method put the right movie "
             f"in its top {TOP}.", lambda q, runs: not in_top(runs["tfidf"]) and not in_top(runs["embed"])),
        ]
    return found


def highlight(text, words):
    """The text as HTML, with every word in `words` marked. It finds words the way TF-IDF does:
    two or more letters or digits in a row, lowercased."""
    out, last = [], 0
    for m in re.finditer(r"(?u)\b\w\w+\b", text):
        if m.group().lower() in words:
            out += [esc(text[last:m.start()]), f"<mark>{esc(m.group())}</mark>"]
            last = m.end()
    return "".join(out) + esc(text[last:])


def overview(movie_id):
    movie = MOVIES.get(movie_id)
    return movie["overview"] if movie else "(This movie is no longer in data/movies.jsonl.)"


# ---------------------------------------------------------------------------------------------
# Pieces of HTML

def page(body, title="Your results"):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="/style.css">
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def named(keys):
    """'TF-IDF', or 'TF-IDF and embeddings': the methods' names as they go in a sentence."""
    return " and ".join(NAMES[key] if i == 0 else NAMES[key].lower() for i, key in enumerate(keys))


def title(results):
    """The page title: "Your results: TF-IDF", later "Your results: TF-IDF and embeddings"."""
    return "Your results" + (f": {named(results)}" if results else "")


def score_table(results):
    """For each kind of question, how often each method put the right movie 1st and in its top
    10, as counts out of that kind's questions."""
    head = ['<th scope="col" rowspan="2">Questions</th>']
    head += [f'<th scope="colgroup" colspan="2">{esc(NAMES[key])}</th>' for key in results]
    sub = "".join(f'<th scope="col">1st</th><th scope="col">in top {TOP}</th>' for _ in results)
    rows = []
    for label, kind in ROWS:
        cells = []
        for r in results.values():
            n, first, top = counts([q for q in r["questions"] if q["kind"] == kind])
            cells += [f"<td>{first} of {n:,}</td>", f"<td>{top} of {n:,}</td>"]
        if n:
            rows.append(f'<tr><th scope="row">{label}</th>{"".join(cells)}</tr>')
    return f"""<p class="caption" id="scores-caption">How many times each method put the right movie 1st, and how many times in its top {TOP}, for each kind of question.</p>
<div class="table-wrap"><table class="scores" aria-describedby="scores-caption">
<thead><tr>{"".join(head)}</tr><tr>{sub}</tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table></div>"""


def top_part(results):
    """The home page's title, what the page shows, the score table, and a note if the TF-IDF
    settings changed after the results were made."""
    parts = [f"<h1>{esc(title(results))}</h1>"]
    if not results:
        return parts[0]
    parts.append(f'<p class="intro">One question from the bank at a time: the movie it was looking '
                 f"for, where each method put it, and each method's top {TOP}. Each method's list "
                 f"is checked {DEPTH} movies deep, so a right movie further down shows as "
                 f'"not in the top {DEPTH}".</p>')
    parts.append(score_table(results))
    if "tfidf" in results:
        try:
            if results["tfidf"]["settings"] != tfidf_settings():
                parts.append('<p class="note">Your TF-IDF settings changed after these results were '
                             "made. The search box uses the new settings; the question bank still "
                             "shows the old ones. To update it, run "
                             "<code>uv run python evaluate.py --method tfidf</code> and reload.</p>")
        except Problem as e:
            parts.append(f'<p class="note">{esc(e)}</p>')
    return "\n".join(parts)


def asked(text):
    """The question, with the end of a long one behind "Show the rest"."""
    words = text.split()
    if len(words) <= SHORT + 15:
        return f'<blockquote class="asked">{esc(text)}</blockquote>'
    start, rest = " ".join(words[:SHORT]), " ".join(words[SHORT:])
    return (f'<blockquote class="asked">{esc(start)} ...'
            f"<details><summary>Show the rest ({len(words) - SHORT} more words)</summary>"
            f"<p>... {esc(rest)}</p></details></blockquote>")


def columns(found, answer_id=None, notes=None):
    """Each method's top 10 side by side. `found` maps a method to its list of hits."""
    notes = notes or {}
    lists = []
    if "tfidf" in found:
        lists.append("TF-IDF lists the question's words it found in each summary, the one that adds "
                     "most to the score first.")
    if "embed" in found:
        lists.append("Embeddings compare whole sentences, so there are no words to list.")
    out = ['<p class="hint">Click a title to see its plot summary.</p>',
           f'<p class="hint words-hint">{esc(" ".join(lists))}</p>' if lists else "",
           f'<div class="columns n{len(found)}">']
    for key, hits in found.items():
        out.append(f'<section class="method"><h3>{esc(NAMES[key])}</h3>')
        if isinstance(hits, str):  # a problem, in words
            out.append(f'<p class="note">{esc(hits)}</p></section>')
            continue
        out.append('<ol class="hits">')
        for n, hit in enumerate(hits, 1):
            right = hit["id"] == answer_id
            words = set(hit.get("matched", []))
            lines = [f'<span class="n">{n}.</span> <span class="title">{esc(hit["title"])}</span>']
            if right:
                lines.append('<span class="badge">The right movie</span>')
            if "matched" in hit:
                marked = ", ".join(f"<mark>{esc(w)}</mark>" for w in hit["matched"][:MATCHED])
                more = len(hit["matched"]) - MATCHED
                if more > 0:
                    marked += f" and {more} more"
                lines.append(f'<span class="words">Matched: {marked}</span>')
            plot = highlight(overview(hit["id"]), words)
            out.append(f'<li class="hit{" right" if right else ""}"><details><summary>'
                       f'{" ".join(lines)}</summary><p class="plot">{plot}</p></details></li>')
        out.append("</ol>")
        if key == "tfidf" and len(hits) < TOP:
            shares = "No plot summary shares" if not hits else f"Only {len(hits)} plot summaries share"
            out.append(f'<p class="note">{shares} a word with this question.</p>')
        if notes.get(key):
            out.append(f'<p class="note">{esc(notes[key])}</p>')
        out.append("</section>")
    out.append("</div>")
    return "\n".join(out)


def search_form(query="", show="all", i=1):
    return f"""<section class="search">
<h2>Search for anything</h2>
<form method="get" action="/search">
<label for="q">Your question</label>
<div class="row"><input type="search" id="q" name="q" value="{esc(query)}">
<input type="hidden" name="show" value="{esc(show)}"><input type="hidden" name="i" value="{i}">
<button type="submit">Search</button></div>
</form>
</section>"""


# ---------------------------------------------------------------------------------------------
# The two pages

def home(params):
    results, questions = bank()
    parts = [top_part(results)]
    if not results:
        parts.append("<p>No question-bank results yet. They appear here after you run "
                     "<code>uv run python evaluate.py --method tfidf</code>. Then reload this page.</p>")
        parts.append(search_form())
        return page("\n".join(parts), title(results))

    methods = list(results)
    options = choices(methods)
    show = params.get("show") if params.get("show") in {o[0] for o in options} else "all"
    value, label, explanation, test = next(o for o in options if o[0] == show)
    shown = [(q, runs) for q, runs in questions if test(q, runs)]
    try:
        i = int(params.get("i", 1))
    except ValueError:
        i = 1

    menu = "".join(f'<option value="{v}"{" selected" if v == show else ""}>{esc(lab)} '
                   f"({sum(t(q, runs) for q, runs in questions)})</option>"
                   for v, lab, _, t in options)
    parts.append(f"""<section class="bank">
<h2>The question bank, one question at a time</h2>
<form class="pick" method="get" action="/">
<label for="show">Show</label>
<select id="show" name="show" onchange="this.form.submit()">{menu}</select>
<button type="submit">Go</button>
</form>""")
    if explanation:
        parts.append(f'<p class="explain">{esc(explanation)}</p>')
    if not shown:
        parts.append("<p>No questions match this choice.</p></section>")
        parts.append(search_form(show=show))
        return page("\n".join(parts), title(results))

    i = (i - 1) % len(shown) + 1
    q, runs = shown[i - 1]
    previous, following = (i - 2) % len(shown) + 1, i % len(shown) + 1
    parts.append(f"""<nav class="steps">
<a href="{link(show=show, i=previous)}" rel="prev">Previous</a>
<span>Question {i} of {len(shown)} <span class="id">({esc(q["id"])})</span></span>
<a href="{link(show=show, i=following)}" rel="next">Next</a>
</nav>""")

    ranks = ", ".join(f"{NAMES[key] if n == 0 else NAMES[key].lower()} {rank_words(runs[key]['rank'])}"
                      for n, key in enumerate(methods))
    answer_words = set(runs["tfidf"].get("answer_matched", [])) if "tfidf" in runs else set()
    marked = ", with the question's words marked" if "tfidf" in runs else ""
    parts.append(f"""<article class="question">
<p class="kind">{esc(KINDS.get(q["kind"], q["kind"]))}</p>
{asked(q["question"])}
<p class="answer">The right movie: <strong>{esc(q["answer_title"])}</strong></p>
<p class="ranks">Where the right movie landed: {esc(ranks)}.</p>
<p class="plot answer-plot"><span class="label">Its plot summary{marked}:</span> {highlight(overview(q["answer_id"]), answer_words)}</p>
</article>""")
    if runs.get("embed", {}).get("cut_off"):
        parts.append(f'<p class="note">{esc(CUT_OFF.format("this one"))}</p>')
    found = {key: runs[key]["top10"] for key in methods}
    parts.append(columns(found, q["answer_id"]))
    parts.append("</section>")
    parts.append(search_form(show=show, i=i))
    return page("\n".join(parts), title(results))


def method(key):
    """The search method for the search box, built on first use. TF-IDF is rebuilt whenever
    tfidf_settings.py changes."""
    if key == "tfidf":
        settings = tfidf_settings()
        if cache.get("settings") != settings:
            cache["tfidf"], cache["settings"] = TfidfSearch(list(MOVIES.values()), settings), settings
    elif "embed" not in cache:
        cache["embed"] = EmbedSearch(list(MOVIES.values()))
    return cache[key]


def search_page(params):
    query = " ".join(params.get("q", "").split())
    show, i = params.get("show", "all"), params.get("i", "1")
    results, _ = bank()
    parts = [f"<h1>{esc(title(results))}</h1>",
             f'<p><a href="{link(show=show, i=i)}">Back to the question bank</a></p>',
             search_form(query, show, i)]
    if query:
        found, notes = {}, {}
        for key in ["tfidf"] + (["embed"] if "embed" in results else []):
            try:
                with lock:
                    m = method(key)
                    found[key] = search(m, [query])[0]["top"]
                    if key == "tfidf":
                        notes[key] = " ".join(m.ignored_lines(query))
                    elif m.cut_off(query):
                        notes[key] = CUT_OFF.format("this one")
            except Problem as e:
                found[key] = str(e)
        if len(query.split()) > 20:  # a long question doesn't fit in the box, so show it all
            parts.append(f'<section class="question">{asked(query)}</section>')
        parts.append(columns(found, None, notes))
    return page("\n".join(parts), title(results))


# ---------------------------------------------------------------------------------------------
# The server

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        params = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/":
                self.send(home(params))
            elif url.path == "/search":
                self.send(search_page(params))
            elif url.path == "/style.css":
                self.send(STYLE.read_text(encoding="utf-8"), "text/css")
            elif url.path == "/ping":
                self.send(PING, "text/plain")
            else:
                self.send(page('<p>Nothing is here. <a href="/">Back to the start</a>.</p>'), status=404)
        except Exception as e:
            traceback.print_exc()
            self.send(page(f"<p>Something went wrong making this page: {esc(e)}. Tell Shilad.</p>"),
                      status=500)

    def send(self, text, kind="text/html", status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{kind}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # keep the terminal quiet


def ours(port):
    """True if this site is already answering on the port."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/ping", timeout=2) as r:
            return r.read().decode() == PING
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--no-open", action="store_true", help="don't open the browser")
    parser.add_argument("--port", type=int, default=PORT, help=f"the port to use (default {PORT})")
    args = parser.parse_args()
    try:
        MOVIES.update((m["id"], m) for m in load_movies())
    except Problem as e:
        print(e)
        return 1

    for port in range(args.port, args.port + 20):
        url = f"http://localhost:{port}"
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            if ours(port):
                print(f"The site is already running at {url}. Reload the page to see your latest "
                      "results.", flush=True)
                if not args.no_open:
                    webbrowser.open(url)
                return 0
    else:
        print(f"Ports {args.port} to {args.port + 19} are all busy. Try --port with another number.")
        return 1

    busy = f" (port {args.port} was busy)" if port != args.port else ""
    print(f"The site is running at {url}{busy}. Stop it with Ctrl-C.", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped the site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
