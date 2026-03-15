"""
Clustering algorithms for UKIP disambiguation engine.

All similarity functions return a score in [0, 100] (int) to stay compatible
with thefuzz's threshold convention.
"""
import re
import unicodedata
from typing import List


# ── 1. Fingerprint ────────────────────────────────────────────────────────────

def fingerprint(s: str) -> str:
    """
    Canonical fingerprint: lowercase → strip accents → remove non-alphanum →
    split on whitespace → sort tokens → join.
    "Apple, Inc." → "apple inc"
    "inc Apple" → "apple inc"  (same fingerprint)
    """
    # Normalize unicode and strip accents
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    # Lowercase + remove non-alphanumeric (keep spaces)
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    # Sort tokens
    tokens = sorted(t for t in s.split() if t)
    return " ".join(tokens)


def fingerprint_similarity(a: str, b: str) -> int:
    """100 if fingerprints match, 0 otherwise."""
    return 100 if fingerprint(a) == fingerprint(b) else 0


# ── 2. N-gram (Jaccard on character bigrams) ──────────────────────────────────

def _ngrams(s: str, n: int = 2) -> set:
    """Character n-grams of a string."""
    s = s.lower().strip()
    if len(s) < n:
        return {s} if s else set()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def ngram_similarity(a: str, b: str, n: int = 2) -> int:
    """
    Jaccard similarity over character n-grams, scaled to [0, 100].
    Robust against OCR errors and minor typos.
    """
    sa, sb = _ngrams(a, n), _ngrams(b, n)
    if not sa and not sb:
        return 100
    if not sa or not sb:
        return 0
    intersection = len(sa & sb)
    union = len(sa | sb)
    return int(round(intersection / union * 100))


# ── 3. Cologne Phonetic ───────────────────────────────────────────────────────

# Cologne phonetic code table (German phonetic algorithm)
_COLOGNE_TABLE = {
    "aeijouy": "0",
    "h":       "",   # silent
    "b":       "1",
    "p":       "1",  # except before h → handled specially
    "dt":      "2",
    "fvw":     "3",
    "cgkq":    "4",
    "x":       "48",
    "sz":      "8",
    "ß":       "8",
    "mn":      "5",
    "r":       "6",
    "l":       "5",  # same code as m/n in Cologne
    "l_":      "5",
}

# Direct char → code mapping built from table
_COLOGNE_MAP: dict = {}
for chars, code in _COLOGNE_TABLE.items():
    for ch in chars:
        _COLOGNE_MAP[ch] = code


def cologne_phonetic(s: str) -> str:
    """
    Cologne Phonetic encoding (Kölner Phonetik).
    Useful for clustering European names with spelling variants:
    "Müller" ≈ "Mueller" ≈ "Muller"
    """
    # Normalize
    s = unicodedata.normalize("NFD", s)
    s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u")
    s = s.replace("Ä", "a").replace("Ö", "o").replace("Ü", "u")
    s = re.sub(r"[^a-zßA-Z]", "", s.lower())

    if not s:
        return ""

    codes = []
    for i, ch in enumerate(s):
        prev = s[i - 1] if i > 0 else ""
        nxt  = s[i + 1] if i < len(s) - 1 else ""

        # Special cases
        if ch == "c":
            if i == 0 and nxt in "ahkloqrux":
                code = "4"
            elif prev in "sz":
                code = "8"
            elif nxt in "ahoukqx" and prev not in "sz":
                code = "4"
            else:
                code = "8"
        elif ch == "p" and nxt == "h":
            code = "3"
        elif ch == "x" and prev in "ckq":
            code = "8"
        elif ch == "d" or ch == "t":
            if nxt in "csz":
                code = "8"
            else:
                code = "2"
        else:
            code = _COLOGNE_MAP.get(ch, "")

        codes.append(code)

    # Collapse consecutive identical codes and remove zeros (except first char)
    result = []
    prev_code = None
    for i, code in enumerate(codes):
        if not code:
            continue
        if code == prev_code:
            continue
        if i > 0 and code == "0":
            prev_code = code
            continue
        result.append(code)
        prev_code = code

    return "".join(result) if result else "0"


def cologne_similarity(a: str, b: str) -> int:
    """100 if Cologne phonetic codes match, 0 otherwise."""
    ca, cb = cologne_phonetic(a), cologne_phonetic(b)
    if ca and cb and ca == cb:
        return 100
    return 0


# ── 4. Metaphone (English/Spanish simplified) ─────────────────────────────────

_METAPHONE_VOWELS = set("aeiou")

def metaphone(s: str) -> str:
    """
    Simplified Metaphone encoding for English and Spanish names.
    Groups phonetically similar names: "Smith" ≈ "Smyth", "García" ≈ "Garsia"
    """
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z]", "", s.lower())
    if not s:
        return ""

    # Drop duplicate adjacent characters (except C)
    deduped = [s[0]]
    for ch in s[1:]:
        if ch != deduped[-1] or ch == "c":
            deduped.append(ch)
    s = "".join(deduped)

    # Drop trailing E
    if s.endswith("e") and len(s) > 1:
        s = s[:-1]

    result = []
    i = 0
    while i < len(s):
        ch = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        nxt2 = s[i + 2] if i + 2 < len(s) else ""

        if ch in _METAPHONE_VOWELS:
            if i == 0:
                result.append(ch.upper())
        elif ch == "b":
            if not (i == len(s) - 1 and s[i - 1] == "m"):
                result.append("B")
        elif ch == "c":
            if nxt == "i" or nxt == "e" or nxt == "y":
                result.append("S")
            elif nxt == "h":
                result.append("X"); i += 1
            elif nxt == "k":
                result.append("K"); i += 1
            else:
                result.append("K")
        elif ch == "d":
            if nxt == "g" and nxt2 in "iey":
                result.append("J"); i += 1
            else:
                result.append("T")
        elif ch == "f":
            result.append("F")
        elif ch == "g":
            if nxt in "iey":
                result.append("J")
            elif nxt == "h" and (i == 0 or s[i - 1] not in _METAPHONE_VOWELS):
                i += 1  # silent gh
            elif nxt == "n" and (i + 2 == len(s) or (nxt2 == "e" and i + 3 == len(s))):
                pass  # silent gn / gned
            else:
                result.append("K")
        elif ch == "h":
            if nxt in _METAPHONE_VOWELS and (i == 0 or s[i - 1] not in _METAPHONE_VOWELS):
                result.append("H")
        elif ch == "j":
            result.append("J")
        elif ch == "k":
            if not (i > 0 and s[i - 1] == "c"):
                result.append("K")
        elif ch == "l":
            result.append("L")
        elif ch == "m":
            result.append("M")
        elif ch == "n":
            result.append("N")
        elif ch == "p":
            if nxt == "h":
                result.append("F"); i += 1
            else:
                result.append("P")
        elif ch == "q":
            result.append("K")
        elif ch == "r":
            result.append("R")
        elif ch == "s":
            if nxt == "h" or (nxt == "i" and nxt2 in "ao"):
                result.append("X")
            else:
                result.append("S")
        elif ch == "t":
            if nxt == "h":
                result.append("0"); i += 1  # θ
            elif nxt == "i" and nxt2 in "ao":
                result.append("X")
            else:
                result.append("T")
        elif ch == "v":
            result.append("F")
        elif ch == "w":
            if nxt in _METAPHONE_VOWELS:
                result.append("W")
        elif ch == "x":
            result.extend(["K", "S"])
        elif ch == "y":
            if nxt in _METAPHONE_VOWELS:
                result.append("Y")
        elif ch == "z":
            result.append("S")

        i += 1

    return "".join(result)


def metaphone_similarity(a: str, b: str) -> int:
    """100 if Metaphone codes match, 0 otherwise."""
    ma, mb = metaphone(a), metaphone(b)
    if ma and mb and ma == mb:
        return 100
    return 0


# ── Registry ──────────────────────────────────────────────────────────────────

ALGORITHMS = {
    "fingerprint": fingerprint_similarity,
    "ngram":       ngram_similarity,
    "phonetic_cologne": cologne_similarity,
    "phonetic_metaphone": metaphone_similarity,
}
