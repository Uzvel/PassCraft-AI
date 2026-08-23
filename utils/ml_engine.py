"""
ml_engine.py — Real ML password strength classifier
====================================================
Uses a trained RandomForestClassifier (18k samples, 99.97% accuracy)
with real SHAP TreeExplainer values.
"""

import math
import pickle
import re
import string
from pathlib import Path
from typing import Optional

import numpy as np

# ── Optional SHAP (graceful fallback if not installed) ──────────────────────
try:
    import shap as shap_lib
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE  = Path(__file__).parent.parent / "model"
_MODEL = _BASE / "rf_model.pkl"
_SCALER = _BASE / "scaler.pkl"

FEATURE_NAMES = [
    "length",
    "entropy",
    "upper_ratio",
    "digit_ratio",
    "special_ratio",
    "has_sequential_digits",
    "has_keyboard_walk",
    "unique_char_ratio",
    "max_repeat_run",
    "has_common_pattern",
]

LABEL_MAP = {0: "Weak", 1: "Medium", 2: "Strong"}

# ── Model singleton (loaded once) ────────────────────────────────────────────
_model  = None
_scaler = None
_explainer = None


def _load_model():
    global _model, _scaler, _explainer
    if _model is not None:
        return
    with open(_MODEL, "rb") as f:
        _model = pickle.load(f)
    with open(_SCALER, "rb") as f:
        _scaler = pickle.load(f)
    if SHAP_AVAILABLE:
        _explainer = shap_lib.TreeExplainer(_model)


def extract_features(password: str) -> list[float]:
    """Extract 10 character-level features from a password string."""
    n = len(password)
    if n == 0:
        return [0.0] * 10

    # Shannon entropy
    freq: dict[str, int] = {}
    for ch in password:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = -sum((c / n) * math.log2(c / n) for c in freq.values())

    upper_ratio   = sum(1 for c in password if c.isupper())   / n
    digit_ratio   = sum(1 for c in password if c.isdigit())   / n
    special_ratio = sum(1 for c in password if c in string.punctuation) / n

    seq_digits = float(bool(re.search(
        r'(?:0123|1234|2345|3456|4567|5678|6789|7890|9876|8765|7654|6543|5432|4321|3210)',
        password
    )))

    keyboard_walks = [
        'qwer', 'wert', 'erty', 'rtyu', 'tyui', 'yuio', 'uiop',
        'asdf', 'sdfg', 'dfgh', 'fghj', 'ghjk', 'hjkl',
        'zxcv', 'xcvb', 'cvbn', 'vbnm',
    ]
    has_kw = float(any(w in password.lower() for w in keyboard_walks))

    unique_ratio = len(freq) / n

    max_run = run = 1
    for i in range(1, n):
        run = run + 1 if password[i] == password[i - 1] else 1
        max_run = max(max_run, run)

    common_patterns = [
        'password', 'pass', 'letmein', '123456', 'qwerty', 'abc',
        'iloveyou', 'admin', 'login', 'welcome', 'monkey', 'dragon',
        'master', '000000', '111111',
    ]
    has_common = float(any(w in password.lower() for w in common_patterns))

    return [
        float(n),
        round(entropy, 4),
        round(upper_ratio, 4),
        round(digit_ratio, 4),
        round(special_ratio, 4),
        seq_digits,
        has_kw,
        round(unique_ratio, 4),
        float(max_run),
        has_common,
    ]


def predict(password: str) -> tuple[int, dict, dict]:
    """
    Classify password strength using the trained Random Forest model.

    Returns:
        score      (int)  : 0=Weak, 1=Medium, 2=Strong
        features   (dict) : feature name → value
        shap_vals  (dict) : feature name → SHAP contribution (float)
    """
    _load_model()

    raw_feats = extract_features(password)
    feat_dict = dict(zip(FEATURE_NAMES, raw_feats))

    X = np.array(raw_feats).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    score = int(_model.predict(X_scaled)[0])

    # ── SHAP values ──────────────────────────────────────────────────────────
    if SHAP_AVAILABLE and _explainer is not None:
        sv = _explainer.shap_values(X_scaled)
        # shap >= 0.42 returns ndarray of shape (n_samples, n_features, n_classes)
        # older shap returns list of length n_classes, each (n_samples, n_features)
        import numpy as _np
        sv = _np.array(sv)
        if sv.ndim == 3 and sv.shape[0] == 1:
            # shape (1, n_features, n_classes) → pick predicted class
            class_shap = sv[0, :, score]
        elif sv.ndim == 3 and sv.shape[2] > 1:
            # shape (n_samples, n_features, n_classes)
            class_shap = sv[0, :, score]
        elif sv.ndim == 2:
            # shape (n_classes, n_features) — old list-of-arrays stacked
            class_shap = sv[score]
        else:
            class_shap = sv.flatten()[:len(FEATURE_NAMES)]
        shap_dict = {
            name: round(float(val), 4)
            for name, val in zip(FEATURE_NAMES, class_shap)
        }
    else:
        # Fallback: feature importance × sign heuristic
        importances = _model.feature_importances_
        shap_dict = {}
        for name, imp, val in zip(FEATURE_NAMES, importances, raw_feats):
            if name == "length":
                direction = 1 if val >= 16 else (-1 if val < 8 else 0.3)
            elif name == "entropy":
                direction = 1 if val >= 3.5 else (-1 if val < 2 else 0.2)
            elif name in ("has_sequential_digits", "has_keyboard_walk", "has_common_pattern"):
                direction = -1 if val else 0
            elif name == "max_repeat_run":
                direction = -0.5 if val > 2 else 0
            else:
                direction = 1 if val > 0 else 0
            shap_dict[name] = round(float(imp * direction), 4)

    return score, feat_dict, shap_dict


def get_proba(password: str) -> dict:
    """Return class probabilities for the three strength levels."""
    _load_model()
    X = np.array(extract_features(password)).reshape(1, -1)
    X_scaled = _scaler.transform(X)
    proba = _model.predict_proba(X_scaled)[0]
    return {LABEL_MAP[i]: round(float(p), 4) for i, p in enumerate(proba)}
