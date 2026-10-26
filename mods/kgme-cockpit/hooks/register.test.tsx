import { expect, mock, test } from 'claude-code/testing'

// HANDOFF-0059 acceptance, the pane's half: it draws what /api/events returns, says so when
// the server cannot be reached, and keeps the last snapshot.
const PANE = {
  plugin: 'kgme-cockpit',
  component: 'Pane',
  requestId: 'kgme-cockpit',
  props: { title: 'KGME cockpit', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 20 }, view: {} },
} as const

const VIEW = {
  events: [
    { id: '01A', ts: '2026-10-26T01:00:00.000-07:00', kind: 'intent', summary: 'Bash make check', class: null, status: null, unmatched: true, ref: null },
  ],
  runs: { R1: { word: 'waiting', quiet: '', closed: false, actor: 'claude-code.hook', job: 'tool:Bash', first_ts: '', last_ts: '2026-10-26T01:00:00.000-07:00' } },
  cursor: '01A',
}
const ANSWERED = {
  events: [
    { id: '01B', ts: '2026-10-26T01:00:01.000-07:00', kind: 'outcome', summary: 'Bash ok', class: null, status: 'ok', unmatched: false, ref: '01A' },
  ],
  runs: { R1: { word: 'working', quiet: '', closed: false, actor: 'claude-code.hook', job: 'tool:Bash', first_ts: '', last_ts: '2026-10-26T01:00:01.000-07:00' } },
  cursor: '01B',
}

test('the pane draws the server’s run states, turning waiting and back, on every surface', async ($, on) => {
  const clock = mock.clock(on)
  const asked: string[] = []
  let answer: unknown = VIEW
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', () => ({ value: undefined }))
  on('http.fetch', (_, e) => { asked.push(e.url); return { value: { status: 200, ok: true, headers: {}, text: JSON.stringify(answer) } } })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await clock.settle()
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...PANE, surface })
    expect((await ui.find({ type: 'Text', text: /claude-code\.hook/ }))?.text).toBe('waiting · claude-code.hook · tool:Bash')
    expect((await ui.find({ type: 'Text', text: /waiting on/ }))?.text).toBe('▔ 1 run waiting on an outcome')
    await ui.unmount()
  }
  answer = ANSWERED
  await clock.advance(2000)
  expect(asked).toEqual(['http://127.0.0.1:8642/api/events', 'http://127.0.0.1:8642/api/events?since=01A'])
  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  expect((await ui.find({ type: 'Text', text: /claude-code\.hook/ }))?.text).toBe('working · claude-code.hook · tool:Bash')
  expect(await ui.find({ type: 'Text', text: /waiting on/ })).toBeUndefined()
  await ui.unmount()
})

test('with the server stopped the pane says so and keeps the last snapshot', async ($, on) => {
  const clock = mock.clock(on)
  let up = true
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', () => ({ value: undefined }))
  on('http.fetch', () => {
    if (!up) throw new Error('connection refused')
    return { value: { status: 200, ok: true, headers: {}, text: JSON.stringify(VIEW) } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await clock.settle()
  up = false
  await clock.advance(2000)
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /server not reached/ }))?.text).toBe('○ server not reached (no response) · last snapshot kept')
  expect((await ui.find({ type: 'Text', text: /claude-code\.hook/ }))?.text).toBe('waiting · claude-code.hook · tool:Bash')
  await ui.unmount()
})

test('a blocked run floods the pane', async ($, on) => {
  const clock = mock.clock(on)
  const blocked = { ...VIEW, runs: { R1: { ...VIEW.runs.R1, word: 'blocked' } } }
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', () => ({ value: undefined }))
  on('http.fetch', () => ({ value: { status: 200, ok: true, headers: {}, text: JSON.stringify(blocked) } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await clock.settle()
  const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /halted/ }))?.text).toBe('▌ halted · a run is blocked')
  await ui.unmount()
})

test('the strip is the server’s waiting runs, with no unmatched row in the page (the arbiter’s ruling on review cycle 2 F3)', async ($, on) => {
  const clock = mock.clock(on)
  const run = (word: string) => ({ R9: { word, quiet: '', closed: false, actor: 'claude-code.hook', job: 'tool:Bash', first_ts: '', last_ts: '2026-10-26T01:00:00.000-07:00' } })
  let answer: unknown = { events: [], runs: run('waiting'), cursor: null }
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('ui.status', () => ({ value: undefined }))
  on('http.fetch', () => ({ value: { status: 200, ok: true, headers: {}, text: JSON.stringify(answer) } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await clock.settle()
  let ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /waiting on/ }))?.text).toBe('▔ 1 run waiting on an outcome')
  await ui.unmount()
  answer = { events: [], runs: run('working'), cursor: null }
  await clock.advance(2000)
  ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /waiting on/ })).toBeUndefined()
  await ui.unmount()
})
