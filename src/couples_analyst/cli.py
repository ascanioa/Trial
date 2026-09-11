"""Command-line entry point. Produces two artifacts per run: analysis.json and a report."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from . import __version__
from .compose import analyze, validate
from .report import render


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="couples-analyst",
        description=(
            "Descriptive coding of a couple's conversation transcript. Not a diagnosis, not "
            "a clinical assessment, not a prediction."
        ),
    )
    ap.add_argument("transcript", nargs="?", help="transcript file (default: stdin)")
    ap.add_argument("--format", choices=["plain", "speaker_turns", "chat_export", "subtitles"],
                    help="override input format detection")
    ap.add_argument("--language", choices=["en", "es"], help="override language detection")
    ap.add_argument("--keep-names", action="store_true",
                    help="preserve speaker names instead of anonymizing to A / B")
    ap.add_argument("--request", default="",
                    help="the user's stated purpose; screened for adversarial use")
    ap.add_argument("--json", dest="json_out", default="analysis.json",
                    help="where to write analysis.json (default: analysis.json)")
    ap.add_argument("--md", dest="md_out", default="report.md",
                    help="where to write the markdown report (default: report.md)")
    ap.add_argument("--stdout", action="store_true", help="also print the report")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if the output contract is violated")
    ap.add_argument("--version", action="version", version=f"couples-analyst {__version__}")
    args = ap.parse_args(argv)

    raw = (
        pathlib.Path(args.transcript).read_text(encoding="utf-8")
        if args.transcript
        else sys.stdin.read()
    )
    if not raw.strip():
        print("empty transcript", file=sys.stderr)
        return 2

    result = analyze(
        raw,
        input_format=args.format,
        anonymize=not args.keep_names,
        language=args.language,
        request_text=args.request,
    )
    if isinstance(result, str):  # adversarial-use refusal
        print(result, file=sys.stderr)
        return 3

    doc = result.to_json()
    problems = validate(doc)

    pathlib.Path(args.json_out).write_text(json.dumps(doc, ensure_ascii=False, indent=2))
    report = render(doc)
    pathlib.Path(args.md_out).write_text(report, encoding="utf-8")

    if args.stdout:
        print(report)
    else:
        print(f"wrote {args.json_out} and {args.md_out}", file=sys.stderr)

    if doc["safety_gate"]["tripped"]:
        print(
            "\nSafety markers present: the conflict-pattern analysis was withheld. "
            "See the report.",
            file=sys.stderr,
        )
    for p in problems:
        print(f"contract warning: {p}", file=sys.stderr)
    return 1 if (problems and args.strict) else 0


if __name__ == "__main__":
    raise SystemExit(main())
