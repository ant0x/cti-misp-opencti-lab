from __future__ import annotations

import argparse
from pathlib import Path

from .input import load_observables
from .misp import render_misp_json
from .report import render_markdown, render_observables_json
from .stix import render_stix_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize CTI observables and export MISP/STIX outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert = subparsers.add_parser("convert", help="Convert observables to MISP/STIX/report outputs.")
    convert.add_argument("-i", "--input", required=True, type=Path, help="Input .txt or .csv file.")
    convert.add_argument("--misp", type=Path, help="Write MISP event JSON.")
    convert.add_argument("--stix", type=Path, help="Write STIX 2.1 bundle JSON for OpenCTI-style workflows.")
    convert.add_argument("--json", type=Path, help="Write normalized observables JSON.")
    convert.add_argument("--markdown", type=Path, help="Write analyst Markdown report.")
    convert.add_argument("--event-info", default="CTI Exchange Lab Export", help="MISP event info field.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "convert":
        observables = load_observables(args.input)
        outputs = {
            args.misp: render_misp_json(observables, info=args.event_info) if args.misp else None,
            args.stix: render_stix_json(observables) if args.stix else None,
            args.json: render_observables_json(observables) if args.json else None,
            args.markdown: render_markdown(observables) if args.markdown else None,
        }
        if not any(outputs.values()):
            print(render_markdown(observables))
            return 0
        for path, content in outputs.items():
            if path and content is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

