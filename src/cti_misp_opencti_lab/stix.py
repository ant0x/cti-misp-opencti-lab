from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from .models import Observable

TLP_MARKINGS = {
    "TLP:CLEAR": "marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9",
    "TLP:GREEN": "marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da",
    "TLP:AMBER": "marking-definition--f88d31f6-486f-44da-b317-01333bde0b82",
    "TLP:RED": "marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed",
}


def build_stix_bundle(observables: list[Observable]) -> dict:
    objects = [_identity()]
    objects.extend(_indicator(observable) for observable in observables)
    return {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": objects,
    }


def render_stix_json(observables: list[Observable]) -> str:
    return json.dumps(build_stix_bundle(observables), indent=2, sort_keys=True)


def _identity() -> dict:
    now = _now()
    return {
        "type": "identity",
        "spec_version": "2.1",
        "id": "identity--5df68d48-3a84-4c6f-8b8b-2de26a27d0aa",
        "created": now,
        "modified": now,
        "name": "CTI MISP OpenCTI Lab",
        "identity_class": "organization",
    }


def _indicator(observable: Observable) -> dict:
    now = _now()
    labels = ["malicious-activity", *observable.tags]
    return {
        "type": "indicator",
        "spec_version": "2.1",
        "id": f"indicator--{uuid.uuid4()}",
        "created": now,
        "modified": now,
        "created_by_ref": "identity--5df68d48-3a84-4c6f-8b8b-2de26a27d0aa",
        "name": f"{observable.type}: {observable.value}",
        "description": f"Source: {observable.source}; confidence: {observable.confidence}",
        "indicator_types": ["malicious-activity"],
        "pattern": _pattern(observable),
        "pattern_type": "stix",
        "valid_from": now,
        "labels": labels,
        "confidence": observable.confidence,
        "object_marking_refs": [TLP_MARKINGS.get(observable.tlp, TLP_MARKINGS["TLP:CLEAR"])],
    }


def _pattern(observable: Observable) -> str:
    escaped = observable.value.replace("\\", "\\\\").replace("'", "\\'")
    if observable.type in {"ipv4", "ipv6"}:
        stix_type = "ipv4-addr" if observable.type == "ipv4" else "ipv6-addr"
        return f"[{stix_type}:value = '{escaped}']"
    if observable.type == "domain":
        return f"[domain-name:value = '{escaped}']"
    if observable.type == "url":
        return f"[url:value = '{escaped}']"
    if observable.type == "email":
        return f"[email-addr:value = '{escaped}']"
    if observable.type in {"md5", "sha1", "sha256"}:
        algo = {"md5": "MD5", "sha1": "SHA-1", "sha256": "SHA-256"}[observable.type]
        return f"[file:hashes.'{algo}' = '{escaped}']"
    return f"[x-observable:value = '{escaped}']"


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

