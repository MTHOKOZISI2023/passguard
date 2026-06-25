import hashlib
import math
from typing import Dict, List

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


GUESSES_PER_SECOND = 10_000_000_000
HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/{prefix}"


class PasswordRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


app = FastAPI(
    title="PassGuard API",
    description="Backend API for the PassGuard password strength analyzer.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": "passguard-backend"}


@app.post("/analyze")
async def analyze(payload: PasswordRequest) -> Dict[str, object]:
    password = payload.password
    rules = evaluate_rules(password)
    passed = sum(rules.values())
    score = round((passed / len(rules)) * 100)
    entropy = calculate_entropy(password)
    crack_time = seconds_to_human(seconds_from_entropy(entropy))
    breached = await check_breach(password)

    return {
        "score": score,
        "label": label_for_score(score),
        "rules": rules,
        "entropy": round(entropy, 1),
        "crack_time": crack_time,
        "breached": breached,
        "tips": generate_tips(rules, breached),
    }


def evaluate_rules(password: str) -> Dict[str, bool]:
    return {
        "length_8": len(password) >= 8,
        "length_12": len(password) >= 12,
        "uppercase": any(char.isupper() for char in password),
        "lowercase": any(char.islower() for char in password),
        "digits": any(char.isdigit() for char in password),
        "symbols": any(not char.isalnum() for char in password),
    }


def label_for_score(score: int) -> str:
    if score <= 33:
        return "Weak"
    if score <= 50:
        return "Fair"
    if score <= 83:
        return "Good"
    return "Strong"


def calculate_entropy(password: str) -> float:
    pool = 0

    if any(char.islower() for char in password):
        pool += 26
    if any(char.isupper() for char in password):
        pool += 26
    if any(char.isdigit() for char in password):
        pool += 10
    if any(not char.isalnum() for char in password):
        pool += 32

    if not password or pool == 0:
        return 0.0

    return len(password) * math.log2(pool)


def seconds_from_entropy(entropy: float) -> float:
    if entropy <= 0:
        return 0.0

    try:
        return (2**entropy) / GUESSES_PER_SECOND
    except OverflowError:
        return float("inf")


def seconds_to_human(seconds: float) -> str:
    if seconds == float("inf"):
        return "longer than measurable"
    if seconds < 1:
        return "<1 second"
    if seconds < 60:
        return f"{round(seconds)} seconds"
    if seconds < 3600:
        return f"{round(seconds / 60)} minutes"
    if seconds < 86_400:
        return f"{round(seconds / 3600)} hours"

    years = seconds / 31_536_000
    if years < 1:
        return f"{round(seconds / 86_400)} days"
    if years < 1_000:
        return f"{round(years)} years"
    if years < 1_000_000:
        return f"{round(years / 1_000)}k years"
    if years < 1_000_000_000:
        return f"{round(years / 1_000_000)}m years"
    return f"{round(years / 1_000_000_000)}b years"


async def check_breach(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(HIBP_RANGE_URL.format(prefix=prefix))
            response.raise_for_status()
    except httpx.HTTPError:
        return False

    for line in response.text.splitlines():
        returned_suffix = line.split(":", 1)[0]
        if returned_suffix == suffix:
            return True

    return False


def generate_tips(rules: Dict[str, bool], breached: bool) -> List[str]:
    tips: List[str] = []

    if breached:
        tips.append("This password was found in a breach. Do not use it.")
    if not rules["length_8"]:
        tips.append("Use at least 8 characters.")
    if not rules["length_12"]:
        tips.append("Use 12 or more characters for stronger protection.")
    if not rules["uppercase"]:
        tips.append("Add an uppercase letter.")
    if not rules["digits"]:
        tips.append("Include a number.")
    if not rules["symbols"]:
        tips.append("Add a symbol such as !, @, #, or $.")
    if not tips:
        tips.append("Great password. A memorable passphrase is also a good option.")

    return tips[:3]
