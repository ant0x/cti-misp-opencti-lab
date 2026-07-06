# CTI MISP OpenCTI Lab

A small CTI exchange lab for normalizing observables and producing portable outputs for MISP and OpenCTI-style workflows.

The tool takes IPs, domains, URLs, hashes or email addresses from `.txt` or `.csv`, deduplicates and normalizes them, then exports:

- MISP event JSON
- STIX 2.1 bundle JSON for OpenCTI-style ingestion workflows
- normalized observables JSON
- analyst Markdown report

## Why This Exists

MISP and OpenCTI are powerful CTI platforms, but many workflows still start from small lists of observables gathered during triage, OSINT research or incident response. This lab focuses on that practical exchange layer: clean the indicators, preserve useful context, and generate structured outputs.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Usage

Generate all outputs:

```bash
cti-lab convert \
  -i examples/observables.csv \
  --misp reports/misp-event.json \
  --stix reports/stix-bundle.json \
  --json reports/observables.json \
  --markdown reports/report.md
```

Print a Markdown report to stdout:

```bash
cti-lab convert -i examples/observables.txt
```

## CSV Format

```csv
observable,type,source,confidence,tlp,tags
8.8.8.8,ipv4,manual,30,TLP:CLEAR,"osint,dns"
malicious-example.test,domain,osint-feed,80,TLP:AMBER,"phishing"
```

Only `observable` is required. If `type` is empty, the CLI tries to detect it.

## Supported Observable Types

- IPv4
- IPv6
- Domain
- URL
- MD5
- SHA1
- SHA256
- Email address

## MISP Output

The generated MISP JSON uses a simple `Event` object with attributes mapped to common MISP types:

- `ipv4` / `ipv6` -> `ip-src`
- `domain` -> `domain`
- `url` -> `url`
- `md5`, `sha1`, `sha256` -> matching hash type
- `email` -> `email-src`

## STIX / OpenCTI Output

The STIX output is a STIX 2.1 bundle with one `identity` object and one `indicator` object per observable. It includes:

- STIX indicator patterns
- confidence
- labels from tags
- TLP marking references

## Roadmap

- Optional MISP API push
- Optional OpenCTI API import helper
- Relationship objects for campaigns, malware and threat actors
- ATT&CK technique tagging
- TAXII collection export example

## Disclaimer

This project is for defensive security, CTI learning and lab workflows. Validate data quality and sharing rules before importing indicators into production CTI platforms.

