# COMP 440: Representing and Retrieving Knowledge

Claude writes your answers here as you say them. A sentence or two is enough for each. Your
Part 0 predictions stay as you first wrote them; Part 5 asks what you would change.

**Name:** Lorenzo Gurrola
**Date:** October 22, 2026

## Part 0: Predictions

### Questions that name a character, place or thing: which method will do better, and why?

TF-IDF because the words will match

### Vague descriptions: which method will do better, and why?

Embeddings because they will capture more of the data if you can't recall specific words

## Part 1: Build the TF-IDF model

### The settings you chose, and why

REMOVE_STOP_WORDS = True: because we don't need to include words without meaning.
MIN_MOVIES = 2: because taking out the super-rare words will be beneficial
REPEATS_COUNT_LESS = True: so we can weight things appropriately

## Part 2: Top terms

### Your movies: what do the top terms get right and wrong about what makes each one distinctive?

For Beauty and the Beast, words like "belle" don't really capture the plot too well. For the Joker, my opinion is that all of the words capture the overall plot.

## Part 3: Your own searches

### Your questions, as you typed them

What movie has an adventurer in Utah trapped with a boulder over his arm for days, until he finally cuts it off and escapes
What movie involves a robot that tricks a computer programmer to let her out of her enclosure by pretending to fall in love with him
What movie involves ants that revolt against their grasshopper overlords using trickery and bravery

### Did the movies you meant come up? What did TF-IDF get right and wrong?

1/3 movies were correct. I think if I used more keywords, TF-IDF mgiht have done better

## Part 4: The question bank

### Which kind of question did TF-IDF handle best, and which worst? By how much?

It did the best on the detailed questions (31/34 in the top 10), and the worst on the vague and reworded questions (0/33 for both).

### The misses you looked at: what do they have in common?

TF-IDF succeeds when it matches many and/or specific words, such as character names, to the question. It fails when it matches few or unspecific words, such as "family" or "painting"

## Part 5: Embeddings

### What is a sentence embedding, in your own words?

A sentence embedding is a list of numbers that describe a word. When the list is interpreted as a vector, similar words will have vectors that point in similar directions. For example, the words in "Beauty in the beast" could have an embedding in this way. also, this technique can be used on full sentences or larger blocks of text.

### Where does each method do better, and why?

TF-IDF does better where there are a lot of keywords, and embeddings did better when there wern't

### Your Part 0 predictions: which held, and which would you change?

The prediction from part 0 held, and I wouldn't change it

### How might you combine the two methods?

Maybe place a weight on each, and try different weights for each step
