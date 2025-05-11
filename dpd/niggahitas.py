"""Add all variants of niggahita character (ŋ ṁ) to a list."""

from typing import List

def replace_niggahitas(word: str) -> str:
    """Replace various types of niggahitas (ŋ ṁ)."""

    word = word.replace("ṁ", "ṃ")
    word = word.replace("ŋ", "ṃ")

    return word
