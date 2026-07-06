from __future__ import annotations

import csv
from pathlib import Path

from .models import Observable
from .normalize import normalize_observable


def load_observables(path: Path) -> list[Observable]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    observables = _load_csv(path) if path.suffix.lower() == ".csv" else _load_txt(path)
    seen: set[tuple[str, str]] = set()
    deduped: list[Observable] = []
    for observable in observables:
        if observable.key in seen or observable.type == "unknown":
            continue
        seen.add(observable.key)
        deduped.append(observable)
    return deduped


def _load_txt(path: Path) -> list[Observable]:
    observables: list[Observable] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        observable = normalize_observable(line)
        if observable:
            observables.append(observable)
    return observables


def _load_csv(path: Path) -> list[Observable]:
    observables: list[Observable] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            raw = row.get("observable") or row.get("value") or row.get("indicator") or ""
            tags = [item.strip() for item in (row.get("tags") or "").split(",") if item.strip()]
            confidence = int(row.get("confidence") or 50)
            observable = normalize_observable(
                raw,
                explicit_type=row.get("type"),
                source=row.get("source") or "manual",
                confidence=confidence,
                tlp=row.get("tlp") or "TLP:CLEAR",
                tags=tags,
            )
            if observable:
                observables.append(observable)
    return observables

