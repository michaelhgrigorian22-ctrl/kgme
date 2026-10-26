import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { EventRow, OpenRun, Snapshot } from '../types'

// HANDOFF-0059 §2: the cockpit beside the chat. Every two seconds it asks the cockpit server
// on loopback for the events after its cursor and draws what comes back: the open runs and
// their states, the last events, the strip for an intent waiting on its outcome, the flood
// for a blocked run. Every run state is the server's (cockpit/render.py), never decided here
// (HANDOFF-0037's rule). It binds no key. When the server cannot be reached it says so and
// keeps the last snapshot.
const PANE = 'kgme-cockpit'
const EVENTS = 'http://127.0.0.1:8642/api/events'
const POLL_MS = 2000
const KEEP = 6
const EMPTY: Snapshot = { runs: [], events: [], cursor: '', isReached: false, wasReached: false, error: '' }
// Change the tag when a stored field changes: it declines what an earlier version stored.
const snapshot = atom({ plugin: 'kgme-cockpit', key: 'snapshot' } as const, EMPTY, { shape: 'snapshot-3' })
const COLOR: Record<string, string> = { working: 'cyan', waiting: 'yellow', transient: 'yellow', blocked: 'magenta' }
const GLYPH: Record<string, string> = { intent: '▶', outcome: '◀', note: '✎', approval: '✓' }

type ViewRun = { word?: unknown; quiet?: unknown; closed?: unknown; actor?: unknown; job?: unknown; last_ts?: unknown }
type ViewEvent = { id?: unknown; ts?: unknown; kind?: unknown; summary?: unknown; class?: unknown; status?: unknown; unmatched?: unknown; ref?: unknown }
type View = { events?: ViewEvent[]; runs?: Record<string, ViewRun>; cursor?: unknown }

const text = (value: unknown): string => (typeof value === 'string' ? value : '')

// the chip the desk draws for an event (cockpit/index.html chipOf), from the fields it carries
function chipOf(e: ViewEvent): string {
  if (e.class === 'blocking') return 'blocking'
  if (e.status === 'refused') return 'refused'
  if (e.class === 'transient' || e.class === 'advisory') return text(e.class)
  if (e.unmatched === true) return 'pending'
  if (e.status === 'ok' || e.kind === 'approval') return 'ok'
  return ''
}

// The server returns every run still open with each poll, so the open runs are exactly the
// ones this view calls open; the events are appended, and a later outcome clears the intent
// it answers as the server pairs them. The strip counts the open runs the server calls
// `waiting` (the arbiter's ruling on review cycle 2 F3): authoritative over the whole ledger,
// never rebuilt from the pane's own bounded history.
export function merge(prev: Snapshot, view: View): Snapshot {
  const runs: OpenRun[] = Object.entries(view.runs ?? {})
    .filter(([, r]) => r.closed !== true)
    .map(([id, r]) => ({ id, word: text(r.word), quiet: text(r.quiet), actor: text(r.actor), job: text(r.job), lastTs: text(r.last_ts) }))
    .sort((a, b) => (a.lastTs < b.lastTs ? 1 : a.lastTs > b.lastTs ? -1 : 0))
  const held = new Set(prev.events.map(e => e.id))
  const answered = new Set((view.events ?? []).filter(e => e.kind === 'outcome').map(e => text(e.ref)))
  const fresh: EventRow[] = (view.events ?? [])
    .filter(e => !held.has(text(e.id)))
    .map(e => ({ id: text(e.id), ts: text(e.ts), kind: text(e.kind), summary: text(e.summary), chip: chipOf(e), unmatched: e.unmatched === true }))
  const events = [...prev.events, ...fresh]
    .map(e => (answered.has(e.id) && e.unmatched ? { ...e, unmatched: false, chip: e.chip === 'pending' ? '' : e.chip } : e))
    .slice(-KEEP * 8)
  return { runs, events, cursor: text(view.cursor) || prev.cursor, isReached: true, wasReached: true, error: '' }
}

function statusOf(s: Snapshot): string {
  if (!s.isReached) return 'kgme · server not reached'
  const newest = s.runs[0]
  return newest ? `kgme · ${newest.actor} ${newest.word}${newest.quiet ? ` · ${newest.quiet}` : ''}` : 'kgme · idle'
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const poll = async () => {
      const prev = await read($, snapshot)
      const url = prev.cursor ? `${EVENTS}?since=${encodeURIComponent(prev.cursor)}` : EVENTS
      let fresh: Snapshot
      try {
        const res = await $.http.fetch(url)
        fresh = res.ok ? merge(prev, JSON.parse(res.text) as View) : { ...prev, isReached: false, error: `HTTP ${res.status}` }
      } catch (err) {
        fresh = { ...prev, isReached: false, error: 'no response' }
      }
      await update($, snapshot, () => fresh)
      $.ui.status(statusOf(fresh))
    }
    void $.ui.open({ id: PANE, title: 'KGME cockpit' })
    void poll()
    $.clock.every(POLL_MS, () => void poll())
    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const s = await read($, snapshot)
    const waiting = s.runs.filter(r => r.word === 'waiting').length
    const blocked = s.runs.some(r => r.word === 'blocked')
    const head = s.isReached
      ? `● live · ${s.runs.length} open run${s.runs.length === 1 ? '' : 's'}`
      : s.wasReached
        ? `○ server not reached (${s.error}) · last snapshot kept`
        : '○ server not reached · start it with kgme cockpit'
    return (
      <Box flexDirection="column">
        <Text color={s.isReached ? (blocked ? 'magenta' : 'cyan') : 'gray'}>{head}</Text>
        {blocked && <Text color="magenta">▌ halted · a run is blocked</Text>}
        {waiting > 0 && <Text color="yellow">{`▔ ${waiting} run${waiting === 1 ? '' : 's'} waiting on an outcome`}</Text>}
        {s.runs.length === 0 && s.wasReached && <Text dimColor>No open run.</Text>}
        {s.runs.map(r => (
          <Text color={COLOR[r.word] ?? 'white'}>{`${r.word}${r.quiet ? ` · ${r.quiet}` : ''} · ${r.actor}${r.job ? ` · ${r.job}` : ''}`}</Text>
        ))}
        {s.events.length > 0 && <Text dimColor>last events</Text>}
        {s.events.slice(-KEEP).map(x => (
          <Text dimColor={!x.unmatched} color={x.unmatched ? 'yellow' : undefined}>{`${x.ts.slice(11, 19)} ${GLYPH[x.kind] ?? '·'} ${x.summary}${x.chip ? ` [${x.chip}]` : ''}`}</Text>
        ))}
      </Box>
    )
  })
}
