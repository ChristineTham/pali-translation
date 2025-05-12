## Google GenAI API
from google import genai
from google.genai import types
from pprint import pprint

from google.api_core import retry

import streamlit as st

SYSTEM_INSTRUCTION="""
You are an efficient and accurate Pali to English translator.

## Instructions

Step 1. Read the entire text.
Step 2. Translate each line of text word by word as accurately as possible. Do not insert any additional text or explanations.
Step 3. Don't include preambles, postambles or explanations.
Step 4. When you have finished translating, output the translation following the format of the input text as closely, including Markdown headings and other formatting.
"""
MAX_TOKENS=8192
TEMPERATURE=0.3

# Retry when rate limit reached
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})

genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(
    genai.models.Models.generate_content
)

st.title("Pāli to English translator using LLM")

if 'client' not in st.session_state:
    st.session_state['client'] = genai.Client()

client = st.session_state['client']

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
    st.markdown("This uses an LLM to translate Pāli text to English without any grounding (ie. external references).")
    model = st.selectbox(label="Model", options=models, index=defmodel, format_func=(lambda m : m.display_name))
    temperature = st.slider(label="Temperature", min_value=0.0, max_value=2.0, value=TEMPERATURE, step=0.1, format="%0.1f")
    system = st.text_area(label="Instruction", value=SYSTEM_INSTRUCTION, height=300)

pali = st.text_area(label="Pāli text")

english = ""

if st.button("Translate"):
    with st.spinner("Translating ..."):
        response = None
        while response is None or response.text.startswith("None"):
            response = client.models.generate_content(
                model=model.name,
                contents=[pali],
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    max_output_tokens=MAX_TOKENS,
                    temperature=temperature,
                ),
            )
        english = response.text

pali_tab, english_tab, markdown_tab = st.tabs(["Pāli", "English", "Markdown"])

with pali_tab:
    st.markdown(pali)

with english_tab:
    st.markdown(english)

with markdown_tab:
    st.code(english, language="markdown")
