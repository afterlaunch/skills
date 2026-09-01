#!/usr/bin/env python3
"""Reconcile the board against what the founder has ACTUALLY replied to.

The problem this exists for. The desk (or a product feeding it) surfaces a
thread and suggests a reply. The founder may have already replied, from a
phone, an hour ago, outside the desk entirely. Reddit has no readable API,
so nothing here can know that. The board then offers work already done, and
a board that does that twice stops being trusted.

The cheap fix is not to check twenty threads. It is to read ONE page: his
own comment history at reddit.com/user/<handle>/comments, which a desk
session can load in the logged-in browser. Every comment there names the
thread it belongs to. Paste those URLs in here and the board corrects
itself.

Usage, from a desk session with the browser open:

    python3 reddit/reconcile.py < urls.txt
    python3 reddit/reconcile.py "https://reddit.com/r/SaaS/comments/1abc/x/comment/p123/"

Then rebuild the board:

    python3 reddit/reindex.py

What it does NOT do: judge the comment, edit it, or decide whether it
broke a sub rule. It records that we are already in the thread. A session
reads the comment and decides the rest.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

# The desk's DATA lives in the content estate outside the repo
# (~/.claude/content/reddit, see .claude/skills/MOVED.md); this script is the
# code and lives in the repo. REDDIT_DESK overrides the estate path.
import os
# The estate. REDDIT_DESK still wins for anyone already using it; otherwise
# this skill lives under the suite's shared SKILLS_ESTATE, so one variable
# configures the whole pack.
def _estate():
    import os
    from pathlib import Path
    explicit = os.environ.get('REDDIT_DESK')
    if explicit:
        return Path(explicit).resolve()
    shared = os.environ.get('SKILLS_ESTATE')
    root = Path(shared) if shared else Path.home() / '.claude' / 'content'
    return (root / 'reddit').resolve()

MAX_INPUT_BYTES = 4 * 1024 * 1024  # a permalink list is kilobytes
HERE = _estate()
THREADS = HERE / 'threads'

# A permalink from a profile page carries everything we need: the sub, the
# thread, and the comment itself. Accepts old./new./np. and any title slug.
# Bounded to what Reddit itself allows (a subreddit name is 3 to 21
# characters, ids are short base36). Unbounded groups let a malformed paste
# build a filename past the filesystem limit, which crashed the run with a
# traceback instead of skipping the line (security review, 2026-08-31).
LINK = re.compile(
    r'reddit\.com/r/(?P<sub>[A-Za-z0-9_]{2,24})/comments/(?P<thread>[a-z0-9]{1,16})'
    r'(?:/[^/]*)?(?:/comment/(?P<comment>[a-z0-9]{1,16}))?',
    re.I,
)


def slug(sub: str) -> str:
    return sub.lower()


def field_line(text: str, name: str) -> str | None:
    m = re.search(rf'^- \*\*{re.escape(name)}:\*\* (.*)$', text, re.M)
    return m.group(1) if m else None


def set_field(text: str, name: str, value: str) -> str:
    pattern = rf'^- \*\*{re.escape(name)}:\*\* .*$'
    if re.search(pattern, text, re.M):
        return re.sub(pattern, f'- **{name}:** {value}', text, count=1, flags=re.M)
    return text


def stub(sub: str, thread: str, comment: str | None) -> str:
    """A thread we have replied in but never filed.

    Deliberately thin. We know we commented and nothing else: no title, no
    date, no read of the thread. Marked so a later session knows the gap is
    real rather than an oversight.
    """
    url = f'https://www.reddit.com/r/{sub}/comments/{thread}/'
    reply = f'{url}comment/{comment}/' if comment else '-'
    return '\n'.join([
        f'# (unread) r/{sub} thread {thread}',
        '',
        f'- **Sub:** r/{sub}',
        f'- **Id:** {thread}',
        f'- **URL:** {url}',
        '- **Posted:** unknown',
        f'- **First seen:** {date.today().isoformat()}',
        f'- **Last checked:** {date.today().isoformat()} | comments unknown',
        '- **Status:** replied',
        f'- **Our reply:** {reply}',
        '- **Product:** unknown',
        '- **Claims:** -',
        '- **Why:** Found on his own comment history during reconciliation. '
        'We are already in this thread and nobody filed it. Open it once to '
        'record what was said and whether it broke a sub rule.',
        '',
    ])


def main() -> int:
    # The estate may not exist yet. The desk's documented first run is this
    # script then reindex.py, and on a fresh machine there is no comment
    # history to paste, so this used to return before creating threads/ and
    # reindex.py died on the missing directory. Create it before any early
    # return, parents included, so the first run works on an empty estate.
    THREADS.mkdir(parents=True, exist_ok=True)

    raw = sys.argv[1:] or sys.stdin.read(MAX_INPUT_BYTES).split()
    if not raw:
        print('Nothing to reconcile. Paste comment permalinks, one per line.')
        return 1

    # Keyed on the lowercased sub because that is the filename convention,
    # but the ORIGINAL case is carried through to every URL we write. Reddit
    # does not care, and a board full of "r/saas" next to "r/SaaS" reads as
    # machine output.
    seen: dict[tuple[str, str], tuple[str, str | None]] = {}
    for token in raw:
        m = LINK.search(token)
        if m:
            seen[(slug(m.group('sub')), m.group('thread'))] = (m.group('sub'), m.group('comment'))

    if not seen:
        print(f'No Reddit permalinks found in {len(raw)} lines. Nothing changed.')
        return 1

    marked, already, created = [], [], []

    for (key, thread), (sub, comment) in sorted(seen.items()):
        path = THREADS / f'{key}__{thread}.md'
        reply_url = (
            f'https://www.reddit.com/r/{sub}/comments/{thread}/comment/{comment}/'
            if comment
            else '-'
        )

        if not path.exists():
            path.write_text(stub(sub, thread, comment))
            created.append(f'r/{sub} {thread}')
            continue

        text = path.read_text()
        status = field_line(text, 'Status') or 'seen'

        # 'fix' means a session already read the comment and wants it edited.
        # Reconciliation must never quietly downgrade that to a tidy 'replied'.
        if status == 'fix':
            already.append(f'r/{sub} {thread} (left as fix-first)')
            continue

        if status == 'replied' and field_line(text, 'Our reply') not in (None, '-'):
            already.append(f'r/{sub} {thread}')
            continue

        text = set_field(text, 'Status', 'replied')
        text = set_field(text, 'Our reply', reply_url)
        why = field_line(text, 'Why') or ''
        text = set_field(
            text,
            'Why',
            f'{why} RECONCILED {date.today().isoformat()}: he had already '
            f'replied here, outside the board.'.strip(),
        )
        path.write_text(text)
        marked.append(f'r/{sub} {thread}')

    print(f'{len(seen)} comments read from his history\n')
    if marked:
        print(f'  {len(marked)} threads corrected, the board was offering work already done:')
        for m in marked:
            print(f'    {m}')
        print('')
    if created:
        print(f'  {len(created)} threads we had never filed, stubbed as replied:')
        for c in created:
            print(f'    {c}')
        print('')
    if already:
        print(f'  {len(already)} already recorded, left alone')
    print('\nNow run: python3 reddit/reindex.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
