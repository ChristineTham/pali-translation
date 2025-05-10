
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

def grammar_parse(grammar: list[tuple[str, str, str]]):
    desc = get_symbols(grammar[2])
    if grammar[1] == 'noun':
        desc += f"({grammar[0]})"
    elif grammar[1] == 'verb':
        desc += f"[{grammar[0]}]"
    else:
        desc += f"({grammar[1]}:{grammar[0]})"
    return desc
