import argparse
import json
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .conformance import Result, evaluate
from .portfolio import evaluate_portfolio, read_registry, render_markdown
from .project import Project
from .usage import HANDOFF_THRESHOLD, read_transcripts, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ads", description="AI delivery standard tools")
    parser.add_argument("--version", action="version", version=f"ads {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="Check one repository against its profile and level")
    check.add_argument("path", nargs="?", default=".")
    check.add_argument("--profile")
    check.add_argument("--level", type=int)
    check.add_argument("--json", action="store_true")

    portfolio = commands.add_parser("portfolio", help="Check every project in a registry")
    portfolio.add_argument("registry")
    portfolio.add_argument("--output")
    portfolio.add_argument("--root", help="folder that holds the projects; overrides the registry's root:")

    usage = commands.add_parser("usage", help="Summarise context per call from Claude Code transcripts")
    usage.add_argument("transcripts", nargs="?", default="/transcripts")
    usage.add_argument("--prefix")
    usage.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    return {"check": run_check, "portfolio": run_portfolio, "usage": run_usage}[args.command](args)


def run_check(args) -> int:
    result = evaluate(Project.load(Path(args.path).resolve(), args.profile, args.level))
    print(json.dumps(result.as_dict(), indent=2) if args.json else render_result(result))
    return 0 if result.conforms else 1


def render_result(result: Result) -> str:
    project = result.project
    lines = [f"{project.root.name}: profile {project.profile}, target L{project.level}, achieved L{result.achieved}"]
    for outcome in result.outcomes:
        mark = "ok  " if outcome.passed else ("FAIL" if outcome.rule.level <= project.level else "next")
        lines.append(f"  {mark} {outcome.rule.id:<14} {outcome.rule.title}")
        lines += [f"         - {problem}" for problem in outcome.problems]
    lines.append("conforms" if result.conforms else f"does not conform: {len(result.failures())} failing rules")
    return "\n".join(lines)


def run_portfolio(args) -> int:
    root, entries = read_registry(Path(args.registry), Path(args.root) if args.root else None)
    rows = evaluate_portfolio(root, entries)
    report = render_markdown(rows, date.today().isoformat())
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    print(report)
    return 0


def run_usage(args) -> int:
    sessions = read_transcripts(Path(args.transcripts), args.prefix)
    if args.json:
        print(json.dumps({"summary": summary(sessions), "sessions": [vars(s) | {"p50": s.p50, "p90": s.p90} for s in sessions]}, indent=2, default=str))
        return 0
    print(f"{'project':<34} {'calls':>6} {'p50':>7} {'p90':>7} {'cacheR M':>9}  dates")
    for s in sorted(sessions, key=lambda s: s.cache_read, reverse=True):
        flag = "  > handoff" if s.over_threshold else ""
        print(f"{s.project[:34]:<34} {s.calls:>6} {s.p50 // 1000:>6}k {s.p90 // 1000:>6}k {s.cache_read / 1e6:>9.1f}  {s.first}..{s.last}{flag}")
    totals = summary(sessions)
    print(
        f"\n{totals['sessions']} sessions, {totals['calls']} calls; cache reads are {totals['cache_read_share']:.1%} of input; "
        f"{totals['sessions_over_threshold']} sessions average over {HANDOFF_THRESHOLD // 1000}k per call and carry "
        f"{totals['cache_read_share_of_long_sessions']:.1%} of cache reads"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
