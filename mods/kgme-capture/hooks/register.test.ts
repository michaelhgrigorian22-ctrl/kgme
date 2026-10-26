import { expect, test } from 'claude-code/testing'

// HANDOFF-0059 acceptance, /capture's half: the one process call runs KGME's own command with
// the words as typed, from the session's folder, and its output comes back verbatim.
test('/capture runs kgme capture with the words verbatim and returns what it printed', async ($, on) => {
  const runs: { argv: readonly string[]; cwd?: string }[] = []  // the session starts outside the checkout: review cycle 1 F2
  on('command.register', () => ({ value: { command: 'capture' } }))
  on('process.run', (_, e) => {
    runs.push({ argv: e.argv, cwd: e.init?.cwd })
    return { value: { exitCode: 0, stdout: 'captured friction: the pane is too wide\n', stderr: '' } }
  })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/somewhere/else', surface: 'terminal', isInteractive: true })
  const ran = await $.command.run({ command: 'capture', args: 'friction "the pane is too wide"' })
  expect(ran.text).toBe('captured friction: the pane is too wide')
  // no folder of the session's: uv takes its project from UV_PROJECT, which kgme session sets
  expect(runs).toEqual([{ argv: ['uv', 'run', '--frozen', 'kgme', 'capture', 'friction', 'the pane is too wide'], cwd: undefined }])
})

test('/capture with no words runs nothing and says how', async ($, on) => {
  let ran = 0
  on('command.register', () => ({ value: { command: 'capture' } }))
  on('process.run', () => { ran++; return { value: { exitCode: 0, stdout: '', stderr: '' } } })
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/repo', surface: 'terminal', isInteractive: true })
  expect((await $.command.run({ command: 'capture', args: 'friction' })).text).toBe('usage: /capture <kind> <words>, the words as you want them kept')
  expect(ran).toBe(0)
})
