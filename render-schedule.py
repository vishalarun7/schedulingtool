import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

@dataclass
class Entry:
    user: str
    start: datetime
    end: datetime


@dataclass
class Schedule:
    users: List[str]
    start: datetime
    interval: timedelta

def parse_time(s: str) -> datetime:
    return datetime.strptime(s, TIME_FORMAT)


def format_time(t: datetime) -> str:
    return t.strftime(TIME_FORMAT)


def read_json_file(path: str):
    with open(path) as f:
        lines = (line for line in f if not line.lstrip().startswith("//"))
        text = "\n".join(lines)
    return json.loads(text)


def parse_args():
    p = argparse.ArgumentParser(description="Render an on-call schedule.")
    p.add_argument("--schedule", required=True)
    p.add_argument("--overrides", required=True)
    p.add_argument("--from", dest="from_", required=True)
    p.add_argument("--until", required=True)
    return p.parse_args()


def load_schedule(path: str) -> Schedule:
    j = read_json_file(path)
    return Schedule(
        users=j["users"],
        start=parse_time(j["handover_start_at"]),
        interval=timedelta(days=j["handover_interval_days"]),
    )


def print_json(entries: List[Entry]) -> None:
    out = [
        {"user": e.user, "start_at": format_time(e.start), "end_at": format_time(e.end)}
        for e in entries
    ]
    print(json.dumps(out, indent=2))


def load_overrides(path: str) -> List[Entry]:
    j = read_json_file(path)
    return [Entry(user=o["user"], start=parse_time(o["start_at"]), end=parse_time(o["end_at"])) for o in j]


def project(s: Schedule, frm: datetime, until: datetime) -> List[Entry]:
    result = []
    if not s.users:
        return result
    k = 0 if frm <= s.start else (frm - s.start) // s.interval
    n = len(s.users)
    while True:
        shift_start = s.start + k * s.interval
        if shift_start >= until:
            break
        shift_end = shift_start + s.interval
        result.append(Entry(s.users[k % n], shift_start, shift_end))
        k += 1
    return result


def overlay(base: List[Entry], overrides: List[Entry]) -> List[Entry]:
    result = list(base)
    for o in overrides:
        nxt = []
        for e in result:
            before = Entry(e.user, e.start, min(e.end, o.start))
            if before.end > before.start:
                nxt.append(before)
            after = Entry(e.user, max(e.start, o.end), e.end)
            if after.end > after.start:
                nxt.append(after)
        nxt.append(o)
        result = nxt
    result.sort(key=lambda e: e.start)
    return result


def clip(entries: List[Entry], frm: datetime, until: datetime) -> List[Entry]:
    result = []
    for e in entries:
        start = max(e.start, frm)
        end = min(e.end, until)
        if end > start:
            result.append(Entry(e.user, start, end))
    return result


def main() -> int:
    args = parse_args()
    try:
        schedule = load_schedule(args.schedule)
        overrides = load_overrides(args.overrides)
        frm = parse_time(args.from_)
        until = parse_time(args.until)

        base = project(schedule, frm, until)
        combined = overlay(base, overrides)
        result = clip(combined, frm, until)

        print_json(result)
    except (OSError, ValueError, KeyError) as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
