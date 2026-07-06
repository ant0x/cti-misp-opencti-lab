from cti_misp_opencti_lab.normalize import normalize_observable


def test_normalizes_url_tracking_params() -> None:
    observable = normalize_observable("HTTPS://Example.com/login/?utm_source=x&token=1")
    assert observable is not None
    assert observable.type == "url"
    assert observable.value == "https://example.com/login?token=1"


def test_detects_sha256() -> None:
    value = "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f"
    observable = normalize_observable(value)
    assert observable is not None
    assert observable.type == "sha256"

