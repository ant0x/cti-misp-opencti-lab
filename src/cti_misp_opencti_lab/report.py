from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict

from .models import Observable


def render_observables_json(observables: list[Observable]) -> str:
    return json.dumps([asdict(observable) for observable in observables], indent=2, sort_keys=True)


def render_markdown(observables: list[Observable]) -> str:
    counts = Counter(observable.type for observable in observables)
    lines = ["# CTI Exchange Report", "", f"Total observables: **{len(observables)}**", "", "## By Type", ""]
    for key, count in sorted(counts.items()):
        lines.append(f"- `{key}`: {count}")
    lines.extend(["", "## Observables", "", "| Type | Value | Source | Confidence | TLP | Tags |", "| --- | --- | --- | ---: | --- | --- |"])
    for observable in observables:
        tags = ", ".join(f"`{tag}`" for tag in observable.tags) or "n/a"
        lines.append(f"| `{observable.type}` | `{observable.value}` | {observable.source} | {observable.confidence} | `{observable.tlp}` | {tags} |")
    lines.append("")
    return "\n".join(lines)

