"""Simple lookup of inflected word and display dictionary information"""

import argparse
import inquirer

# These are the essential imports needed for database operations
from dpd.db_helpers import get_db_session

# To access any table, import its corresponding class here
# Other available options include DpdRoot, DbInfo, and Lookup, etc.
from dpd.models import DpdHeadword, Lookup
from grammar import grammar_parse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Pāli word lookup")

# Add a positional argument that accepts one or more words
# 'nargs="+"' means it will accept at least one argument and store them in a list.
parser.add_argument('words', nargs='+', help='One or more words to search in dictionary')

# Parse the arguments
args = parser.parse_args()

# This establishes a connection to the database - use it once to access the database
db_session = get_db_session('dpd.db')

for word in args.words:
    word = word.lower()

    # Example of searching a table using basic filters:
    # Find records where part of speech is "adj" and words start with "a"
    lookup = (
        db_session.query(Lookup)
        .filter(Lookup.lookup_key == word)
        .first()
    )
    # print(lookup)

    print(f"Word '{word}': {lookup.headwords}")
    if lookup.deconstructor:
        print(f"deconstruct: {lookup.deconstructor}")

    print("grammar:")
    if lookup.grammar:
        for g in lookup.grammar_unpack:
            print(f"* {grammar_parse(g)}")

    print("meanings:")
    for hw in lookup.headwords_unpack:
        # print(hw)
        headword = (
            db_session.query(DpdHeadword)
            .filter(DpdHeadword.id == hw)
            .first()
        )
        # print(headword)
        print(f"* {headword.lemma_1}: {headword.meaning_combo}")

# Always close the database session when you're finished
db_session.close()
