import json
from pathlib import Path

from cti_misp_opencti_lab.input import load_observables
from cti_misp_opencti_lab.misp import build_misp_event
from cti_misp_opencti_lab.stix import build_stix_bundle


def test_misp_export_contains_attributes() -> None:
    observables = load_observables(Path("examples/observables.csv"))
    event = build_misp_event(observables, info="test event")
    attributes = event["Event"]["Attribute"]
    assert event["Event"]["info"] == "test event"
    assert len(attributes) == len(observables)
    assert {attribute["type"] for attribute in attributes} >= {"ip-src", "domain", "url", "sha256", "email-src"}


def test_stix_export_contains_indicators() -> None:
    observables = load_observables(Path("examples/observables.csv"))
    bundle = build_stix_bundle(observables)
    indicators = [item for item in bundle["objects"] if item["type"] == "indicator"]
    assert bundle["type"] == "bundle"
    assert len(indicators) == len(observables)
    assert any("domain-name:value" in indicator["pattern"] for indicator in indicators)
    json.dumps(bundle)

