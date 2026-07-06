# Contributing

Contributions are welcome for CTI mappings, export formats and normalization improvements.

## Local Setup

```bash
python -m pip install -e ".[dev]"
pytest
cti-lab convert -i examples/observables.csv
```

## Guidelines

- Keep exports transparent and easy to inspect.
- Do not include live customer indicators unless they are safe to share.
- Add tests for new observable types and mapping logic.
- Keep optional platform API integrations disabled by default.

