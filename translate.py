"""Translate a sentence in Pāli by looking up and classifying each word in DPD first, then using an LLM to do the final translation."""

# Basic libraries
import sys
import re
import argparse
import inquirer

## Google GenAI API
from google import genai
from google.genai import types
from pprint import pprint

from google.api_core import retry

# These are the essential imports needed for database operations
from dpd.db_helpers import get_db_session

# To access any table, import its corresponding class here
# Other available options include DpdRoot, DbInfo, and Lookup, etc.
from dpd.models import DpdHeadword, Lookup

# Transliterate words into standard form
from dpd.translit import auto_translit_to_roman
from dpd.niggahitas import replace_niggahitas

# Grammar helper functions
from grammar import grammar_parse, grammar_explain

# Retry when rate limit reached
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
    genai.models.Models.generate_content
)

MODEL = "gemini-2.5-pro-preview-03-25"
MAX_TOKENS = 8192
TEMPERATURE = 0.3
SYSTEM_INSTRUCTION = """
You are an accurate Pāli to English translator. You translate Pāli sentences to English by first considering the entire sentence, then consider the grammatical role and meaning of each word in the sentence in a Markdown table that will be provided to you, and then generate as output the translated sentence in natural English.
"""

sentence = sys.argv[1]

# Use regex to find all sequences of word characters (letters, numbers, underscore).
# This effectively discards punctuation as it only extracts word-like sequences.
# \w in Python 3's re module is Unicode-aware and should handle Pāli characters.
words = re.findall(r'\w+', sentence.lower())
# print(words)

# This establishes a connection to the database - use it once to access the database
db_session = get_db_session('dpd.db')

pali = []
grammar = []
meaning = []

for word in words:
    word = replace_niggahitas(auto_translit_to_roman(word.lower()))
    pali.append(word)

    print(f"\n\n{word}:")

    # Lookup word in dictionary
    lookup = (
        db_session.query(Lookup)
        .filter(Lookup.lookup_key == word)
        .first()
    )

    if lookup is None:
        print (f"{word} failed lookup, trying headword")
        grammar.append([word, "unknown", "🔼"])
        meaning.append(None)
        continue

    if lookup.deconstructor:
        print(f"deconstruct {word}: {lookup.deconstructor}")

    headwords = [db_session.query(DpdHeadword).filter(DpdHeadword.id == hw).first() for hw in lookup.headwords_unpack]

    headword = inquirer.list_input(
        message="meaning",
        choices=[(f"{hw.lemma_1}: {hw.meaning_combo}",hw) for hw in headwords],
    )
    meaning.append(headword)

    print(f"{word}: {headword.meaning_combo} [pos={headword.pos} grammar={headword.grammar} neg={headword.neg} verb={headword.verb} trans={headword.trans} case={headword.plus_case}]\n")

    if lookup.grammar:
        inflection = inquirer.list_input(
            message="inflection form",
            choices=[(grammar_parse(g),g) for g in lookup.grammar_unpack],
        )
    else:
        inflection = [word, "particle", "particle"]

    grammar.append(inflection)
    print(grammar_parse(inflection) + ' = ' + grammar_explain(inflection))

print(' '.join(pali))
print(' '.join([grammar_parse(g) for g in grammar]))
print(' | '.join([(hw.meaning_1 if hw is not None else 'unknown') for hw in meaning]))

meanings_table = "| word | grammar role | meaning |\n| --- | --- | --- |\n"
for index, word in enumerate(pali):
    meanings_table += f"| {word} | {grammar_explain(grammar[index])} | {meaning[index].meaning_combo if meaning[index] is not None else 'unknown, possibly a formal name'} |\n"

# print(meanings_table)

prompt1 = f"Consider the following sentence in Pāli. <sentence>{sentence}.</sentence>.\n\nNow consider the meanings of each word in the following table:\n"
prompt2 = "\n\nNow translate the sentence as accurately as you can into natural English considering the grammatical role and meaning of each word in the sentence from the above table."
client = genai.Client()
response = client.models.generate_content(
    model=MODEL,
    contents=[prompt1,meanings_table,prompt2],
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        max_output_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    ),
)
print(response.text)

# Always close the database session when you're finished
db_session.close()
