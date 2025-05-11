
to_symbol = {
    "nom": "①",
    "acc": "②",
    "instr": "③",
    "dat": "④",
    "abl": "⑤",
    "gen": "⑥",
    "loc": "⑦",
    "voc": "⓪",
    "masc": "🚹",
    "fem": "🚺",
    "nt": "🚻",
    "x": "⚧️",
    "sg": "⨀",
    "pl": "⨂",
    "dual": "⨁",
    "act": "🟢",
    "reflx": "🔵",
    "pr": "▶️",
    "fut": "⏭",
    "aor": "⏮",
    "opt": "⏯",
    "imp": "⏹",
    "cond": "🔀",
    "imperf": "↩️",
    "perf": "🔄",
    "1st": "👆",
    "2nd": "🤘",
    "3rd": "🤟",
}

to_explanation = {
    "nom": "nominative",
    "acc": "accussative",
    "instr": "instrumental",
    "dat": "dative",
    "abl": "ablative",
    "gen": "genitive",
    "loc": "locative",
    "voc": "vocative",
    "masc": "masculine",
    "fem": "feminine",
    "nt": "neuter",
    "x": "all-gender",
    "sg": "singular",
    "pl": "plural",
    "dual": "dual",
    "act": "active",
    "reflx": "reflexive",
    "pr": "present-tense",
    "fut": "future-tense",
    "aor": "aorist",
    "opt": "optative",
    "imp": "imperative",
    "cond": "conditional",
    "imperf": "imperfect",
    "perf": "perfect",
    "1st": "first person",
    "2nd": "second person",
    "3rd": "third person",
}

to_meaning = {
    "nom": "subject",
    "acc": "object",
    "instr": "by/with",
    "dat": "for",
    "abl": "from",
    "gen": "of",
    "loc": "in/at/on",
    "voc": "vocative",
}

def get_symbols(grammar: str):
    if grammar == "in comps":
        return "🆎"

    chunks = grammar.split(' ')
    return ''.join(map(lambda s: to_symbol.get(s, s), chunks))

def get_explanation(grammar: str):
    if grammar[1] == "unknown":
        return f"?({grammar[0]})"
    elif grammar == "particle":
        return "indeclinable or particle"

    chunks = grammar.split(' ')
    return ' '.join(map(lambda s: to_explanation.get(s, s), chunks))

def grammar_parse(grammar: list[tuple[str, str, str]]):
    if grammar[1] == "unknown":
        return f"?({grammar[0]})"
    elif grammar[1] == "particle":
        return f"🔼({grammar[0]})"

    desc = get_symbols(grammar[2])
    if grammar[1] == 'noun':
        desc += f"({grammar[0]})"
    elif grammar[1] == 'verb':
        desc += f"[{grammar[0]}]"
    else:
        desc += f"({grammar[1]}:{grammar[0]})"
    return desc

def grammar_explain(grammar: list[tuple[str, str, str]]):
    if grammar[1] == "unknown":
        return "unknown, possibly a formal name"
    elif grammar[1] == "particle":
        return "particle or indeclinable"
    else:
        return f"{get_explanation(grammar[2])} of {grammar[0]} ({grammar[1]})"
