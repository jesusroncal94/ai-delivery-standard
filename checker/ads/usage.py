import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from statistics import median

HANDOFF_THRESHOLD = 200_000
WORKTREE_MARKER = "--claude-worktrees-"


@dataclass
class Session:
    project: str
    file: str
    contexts: list[int] = field(default_factory=list)
    cache_read: int = 0
    cache_write: int = 0
    uncached_input: int = 0
    output: int = 0
    first: str = ""
    last: str = ""

    @property
    def calls(self) -> int:
        return len(self.contexts)

    @property
    def mean_context(self) -> int:
        return sum(self.contexts) // self.calls if self.calls else 0

    @property
    def p50(self) -> int:
        return int(median(self.contexts)) if self.contexts else 0

    @property
    def p90(self) -> int:
        return percentile(self.contexts, 0.9)

    @property
    def over_threshold(self) -> bool:
        return self.mean_context > HANDOFF_THRESHOLD


def percentile(values: list[int], q: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(q * len(ordered)))]


def read_session(path: Path, project: str) -> Session:
    session = Session(project=project, file=path.name)
    seen: set[str] = set()
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if '"assistant"' not in line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = record.get("message") or {}
            usage = message.get("usage")
            if record.get("type") != "assistant" or not usage or message.get("id") in seen:
                continue
            seen.add(message.get("id"))
            read = usage.get("cache_read_input_tokens", 0)
            write = usage.get("cache_creation_input_tokens", 0)
            fresh = usage.get("input_tokens", 0)
            session.contexts.append(read + write + fresh)
            session.cache_read += read
            session.cache_write += write
            session.uncached_input += fresh
            session.output += usage.get("output_tokens", 0)
            stamp = record.get("timestamp", "")[:10]
            session.first = session.first or stamp
            session.last = stamp or session.last
    return session


def project_label(folder: str, prefix: str) -> str:
    worktree = WORKTREE_MARKER in folder
    name = folder.split(WORKTREE_MARKER)[0]
    name = name[len(prefix):].lstrip("-") if name.startswith(prefix) else name
    return f"{name or '(root)'}{' (worktree)' if worktree else ''}"


def read_transcripts(root: Path, prefix: str | None = None) -> list[Session]:
    folders = sorted(p for p in root.iterdir() if p.is_dir())
    common = prefix if prefix is not None else os.path.commonprefix([f.name for f in folders]).rstrip("-")
    sessions = [
        read_session(transcript, project_label(folder.name, common))
        for folder in folders
        for transcript in sorted(folder.glob("*.jsonl"))
    ]
    return [s for s in sessions if s.calls]


def summary(sessions: list[Session]) -> dict:
    cache_read = sum(s.cache_read for s in sessions)
    all_input = cache_read + sum(s.cache_write + s.uncached_input for s in sessions)
    long_sessions = [s for s in sessions if s.over_threshold]
    return {
        "sessions": len(sessions),
        "calls": sum(s.calls for s in sessions),
        "cache_read_share": round(cache_read / all_input, 3) if all_input else 0,
        "sessions_over_threshold": len(long_sessions),
        "cache_read_share_of_long_sessions": round(sum(s.cache_read for s in long_sessions) / cache_read, 3) if cache_read else 0,
        "output_tokens": sum(s.output for s in sessions),
    }
