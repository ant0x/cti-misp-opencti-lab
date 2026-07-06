from __future__ import annotations

import json
from datetime import UTC, datetime

from .models import Observable

MISP_TYPE_MAP = {
    "ipv4": "ip-src",
    "ipv6": "ip-src",
    "domain": "domain",
    "url": "url",
    "md5": "md5",
    "sha1": "sha1",
    "sha256": "sha256",
    "email": "email-src",
}


def build_misp_event(observables: list[Observable], *, info: str = "CTI Exchange Lab Export") -> dict:
    now = datetime.now(UTC).strftime("%Y-%m-%d")
    all_tags = sorted({tag for observable in observables for tag in observable.tags})
    return {
        "Event": {
            "info": info,
            "date": now,
            "distribution": "0",
            "threat_level_id": "2",
            "analysis": "1",
            "Tag": [{"name": tag} for tag in all_tags],
            "Attribute": [_attribute(observable) for observable in observables],
        }
    }


def render_misp_json(observables: list[Observable], *, info: str = "CTI Exchange Lab Export") -> str:
    return json.dumps(build_misp_event(observables, info=info), indent=2, sort_keys=True)


def _attribute(observable: Observable) -> dict:
    return {
        "type": MISP_TYPE_MAP[observable.type],
        "category": "Network activity" if observable.type in {"ipv4", "ipv6", "domain", "url"} else "Payload delivery",
        "value": observable.value,
        "to_ids": True,
        "distribution": "0",
        "comment": f"source={observable.source}; confidence={observable.confidence}; tlp={observable.tlp}",
        "Tag": [{"name": tag} for tag in observable.tags],
    }

