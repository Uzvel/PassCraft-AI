"""
generator.py — Personalized passphrase generator + adversarial optimizer
=========================================================================
Three cognitive profiles:
    Phonetic      — rhyme families, alliteration clusters
    Spatial       — QWERTY finger-zone localized words
    Visual Absurdity — surreal vivid noun mashups

Adversarial optimizer: SHAP-guided mutation loop until score = 2 (Strong).
"""

import random
import re
import secrets
from typing import Optional

# ── Word pools ───────────────────────────────────────────────────────────────

PHONETIC_POOLS = {
    "rhyme_ight": ["Night", "Bright", "Ignite", "Delight", "Insight", "Knight", "Flight"],
    "rhyme_ow":   ["Flow", "Glow", "Throw", "Rainbow", "Plateau", "Below", "Bestow"],
    "rhyme_aze":  ["Blaze", "Maze", "Phase", "Craze", "Amaze", "Graze", "Daze"],
    "rhyme_ake":  ["Awake", "Shake", "Drake", "Quake", "Flake", "Opaque", "Remake"],
    "alliter_s":  ["Silver", "Storm", "Stride", "Spark", "Swift", "Surge", "Stellar"],
    "alliter_fl": ["Flame", "Flash", "Fleet", "Flair", "Flick", "Flood", "Flare"],
    "alliter_cr": ["Crush", "Craft", "Crown", "Creek", "Crisp", "Craze", "Creed"],
    "alliter_bl": ["Blaze", "Blade", "Bloom", "Bliss", "Blind", "Blunt", "Bleak"],
}

SPATIAL_REAL = [
    "Steer", "Greet", "Treed", "Frees", "Sweet", "Fleet", "Sewed",
    "Freed", "Greed", "Sleet", "Trews", "Deter", "Egged", "Refer",
    "Reef",  "Seed",  "Deed",  "Feed",  "Weed",  "Teed",  "Reed",
]

ABSURD_NOUNS_A = [
    "Velvet", "Chrome", "Neon", "Marble", "Obsidian", "Titanium",
    "Crimson", "Glacier", "Phantom", "Cosmic", "Molten", "Ceramic",
    "Amber", "Tungsten", "Sapphire", "Vortex",
]
ABSURD_NOUNS_B = [
    "Walrus", "Blimp", "Banjo", "Cactus", "Igloo", "Platypus", "Anvil",
    "Zeppelin", "Mackerel", "Kazoo", "Pretzel", "Lobster", "Penguin",
    "Accordion", "Trombone", "Manatee",
]
ABSURD_ACTIONS = [
    "Rides", "Destroys", "Befriends", "Launches", "Melts", "Greets",
    "Inspects", "Kidnaps", "Ignites", "Defeats", "Haunts", "Repairs",
    "Discovers", "Architects", "Obliterates",
]

DELIMITERS = ["-", "_", ".", "~", "!", "#"]
LEET_MAP   = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
SUFFIXES   = ["Mx", "Z3", "Vx", "Q9", "W8", "Nx", "Kz", "J4", "R6", "P2"]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _clean(kw: str, max_len: int = 10) -> str:
    """Strip non-alphanumeric, title-case, truncate."""
    clean = re.sub(r"[^a-zA-Z0-9]", "", kw)
    return clean[:max_len].capitalize() if clean else ""


def _pick(lst: list, rng: random.Random) -> str:
    return rng.choice(lst)


# ── Generator ────────────────────────────────────────────────────────────────

def generate_passphrase(
    artists: list[str],
    aesthetics: list[str],
    year: Optional[str],
    profile: str,
    seed: Optional[int] = None,
) -> str:
    """
    Generate a personalized raw passphrase.

    Args:
        artists    : User's favorite artists/bands
        aesthetics : Aesthetic / subculture keywords
        year       : Memorable year string
        profile    : "Phonetic" | "Spatial" | "Visual Absurdity"
        seed       : Optional RNG seed for reproducibility

    Returns:
        Raw passphrase string (pre-optimization).
    """
    rng = random.Random(seed if seed is not None else secrets.randbits(32))

    # Sanitize user keywords
    user_kws = [_clean(k) for k in (artists + aesthetics) if k.strip()]
    user_kws = [k for k in user_kws if len(k) >= 3][:6]
    personal = rng.choice(user_kws) if user_kws else "Echo"

    yr = _clean(year) if year and year.strip() else str(rng.randint(1990, 2024))
    delim = _pick(DELIMITERS, rng)

    if profile == "Phonetic":
        pool_words = _pick(list(PHONETIC_POOLS.values()), rng)
        words = rng.sample(pool_words, min(3, len(pool_words)))
        parts = [words[0], personal, words[1], yr]

    elif profile == "Spatial":
        words = rng.sample(SPATIAL_REAL, 3)
        parts = [words[0], personal, words[1], yr]

    else:  # Visual Absurdity
        noun_a  = _pick(ABSURD_NOUNS_A, rng)
        noun_b  = _pick(ABSURD_NOUNS_B, rng)
        action  = _pick(ABSURD_ACTIONS, rng)
        parts = [noun_a + noun_b, action, personal, yr]

    return delim.join(parts)


# ── Mutation operators ────────────────────────────────────────────────────────

def _apply_leet(s: str, intensity: float = 0.45) -> str:
    result = []
    for ch in s:
        if ch.lower() in LEET_MAP and random.random() < intensity:
            result.append(LEET_MAP[ch.lower()])
        else:
            result.append(ch)
    return "".join(result)


def _inject_special(s: str) -> str:
    combos = ["@#", "!$", "#3", "$7", "!9", "@2", "#5", "!0"]
    insertion = random.choice(combos)
    pos = random.randint(max(1, len(s) // 2), len(s))
    return s[:pos] + insertion + s[pos:]


def _shift_capitals(s: str) -> str:
    indices = [i for i, c in enumerate(s) if c.islower()]
    if not indices:
        return s
    picks = random.sample(indices, min(2, len(indices)))
    lst = list(s)
    for i in picks:
        lst[i] = lst[i].upper()
    return "".join(lst)


def _extend_suffix(s: str) -> str:
    delim  = random.choice(DELIMITERS)
    suffix = random.choice(SUFFIXES)
    return s + delim + suffix


# ── Adversarial optimizer ─────────────────────────────────────────────────────

def optimize_passphrase(
    passphrase: str,
    predict_fn,
    max_iterations: int = 30,
) -> tuple[str, int, list[str]]:
    """
    Iteratively mutate `passphrase` until predict_fn returns score=2 (Strong).

    Args:
        passphrase    : Raw generated passphrase
        predict_fn    : Callable matching ml_engine.predict() signature
        max_iterations: Safety cap on mutation loop

    Returns:
        (optimized_passphrase, final_score, iteration_log)
    """
    current = passphrase
    log: list[str] = []

    for i in range(max_iterations):
        score, feats, shap = predict_fn(current)
        label = ["WEAK", "MEDIUM", "STRONG"][score]
        log.append(
            f"iter {i:02d} | {label:<6} | len={int(feats['length']):>3} "
            f"| H={feats['entropy']:.2f} | {current}"
        )

        if score == 2:
            return current, score, log

        # SHAP-guided mutation: target the most negative contributor
        worst_feat = min(shap, key=shap.get)

        if feats["length"] < 18 or worst_feat == "length":
            current = _extend_suffix(current)
            log[-1] += "  → [extend: length low]"
        elif worst_feat in ("entropy", "unique_char_ratio"):
            current = _apply_leet(current, 0.5)
            log[-1] += "  → [leet: entropy low]"
        elif worst_feat == "upper_ratio":
            current = _shift_capitals(current)
            log[-1] += "  → [capitals: upper ratio low]"
        elif worst_feat in ("special_ratio",):
            current = _inject_special(current)
            log[-1] += "  → [inject: special ratio low]"
        else:
            # Rotate through all mutations
            ops = [_extend_suffix, _shift_capitals, _inject_special,
                   lambda s: _apply_leet(s, 0.4)]
            current = random.choice(ops)(current)
            log[-1] += "  → [random mutation]"

    score, _, _ = predict_fn(current)
    return current, score, log
