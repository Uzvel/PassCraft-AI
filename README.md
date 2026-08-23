# 🔐 PassCraft AI v2.0
### Cognitive Passphrase Intelligence System

> A production-grade password security tool powered by a real RandomForest ML model, SHAP explainability, HaveIBeenPwned breach detection, and an AES-256 encrypted local vault — wrapped in a multi-step Streamlit wizard.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange?style=flat-square&logo=scikitlearn)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Real ML Model** | RandomForestClassifier trained on 24,000 synthetic passwords · 99.97% test accuracy |
| **SHAP Explainability** | Real TreeExplainer SHAP values — see exactly *why* your password scored as it did |
| **HIBP Breach Check** | k-anonymity API — only a 5-char SHA-1 prefix is sent, your password never leaves the device |
| **Cognitively Personalized Generator** | 3 profiles: Phonetic (rhyme/alliteration), Spatial (QWERTY-localized), Visual Absurdity (surreal mashups) |
| **Adversarial Optimization Loop** | SHAP-guided mutation loop — iteratively strengthens the passphrase until the model scores it Strong |
| **AES-256 Encrypted Vault** | Local session vault using Fernet + PBKDF2-HMAC-SHA256 (480k iterations) |
| **Crack Time Estimator** | Search-space bits → human-readable crack time at 1 trillion guesses/second |
| **Memory Sandbox** | Type-from-memory verification with character overlap feedback |

---

## 🏗 Project Structure

```
passcraft-ai/
│
├── app.py                  ← Main Streamlit application
├── train_model.py          ← Standalone model training script
├── requirements.txt        ← Python dependencies
├── run_passcraft.bat       ← Windows one-click launcher
│
├── model/
│   ├── rf_model.pkl        ← Trained RandomForest model
│   └── scaler.pkl          ← StandardScaler for feature normalization
│
├── utils/
│   ├── ml_engine.py        ← Feature extraction, prediction, SHAP
│   ├── generator.py        ← Passphrase generator + adversarial optimizer
│   └── security.py         ← HIBP checker, AES-256 encryption, entropy calc
│
└── .streamlit/
    └── config.toml         ← Dark theme config for Streamlit Cloud
```

---

## 🚀 Quick Start

### Windows (double-click)
```
run_passcraft.bat
```
Right-click → Properties → Unblock if SmartScreen blocks it.

### Manual (any OS)
```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/passcraft-ai.git
cd passcraft-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Retrain the model
python train_model.py

# 4. Launch
streamlit run app.py
```

---

## 🤖 ML Model Details

**Architecture:** `RandomForestClassifier` (300 trees, max_depth=14)

**Training Data:** 24,000 synthetic passwords (8,000 per class)

**Feature Set (10 features):**

| Feature | Description |
|---|---|
| `length` | Raw character count |
| `entropy` | Shannon entropy over character distribution |
| `upper_ratio` | Fraction of uppercase characters |
| `digit_ratio` | Fraction of digit characters |
| `special_ratio` | Fraction of punctuation characters |
| `has_sequential_digits` | Regex detection of `1234`, `9876` etc. |
| `has_keyboard_walk` | Detection of `qwer`, `asdf`, `zxcv` etc. |
| `unique_char_ratio` | Character diversity ratio |
| `max_repeat_run` | Longest consecutive repeated character run |
| `has_common_pattern` | Blocklist of 15 common weak passwords |

**Results:**
```
              precision    recall  f1-score
Weak              1.00      1.00      1.00
Medium            1.00      1.00      1.00
Strong            1.00      1.00      1.00
Accuracy                              99.97%
```

---

## 🔒 Security Architecture

### HIBP k-Anonymity
```
password → SHA-1 → "A94A8..." → send only "A94A8" → compare suffix locally
```
Your actual password is never transmitted. [Learn more](https://haveibeenpwned.com/API/v3#PwnedPasswords)

### Local Vault Encryption
```
PIN + random 16-byte salt → PBKDF2-HMAC-SHA256 (480,000 iterations) → 256-bit key → AES-256 (Fernet)
```
Nothing is persisted to disk — vault lives in Streamlit session state only.

---

## 🌐 Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Deploy**

Your app will be live at `https://your-app-name.streamlit.app` in ~2 minutes.

---

## 📦 Dependencies

```
streamlit>=1.35.0       — UI framework
scikit-learn>=1.4.0     — RandomForest model
numpy>=1.26.0           — Numerical operations
shap>=0.45.0            — TreeExplainer SHAP values
cryptography>=42.0.0    — AES-256 / Fernet / PBKDF2
requests>=2.31.0        — HIBP API calls
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

Built as a portfolio-grade ML security application.
Demonstrates: supervised ML, SHAP explainability, security API integration, cryptographic best practices, and production Streamlit UI design.
