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

XXXX

### Did the movies you meant come up? What did TF-IDF get right and wrong?

XXXX

## Part 4: The question bank

### Which kind of question did TF-IDF handle best, and which worst? By how much?

XXXX

### The misses you looked at: what do they have in common?

XXXX

## Part 5: Embeddings

### What is a sentence embedding, in your own words?

XXXX

### Where does each method do better, and why?

XXXX

### Your Part 0 predictions: which held, and which would you change?

XXXX

### How might you combine the two methods?

XXXX
