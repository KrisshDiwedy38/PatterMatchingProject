# Real text data

Experiment 5 and the `real_text` dataset need a book saved as `data/book.txt`.

1. Go to [Project Gutenberg](https://www.gutenberg.org/) and pick any book, for example
   *Pride and Prejudice*: https://www.gutenberg.org/cache/epub/1342/pg1342.txt
2. Save the "Plain Text UTF-8" version as `data/book.txt`.

The loader lowercases the text and collapses all whitespace to single spaces.
If the file is missing, the real-text experiment is skipped with a warning and the
dashboard hides the `real_text` option. Nothing else is affected.
