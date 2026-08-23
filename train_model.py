"""
train_model.py — Retrain the PassCraft AI RandomForest classifier
=================================================================
Run this once to regenerate model/rf_model.pkl and model/scaler.pkl.
Usage:
    py train_model.py
    python train_model.py
"""

import math
import os
import pickle
import random
import re
import string
import warnings
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Feature extractor (must match utils/ml_engine.py) ────────────────────────
def extract_features(password: str) -> list:
    n = len(password)
    if n == 0:
        return [0.0] * 10
    freq = {}
    for ch in password:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = -sum((c / n) * math.log2(c / n) for c in freq.values())
    upper_ratio   = sum(1 for c in password if c.isupper())   / n
    digit_ratio   = sum(1 for c in password if c.isdigit())   / n
    special_ratio = sum(1 for c in password if c in string.punctuation) / n
    seq_digits = float(bool(re.search(
        r'(?:0123|1234|2345|3456|4567|5678|6789|7890|9876|8765|7654|6543|5432|4321)',
        password)))
    kw = ['qwer','wert','erty','rtyu','asdf','sdfg','dfgh','zxcv','xcvb','cvbn']
    has_kw = float(any(w in password.lower() for w in kw))
    unique_ratio = len(freq) / n
    max_run = run = 1
    for i in range(1, n):
        run = run + 1 if password[i] == password[i - 1] else 1
        max_run = max(max_run, run)
    common = ['password','pass','letmein','123456','qwerty','abc',
              'iloveyou','admin','login','welcome','monkey','dragon',
              'master','000000','111111']
    has_common = float(any(w in password.lower() for w in common))
    return [float(n), round(entropy,4), round(upper_ratio,4), round(digit_ratio,4),
            round(special_ratio,4), seq_digits, has_kw, round(unique_ratio,4),
            float(max_run), has_common]


# ── Synthetic password generators ─────────────────────────────────────────────
def make_weak():
    choices = [
        lambda: random.choice(['password','123456','qwerty','letmein','abc123',
                               'iloveyou','admin','welcome','monkey','dragon',
                               'pass','000000','111111','sunshine','shadow']),
        lambda: ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 7))),
        lambda: ''.join(random.choices(string.digits, k=random.randint(4, 8))),
        lambda: random.choice(['qwer','asdf','zxcv']) + str(random.randint(1, 99)),
        lambda: random.choice(string.ascii_lowercase) * random.randint(4, 8),
    ]
    return random.choice(choices)()


def make_medium():
    choices = [
        lambda: ''.join(random.choices(string.ascii_letters + string.digits,
                                       k=random.randint(8, 11))),
        lambda: (random.choice(string.ascii_uppercase)
                 + ''.join(random.choices(string.ascii_lowercase, k=6))
                 + str(random.randint(10, 99))),
        lambda: ''.join(random.choices(string.ascii_letters, k=random.randint(9, 13))),
        lambda: ''.join(random.choices(string.ascii_lowercase + string.digits,
                                       k=random.randint(10, 13))),
        lambda: (''.join(random.choices(string.ascii_lowercase, k=5))
                 + random.choice('!@#$%')
                 + str(random.randint(100, 999))),
    ]
    return random.choice(choices)()


def make_strong():
    choices = [
        lambda: ''.join(random.choices(
            string.ascii_letters + string.digits + string.punctuation,
            k=random.randint(16, 28))),
        lambda: ('-'.join([
            ''.join(random.choices(string.ascii_letters, k=random.randint(4, 7)))
            for _ in range(4)
        ]) + str(random.randint(10, 99)) + random.choice('!@#$%')),
        lambda: (''.join(random.choices(string.ascii_uppercase, k=2))
                 + ''.join(random.choices(string.ascii_lowercase, k=6))
                 + ''.join(random.choices(string.digits, k=3))
                 + ''.join(random.choices('!@#$%^&*', k=3))
                 + ''.join(random.choices(string.ascii_letters, k=5))),
        lambda: ('_'.join(random.choices(
            ['Neon','Frost','Blaze','Vex','Tide','Arc','Zap','Nova',
             'Pulse','Flux','Apex','Void','Core','Hex'], k=3))
            + '_' + str(random.randint(1990, 2024))
            + random.choice('!@#$%')),
        lambda: ''.join(random.choices(
            string.ascii_letters + string.digits + '!@#$%^',
            k=random.randint(20, 32))),
    ]
    return random.choice(choices)()


# ── Main training routine ─────────────────────────────────────────────────────
def train():
    print("\n PassCraft AI — Model Training Script")
    print(" =" * 36)

    random.seed(42)
    np.random.seed(42)
    N_PER_CLASS = 8000
    total = N_PER_CLASS * 3

    print(f"\n[1/4] Generating {total:,} synthetic passwords...")
    X, y = [], []
    generators = [(make_weak, 0), (make_medium, 1), (make_strong, 2)]
    for gen_fn, label in generators:
        name = ["Weak", "Medium", "Strong"][label]
        for i in range(N_PER_CLASS):
            pw = gen_fn()
            X.append(extract_features(pw))
            y.append(label)
        print(f"    {name:<8} — {N_PER_CLASS:,} samples generated")

    X = np.array(X)
    y = np.array(y)

    print("\n[2/4] Splitting and scaling features...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    print("\n[3/4] Training RandomForestClassifier...")
    print("      n_estimators=300, max_depth=14, n_jobs=-1")
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train_s, y_train)

    acc = rf.score(X_test_s, y_test) * 100
    print(f"\n      Test Accuracy: {acc:.2f}%\n")
    print(classification_report(
        y_test, rf.predict(X_test_s),
        target_names=["Weak", "Medium", "Strong"]
    ))

    print("[4/4] Saving model artifacts...")
    out_dir = Path(__file__).parent / "model"
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / "rf_model.pkl", "wb") as f:
        pickle.dump(rf, f)
    with open(out_dir / "scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    print(f"\n Model saved → {out_dir}/rf_model.pkl")
    print(f" Scaler saved → {out_dir}/scaler.pkl")
    print("\n Done. Run 'streamlit run app.py' to launch.\n")


if __name__ == "__main__":
    train()
