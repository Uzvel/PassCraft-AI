# 🔐 PassCraft AI
### Secure, Offline Password Manager & Generator

> A production-ready desktop security application. PassCraft AI leverages machine learning to generate highly memorable, secure passwords and stores them in a local SQLite database utilizing AES-256 field-level encryption.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=flat-square)](https://github.com/TomSchimansky/CustomTkinter)
[![SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy-red?style=flat-square)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## ✨ Features

| Feature | Details |
|---|---|
| **Native Desktop Client** | Built with CustomTkinter for a fast, responsive, and completely offline user experience. |
| **Encrypted Local Vault** | Uses SQLAlchemy and SQLite. Passwords are encrypted with AES-256 (Fernet) before writing to disk. |
| **Zero-Knowledge Architecture** | The Master PIN is never saved. It is combined with a persistent 16-byte salt (PBKDF2-HMAC-SHA256, 480k iterations) in RAM to decrypt entries. |
| **Cognitive Generation** | Generates passwords based on personal cognitive anchors (Locations, Hobbies, Media) rather than random strings. |
| **ML Auto-Strengthen** | An underlying RandomForest classifier and SHAP adversarial optimization loop automatically mutates the generated password until it reaches a 'Strong' entropy rating. |

---

## 🚀 Quick Start

### Installation

```bash
# 1. Clone
git clone [https://github.com/YOUR_USERNAME/passcraft-ai.git](https://github.com/YOUR_USERNAME/passcraft-ai.git)
cd passcraft-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the desktop app
python app.py