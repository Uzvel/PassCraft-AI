"""
security.py — HaveIBeenPwned breach checker + local encryption utilities
=========================================================================
HIBP uses k-anonymity: only the first 5 chars of the SHA-1 hash are sent
to the API. Your actual password never leaves the device.

Encryption: AES-256 via cryptography.fernet (symmetric, key derived from
a user-supplied master PIN using PBKDF2-HMAC-SHA256).
"""

import base64
import hashlib
import os
import time
from typing import Optional

import requests
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ── Constants ────────────────────────────────────────────────────────────────
HIBP_API   = "https://api.pwnedpasswords.com/range/"
HIBP_AGENT = "PassCraft-AI/2.0 (educational password strength tool)"
REQUEST_TIMEOUT = 6  # seconds


# ══════════════════════════════════════════════════════════════════════════════
#  HIBP BREACH CHECKER
# ══════════════════════════════════════════════════════════════════════════════

def _sha1_prefix(password: str) -> tuple[str, str]:
    """
    Return (first_5_hex_chars, remaining_35_hex_chars) of SHA-1(password).
    Only the prefix is sent to the API — full hash never leaves the device.
    """
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    return digest[:5], digest[5:]


def check_hibp(password: str) -> dict:
    """
    Query the HIBP Pwned Passwords API using k-anonymity.

    Returns a dict:
        {
            "breached"  : bool,
            "count"     : int,    # times seen in breaches (0 if not found)
            "error"     : str,    # non-empty if request failed
            "offline"   : bool,   # True if we couldn't reach the API
        }
    """
    result = {"breached": False, "count": 0, "error": "", "offline": False}

    try:
        prefix, suffix = _sha1_prefix(password)
        resp = requests.get(
            HIBP_API + prefix,
            headers={"User-Agent": HIBP_AGENT, "Add-Padding": "true"},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()

        # Response is a list of "SUFFIX:COUNT" lines
        for line in resp.text.splitlines():
            parts = line.split(":")
            if len(parts) == 2 and parts[0].strip() == suffix:
                count = int(parts[1].strip())
                result["breached"] = count > 0
                result["count"]    = count
                return result

        # Suffix not found → password not in any breach
        return result

    except requests.exceptions.Timeout:
        result["error"]   = "Request timed out. Check your internet connection."
        result["offline"] = True
        return result
    except requests.exceptions.ConnectionError:
        result["error"]   = "Could not reach HIBP API. Check your internet connection."
        result["offline"] = True
        return result
    except requests.exceptions.HTTPError as e:
        result["error"] = f"HIBP API error: {e}"
        return result
    except Exception as e:
        result["error"] = f"Unexpected error: {e}"
        return result


def breach_summary(hibp_result: dict) -> tuple[str, str]:
    """
    Return (status_label, detail_message) for UI display.

    status_label: "SAFE" | "BREACHED" | "OFFLINE" | "ERROR"
    """
    if hibp_result["offline"]:
        return "OFFLINE", "Could not reach HIBP API. Result unavailable offline."
    if hibp_result["error"]:
        return "ERROR", hibp_result["error"]
    if hibp_result["breached"]:
        count = hibp_result["count"]
        return (
            "BREACHED",
            f"Found {count:,} times in known data breaches. "
            f"Do not use this passphrase.",
        )
    return "SAFE", "Not found in any known data breach database. ✓"


# ══════════════════════════════════════════════════════════════════════════════
#  LOCAL ENCRYPTION  (AES-256 via Fernet + PBKDF2)
# ══════════════════════════════════════════════════════════════════════════════

_SALT_SIZE   = 16   # bytes
_ITERATIONS  = 480_000  # OWASP 2023 recommendation for PBKDF2-SHA256


def _derive_key(pin: str, salt: bytes) -> bytes:
    """Derive a 32-byte Fernet key from a user PIN + salt via PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(pin.encode("utf-8")))


def encrypt_passphrase(passphrase: str, pin: str) -> bytes:
    """
    Encrypt a passphrase string with a user-supplied PIN.

    Returns raw bytes: [16-byte salt] + [Fernet ciphertext]
    Safe to store in a file or session state.
    """
    salt = os.urandom(_SALT_SIZE)
    key  = _derive_key(pin, salt)
    token = Fernet(key).encrypt(passphrase.encode("utf-8"))
    return salt + token


def decrypt_passphrase(blob: bytes, pin: str) -> Optional[str]:
    """
    Decrypt a blob produced by encrypt_passphrase().

    Returns the plaintext string, or None if the PIN is wrong / blob is corrupt.
    """
    try:
        salt  = blob[:_SALT_SIZE]
        token = blob[_SALT_SIZE:]
        key   = _derive_key(pin, salt)
        return Fernet(key).decrypt(token).decode("utf-8")
    except (InvalidToken, Exception):
        return None


def entropy_bits(passphrase: str) -> float:
    """
    Estimate brute-force search space in bits.
    charset_size ^ length expressed as log2.
    """
    import math, string as _str
    has_lower   = any(c.islower()              for c in passphrase)
    has_upper   = any(c.isupper()              for c in passphrase)
    has_digit   = any(c.isdigit()              for c in passphrase)
    has_special = any(c in _str.punctuation   for c in passphrase)
    pool = 0
    if has_lower:   pool += 26
    if has_upper:   pool += 26
    if has_digit:   pool += 10
    if has_special: pool += 32
    if pool == 0:
        return 0.0
    return round(math.log2(pool) * len(passphrase), 2)


def crack_time_label(bits: float) -> str:
    """Human-readable estimated crack time at 1 trillion guesses/sec."""
    seconds = (2 ** bits) / 1e12
    if seconds < 1:
        return "Instantly"
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    if seconds < 3600:
        return f"{seconds/60:.0f} minutes"
    if seconds < 86400:
        return f"{seconds/3600:.0f} hours"
    if seconds < 31_536_000:
        return f"{seconds/86400:.0f} days"
    if seconds < 31_536_000 * 1000:
        return f"{seconds/31_536_000:.0f} years"
    if seconds < 31_536_000 * 1e9:
        return f"{seconds/31_536_000/1e6:.1f} million years"
    return "Longer than the age of the universe"
