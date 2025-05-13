import re

## Google GenAI API
from google import genai
from google.genai import types

from google.api_core import retry
from google.api_core import exceptions

import streamlit as st

# To access any table, import its corresponding class here
# Other available options include DpdRoot, DbInfo, and Lookup, etc.
from dpd.models import DpdHeadword, Lookup

# Transliterate words into standard form
from dpd.translit import auto_translit_to_roman
from dpd.niggahitas import replace_niggahitas

# Grammar helper functions
from grammar import grammar_parse, grammar_explain

MAX_TOKENS=8192
TEMPERATURE=0.3

st.title("Pāli to English translator v2 using DPD and LLM")

conn = st.connection('dpd_db', type='sql')

if 'client' not in st.session_state:
    st.session_state['client'] = genai.Client()

client = st.session_state['client']

# Retry when rate limit reached
is_retriable = lambda e: isinstance(e, (exceptions.ResourceExhausted, exceptions.ServiceUnavailable))
retry_decorator = retry.Retry(predicate=is_retriable)
generate_content = retry_decorator(client.models.generate_content)

if 'models' not in st.session_state:
    models = []
    for model in client.models.list():
        models.append(model)
    st.session_state['models'] = models

models = st.session_state['models']

defmodel = 0
for index, model in enumerate(models):
    if model.name == "models/gemini-2.5-pro-preview-05-06":
        defmodel = index

with st.sidebar:
    st.markdown("This uses an LLM to translate Pāli text to English by first looking up words in DPD and then analysing them.")
    model = st.selectbox(label="Model", options=models, index=defmodel, format_func=(lambda m : m.display_name))
    temperature = st.slider(label="Temperature", min_value=0.0, max_value=2.0, value=TEMPERATURE, step=0.1, format="%0.1f")
    # system = st.text_area(label="Instruction", value=SYSTEM_INSTRUCTION, height=300)

pali = st.text_area(label="Pāli text")

words = []
meanings = []
lookups = ""
analysis = ""
naive = ""
grounded = ""

words = re.findall(r'\w+', pali.lower())
words = [replace_niggahitas(auto_translit_to_roman(word)) for word in words]
with conn.session as db_session:
    for word in words:
        lookup = db_session.query(Lookup).filter(Lookup.lookup_key == word).first()
        if lookup is not None:
            headwords = [db_session.query(DpdHeadword).filter(DpdHeadword.id == hw).first() for hw in lookup.headwords_unpack]
        else:
            headwords = None
        meanings.append([word, lookup, headwords])

for word in meanings:
    lookups += f"### Word: {word[0]}\n\n"
    if word[1] is not None and word[1].grammar:
        lookups += "Possible grammmar roles (select one):\n"
        for g in word[1].grammar_unpack:
            lookups += f"* {grammar_parse(g)} = {grammar_explain(g)}\n"
    else:
        lookups += "Grammar roles unavailable.\n"
    lookups += '\n'
    if word[2] is not None:
        lookups += "Possible meanings (select one):\n"
        for m in word[2]:
            lookups += f"* {m.lemma_1}: {m.meaning_combo}\n"
    else:
        lookups += "Meaning unavailable.\n"
    lookups += '\n'

standard, enhanced = st.columns(2)

if standard.button("Translate (LLM)"):
    system = """
You are an efficient and accurate Pali to English translator.

## Instructions

Step 1. Read the entire text.
Step 2. Translate the text as accurately as possible. Do not insert any additional text or explanations.
Step 3. Don't include preambles, postambles or explanations.
Step 4. Output the translation only, preserving formatting of the input text, including Markdown headings and other formatting.
"""
    with st.spinner("Translating using LLM ..."):
        response = generate_content(
            model=model.name,
            contents=[pali],
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=MAX_TOKENS,
                temperature=temperature,
            ),
        )
        naive = response.text

if enhanced.button("Translate (DPD+LLM)"):
    with st.spinner("Analysing grammar and meaning ..."):
        system = "You are an accurate Pāli to English translator."
        prompt1 = "1. Consider the following sentence in Pāli."
        prompt2 = "\n\n2. Based on the context of the Pāli sentence, select one grammatical role and one meaning for each word from the possible roles and meanings in the following table.\n\n3. Write out your answers as a Markdown table with the following columns: word, grammar role, meaning without any preambles, postambles, quotations.\n"

        response = generate_content(
            model=model.name,
            contents=[prompt1, pali, prompt2, lookups],
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=MAX_TOKENS,
                temperature=temperature,
            ),
        )
        analysis = response.text

    with st.spinner("Translating based on analysis ..."):
        system = "You are an accurate Pāli to English translator."
        prompt1 = "1. Consider the following sentence in Pāli:\n"
        prompt2 = "\n\n2. Now consider the grammatical roles and meanings of each word in the following table:\n"
        prompt3 = "\n\n3. Translate the sentence as accurately as you can into natural English considering the grammatical role and meaning of each word in the sentence from the above table as a reference. Output the translation preserving formatting of the input text, including Markdown headings and other formatting. Don't include preambles, postambles or explanations."

        response = generate_content(
            model=model.name,
            contents=[prompt1, pali, prompt2, analysis, prompt3],
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=MAX_TOKENS,
                temperature=temperature,
            ),
        )
        grounded = response.text

translation_tab, dpd_tab = st.tabs(["Translation", "DPD Analysis"])

with dpd_tab:
    st.markdown(lookups)

with translation_tab:
    st.subheader("Pāli")
    st.markdown(pali)
    if len(analysis) > 0:
        st.subheader("Analysis")
        st.markdown(analysis)
    if len(naive) > 0:
        st.subheader("Translation (LLM)")
        st.markdown(naive)
        st.subheader("Markdown")
        st.code(naive, language="markdown")
    if len(grounded) > 0:
        st.subheader("Translation (DPD+LLM)")
        st.markdown(grounded)
        st.subheader("Markdown")
        st.code(grounded, language="markdown")
