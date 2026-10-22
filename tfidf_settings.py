"""
Your TF-IDF settings. In Part 1 you choose a value for each one.

top_terms.py, search.py, evaluate.py and site.py all read this file, so a change here changes what
they show. After a change, run `uv run python evaluate.py --method tfidf` again to update your
scores.

The values below start as scikit-learn's defaults, the plainest version of TF-IDF. The name in
parentheses is the matching argument of scikit-learn's TfidfVectorizer, which retrieval.py builds
from these three values. Words are always lowercased first, so "Dog" and "dog" are one word.
"""

# Leave out about 300 common English words, such as "the", "a", "of" and "about", using
# scikit-learn's list. True or False. (stop_words="english" when True)
REMOVE_STOP_WORDS = True

# Keep only the words that appear in the plot summaries of at least this many movies. A whole
# number, 1 or more. 1 keeps every word. (min_df)
MIN_MOVIES = 2

# When a word appears several times in one plot summary, count it less than its full count:
# 1 + log(count) instead of count, so 4 appearances count as about 2.4. True or False.
# (sublinear_tf)
REPEATS_COUNT_LESS = True
