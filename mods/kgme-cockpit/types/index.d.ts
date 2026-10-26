// HANDOFF-0059 §2: what the kgme-cockpit pane keeps between polls, as /api/events returned it.
export type OpenRun = {
  id: string
  word: string
  quiet: string
  actor: string
  job: string
  lastTs: string
}
export type EventRow = {
  id: string
  ts: string
  kind: string
  summary: string
  chip: string
  unmatched: boolean
}
export type Snapshot = {
  runs: OpenRun[]
  events: EventRow[]
  cursor: string
  isReached: boolean
  wasReached: boolean
  error: string
}

declare module 'claude-code' {
  interface PluginState {
    'kgme-cockpit': { snapshot: Shaped<Snapshot> }
  }
}
