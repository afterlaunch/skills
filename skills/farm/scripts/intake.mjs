#!/usr/bin/env node
// farm intake: the one door. Capture first, classify second, never fetch.
//
// Whoever finds the thing is usually on a phone. A phone can paste a link
// and almost nothing else, so the first job is to make sure the link cannot
// be lost, and the second is to say what kind of thing it is. Fetching is
// somebody else's job, later, possibly on another machine.
//
// THE RULE THIS SCRIPT EXISTS TO ENFORCE: capture never fails. No network
// call sits in front of the write. A source that cannot be reached still
// gets a file, with a reason recorded, and joins the drain queue. The old
// failure mode was asking for the text of an article to be pasted in while
// someone was out walking, which is a request that cannot be met and which
// lost the link.
//
// The classification is deliberately dumb: URL SHAPE ONLY, no network, no
// judgement. It answers one question, ACTOR or ITEM, because that is the
// fork that lets a single door serve both halves of the pipeline.
//
//   ACTOR  a profile, a subreddit, a channel, a site. Someone to watch.
//          Lands in a register and changes what the sweeps read.
//   ITEM   a post, a thread, a video, an article. Something to respond to
//          or mine. Lands in a lane and becomes a reply, a piece or a build.
//
// Everything past that is a judgement call and belongs in the session, with
// the content in front of it, not in a regex here.
//
// Usage:
//   node scripts/intake.mjs "<url or text>" --note "why this got grabbed"
//   node scripts/intake.mjs --drain          what is captured and unfinished
//   node scripts/intake.mjs "<url>" --json   machine-readable, for the skill
//
// The estate: everything this writes lives in one directory, outside any
// code repository, shared by every session that reads it. Default:
// ~/.claude/content. Override with SKILLS_ESTATE=/path (a test run, a second
// brand, a shared machine). With the env var unset this is byte-identical
// to a plain ~/.claude/content default.

import { writeFileSync, readFileSync, readdirSync, existsSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { homedir } from 'node:os';

const DEFAULT_ESTATE = join(homedir(), '.claude', 'content');
const ESTATE = process.env.SKILLS_ESTATE || DEFAULT_ESTATE;
// Hints printed below use this literal tilde form when the estate is the
// default, so unset-env-var output stays byte-identical to before this
// override existed; an explicit SKILLS_ESTATE shows its own real path instead.
const ESTATE_DISPLAY = process.env.SKILLS_ESTATE ? ESTATE : '~/.claude/content';
const INBOX = join(ESTATE, 'inbox');

const argv = process.argv.slice(2);
const asJson = argv.includes('--json');
const drain = argv.includes('--drain');

function flag(name) {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 ? argv[i + 1] : undefined;
}

// ---------------------------------------------------------------- classify

// Reachability is a property of the SOURCE, not of the machine, and it is
// recorded so a drain run can tell "nobody has got to this yet" apart from
// "this one needs a browser". Measured 2026-08-22: Reddit returns 403 to a
// plain fetch and old.reddit redirects to a login wall; LinkedIn has no
// public read at all. Both need a logged-in browser, so both are desk work.
const CHANNELS = [
  {
    channel: 'x',
    kind: 'item',
    reachable: true,
    test: /^https?:\/\/(?:www\.)?(?:twitter|x)\.com\/[^/]+\/status(?:es)?\/(\d+)/i,
    next: 'use a dedicated reply-drafting tool for this channel if one is set up, otherwise fetch it directly',
    lands: 'a reply brief, with whichever claims its triggers flagged',
  },
  {
    channel: 'x',
    kind: 'actor',
    reachable: true,
    test: /^https?:\/\/(?:www\.)?(?:twitter|x)\.com\/(?!home|explore|search|i\/|notifications)([A-Za-z0-9_]{1,15})\/?$/i,
    next: `add a row to ${ESTATE_DISPLAY}/x/WATCHLIST.md`,
    lands: 'the X watchlist, so the next sweep reads them',
  },
  {
    channel: 'reddit',
    kind: 'item',
    reachable: false,
    why: 'Reddit returns 403 to a plain fetch and old.reddit redirects to a login wall',
    test: /^https?:\/\/(?:www\.|old\.|np\.)?reddit\.com\/r\/([A-Za-z0-9_]+)\/comments\/([a-z0-9]+)/i,
    next: 'at the desk: open it in the browser, then write reddit/threads/<sub>__<id>.md',
    lands: 'the Reddit board, as a thread file',
  },
  {
    channel: 'reddit',
    kind: 'actor',
    reachable: false,
    why: 'Reddit needs a logged-in browser',
    test: /^https?:\/\/(?:www\.|old\.|np\.)?reddit\.com\/r\/([A-Za-z0-9_]+)\/?$/i,
    next: `add the sub to ${ESTATE_DISPLAY}/reddit/RULES.md and read its rules page`,
    lands: 'the Reddit venue list, with its own rulebook',
  },
  {
    channel: 'linkedin',
    kind: 'item',
    reachable: false,
    // Verified against the live API docs, version li-lms-2026-08: there is no
    // content search endpoint, and reading a member's posts needs
    // r_member_social, which the docs mark restricted to approved users. A
    // screenshot is the only read path that works from a phone.
    why: 'the LinkedIn API has no content search, and reading a member post needs the restricted r_member_social scope',
    test: /^https?:\/\/(?:www\.)?linkedin\.com\/(?:posts|feed\/update|pulse)\//i,
    next: 'screenshot it and send the image, which works from a phone. Otherwise open it at the desk',
    lands: 'the LinkedIn board once that channel exists',
  },
  {
    channel: 'linkedin',
    kind: 'actor',
    // Reachable because adding someone to a watchlist needs the URL and a
    // name, not the page. Only ITEMS on LinkedIn need a browser, so an actor
    // must not clog the desk queue behind them.
    reachable: true,
    test: /^https?:\/\/(?:www\.)?linkedin\.com\/(?:in|company|school)\/([^/?#]+)/i,
    next: `add a row to ${ESTATE_DISPLAY}/linkedin/WATCHLIST.md`,
    lands: 'the LinkedIn watchlist',
  },
  {
    channel: 'youtube',
    kind: 'item',
    reachable: true,
    test: /^https?:\/\/(?:(?:www\.|m\.)?youtube\.com\/watch\?[^#]*\bv=|youtu\.be\/)([A-Za-z0-9_-]{6,})/i,
    next: 'pull the transcript with whatever transcript tool is set up, or fall back to the page itself',
    lands: 'ideas/ or EXPERIMENTS.md, depending on what the transcript carries',
  },
  {
    channel: 'youtube',
    kind: 'actor',
    reachable: true,
    test: /^https?:\/\/(?:www\.)?youtube\.com\/(?:@[^/?#]+|channel\/[^/?#]+|c\/[^/?#]+)\/?$/i,
    next: `add a youtube: line to ${ESTATE_DISPLAY}/SOURCES.md`,
    lands: 'the source watchlist',
  },
];

function classify(input) {
  const raw = String(input ?? '').trim();

  if (!/^https?:\/\//i.test(raw)) {
    return {
      kind: 'item',
      channel: 'note',
      reachable: true,
      url: null,
      text: raw,
      next: 'judge it in session against the three lanes',
      lands: 'inbox/, until a drain run judges it',
    };
  }

  for (const c of CHANNELS) {
    const m = raw.match(c.test);
    if (m) {
      return {
        kind: c.kind,
        channel: c.channel,
        reachable: c.reachable,
        why: c.why,
        url: raw,
        ref: m[2] ?? m[1] ?? null,
        next: c.next.replace('<url>', raw),
        lands: c.lands,
      };
    }
  }

  // Anything else on the open web. A bare host is a publication worth
  // subscribing to; a path is one article worth reading. That is the same
  // actor/item split, applied to the part of the internet with no API.
  let u;
  try {
    u = new URL(raw);
  } catch {
    return { kind: 'item', channel: 'note', reachable: true, url: null, text: raw, next: 'judge it in session', lands: 'inbox/' };
  }

  const bare = u.pathname === '/' || u.pathname === '';
  return bare
    ? {
        kind: 'actor',
        channel: 'web',
        reachable: true,
        url: raw,
        ref: u.hostname,
        next: `add a page: line to ${ESTATE_DISPLAY}/SOURCES.md`,
        lands: 'the source watchlist',
      }
    : {
        kind: 'item',
        channel: 'web',
        reachable: true,
        url: raw,
        ref: u.hostname,
        next: 'WebFetch it, then sort the ideas into lanes',
        lands: 'sources/ plus whichever lanes it opens',
      };
}

// ---------------------------------------------------------------- capture

function slugify(s) {
  return (
    String(s)
      .toLowerCase()
      .replace(/^https?:\/\//, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 48) || 'capture'
  );
}

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
}

function capture(c, note) {
  if (!existsSync(INBOX)) mkdirSync(INBOX, { recursive: true });
  const path = join(INBOX, `${stamp()}-${slugify(c.url ?? c.text ?? 'note')}.md`);

  // Frontmatter is newline-joined, prose is blank-line-joined. Joining the
  // whole thing with blank lines produces frontmatter that no YAML parser
  // will read, which would make these files invisible to reindex.py.
  const front = [
    '---',
    `captured: ${new Date().toISOString()}`,
    `kind: ${c.kind}`,
    `channel: ${c.channel}`,
    `reachable: ${c.reachable}`,
    'state: captured',
    '---',
  ].join('\n');

  const prose = [
    c.url ? `<${c.url}>` : '',
    note ? `**Why I grabbed it:** ${note}` : '_No note. Judge it cold on the drain run._',
    c.text && !c.url ? c.text : '',
    c.reachable ? '' : `**Deferred.** ${c.why ?? 'Needs a logged-in browser.'}. Finish this at the desk.`,
    `**Next:** ${c.next}`,
  ]
    .filter(Boolean)
    .join('\n\n');

  writeFileSync(path, `${front}\n\n${prose}\n`);
  return path;
}

// ---------------------------------------------------------------- drain

function drainList() {
  if (!existsSync(INBOX)) return [];
  const out = [];
  for (const f of readdirSync(INBOX).sort()) {
    if (!f.endsWith('.md')) continue;
    const text = readFileSync(join(INBOX, f), 'utf8');
    if (!/^state:\s*captured\s*$/m.test(text)) continue;
    const get = (k) => (text.match(new RegExp(`^${k}:\\s*(.+)$`, 'm')) ?? [])[1]?.trim();
    const url = (text.match(/^<(https?:\/\/[^>]+)>$/m) ?? [])[1];
    out.push({
      file: f,
      kind: get('kind'),
      channel: get('channel'),
      reachable: get('reachable') === 'true',
      captured: get('captured'),
      url,
    });
  }
  return out;
}

// ---------------------------------------------------------------- main

if (drain) {
  const items = drainList();
  if (asJson) {
    console.log(JSON.stringify(items, null, 2));
  } else if (!items.length) {
    console.log('Nothing captured and unfinished. The inbox is drained.');
  } else {
    const ready = items.filter((i) => i.reachable);
    const desk = items.filter((i) => !i.reachable);
    console.log(`${items.length} captured and not yet processed\n`);
    if (ready.length) {
      console.log(`  ${ready.length} can be finished anywhere:`);
      for (const i of ready) console.log(`    ${i.channel}/${i.kind}  ${i.url ?? i.file}`);
      console.log('');
    }
    if (desk.length) {
      console.log(`  ${desk.length} need the browser, so they are desk work:`);
      for (const i of desk) console.log(`    ${i.channel}/${i.kind}  ${i.url ?? i.file}`);
    }
  }
  process.exit(0);
}

// The first bare argument, skipping whatever follows --note. Guard the
// no-note case explicitly: indexOf returns -1, and -1 + 1 is 0, which would
// silently skip the URL itself.
const noteIdx = argv.indexOf('--note');
const input = argv.find((a, i) => !a.startsWith('--') && !(noteIdx >= 0 && i === noteIdx + 1));

if (!input) {
  console.error('Need something to farm: a URL, or text in quotes.');
  console.error('  node scripts/intake.mjs "https://x.com/someone/status/123" --note "good thread"');
  console.error('  node scripts/intake.mjs --drain');
  process.exit(1);
}

const c = classify(input);

// --dry classifies without filing. For checking what a shape resolves to
// without leaving a file behind, which is also how the routing table is
// tested. Never use it in the real flow: an unfiled capture is a lost one.
if (argv.includes('--dry')) {
  console.log(`${c.kind.padEnd(5)} ${c.channel.padEnd(9)} ${c.reachable ? 'reachable' : 'needs browser'}  ${c.next}`);
  process.exit(0);
}

const path = capture(c, flag('note'));

if (asJson) {
  console.log(JSON.stringify({ ...c, captured: path }, null, 2));
} else {
  console.log('farm intake');
  console.log(`  ${c.kind.toUpperCase()} on ${c.channel}${c.reachable ? '' : '  (needs a browser)'}`);
  console.log(`  captured: ${path}`);
  if (!c.reachable) console.log(`  deferred: ${c.why}`);
  console.log('');
  console.log(`  lands in: ${c.lands}`);
  console.log(`  next:     ${c.next}`);
}
