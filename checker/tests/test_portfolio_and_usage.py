from ads.portfolio import evaluate_portfolio, read_registry, render_markdown
from ads.usage import read_transcripts, summary

from conftest import FIXTURES


def test_portfolio_report_lists_every_project(render, tmp_path):
    render("api", profile="service", level=2)
    registry = tmp_path / "portfolio.yaml"
    registry.write_text(
        "root: .\nprojects:\n"
        "  - {path: api, profile: service, target: 2}\n"
        "  - {path: gone, profile: demo, target: 1}\n",
        encoding="utf-8",
    )

    report = render_markdown(evaluate_portfolio(*read_registry(registry)), "2026-10-28")

    assert "| api | service | active | L2 | ✅ L" in report
    assert "| gone | demo | active | L1 | — | folder not found |" in report
    assert "1 of 2 checked projects meet their target level." in report


def test_usage_measures_context_per_call():
    sessions = {s.project: s for s in read_transcripts(FIXTURES / "transcripts")}

    long, short = sessions["alpha"], sessions["beta (worktree)"]
    assert long.calls == 2
    assert long.over_threshold
    assert short.calls == 2 and not short.over_threshold
    totals = summary(list(sessions.values()))
    assert totals["sessions_over_threshold"] == 1
    assert totals["cache_read_share_of_long_sessions"] == round(540_000 / 600_000, 3)
