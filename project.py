"""Compare what competing ad openings show during the same time window."""

import math


def items(data, key, *, allow_empty=False):
    value = data.get(key) if isinstance(data, dict) else None
    if not isinstance(value, list) or (not value and not allow_empty) or len(value) > 500:
        raise ValueError(f"{key} must be a list of up to 500 entries")
    if any(not isinstance(item, dict) for item in value):
        raise ValueError(f"Every entry in {key} must be an object")
    return value


def number(value, field, *, positive=False):
    if type(value) not in (int, float) or not 0 <= value <= 1e12 or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite nonnegative number at most 1e12")
    if positive and value == 0:
        raise ValueError(f"{field} must be greater than zero")
    return value


def label(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


TITLE = "Hook Cut Lab"
DESCRIPTION = "Compare when each ad opening shows its product, promise and proof."
PROMPT = "Compare these openings for a creative review. Describe the timing tradeoffs and propose a single controlled A/B edit. Cite the measured beats. Never predict viewing, click or sales outcomes."
FEATURES = {"product", "promise", "proof", "context", "title"}


def covered(intervals):
    total = 0
    cursor = 0
    for start, end in sorted(intervals):
        total += max(0, end - max(start, cursor))
        cursor = max(cursor, end)
    return total


def analyze(data: dict) -> dict:
    variants = items(data, "variants")
    window = number(data.get("window_seconds", 3), "window_seconds", positive=True)
    rows = []
    seen = set()
    for variant in variants:
        name = label(variant.get("name"), "name")
        if name in seen:
            raise ValueError("Variant names must be unique")
        seen.add(name)
        spans = {feature: [] for feature in FEATURES}
        for beat in items(variant, "beats", allow_empty=True):
            start = number(beat.get("start"), "start")
            end = number(beat.get("end"), "end")
            features = beat.get("features")
            if end <= start or not isinstance(features, list) or not features:
                raise ValueError("Each beat needs a positive interval and at least one feature")
            for raw in features:
                feature = label(raw, "feature").casefold()
                if feature not in FEATURES:
                    raise ValueError(f"Unknown beat feature: {feature}")
                if start < window:
                    spans[feature].append((start, min(window, end)))
        def first(feature):
            return round(min(x[0] for x in spans[feature]), 3) if spans[feature] else "Absent"
        rows.append({"Opening": name, "Product visible (s)": round(covered(spans["product"]), 3),
                     "First promise (s)": first("promise"), "First proof (s)": first("proof")})
    with_proof = sum(r["First proof (s)"] != "Absent" for r in rows)
    return {"summary": f"{with_proof} of {len(rows)} openings show proof in the first {window:g} seconds.",
            "metrics": {"Openings": len(rows), "Window (s)": window, "With early proof": with_proof}, "rows": rows}
