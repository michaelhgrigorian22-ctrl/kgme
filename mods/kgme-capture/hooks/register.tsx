import type { Register } from 'claude-code'

// HANDOFF-0059 §3: `/capture <kind> <words>` runs `kgme capture <kind> <words>` and returns
// what it printed, verbatim, so Michou's words reach the vault without leaving the
// prompt (HANDOFF-0050, capture on his word). This is the mod's one `$.process` call, named by
// its handoff: KGME's own command with his words and nothing else. `kgme` is a shell function
// (`uv run --frozen --project "$KGME_HOME" kgme`), and a process runs without a shell, so the
// call spells the function out. Its project is the checkout `kgme session` launched from,
// which the launcher names as `UV_PROJECT` for every level that loads a mod (review cycle 1
// F2): where the terminal stands does not move it.
const USAGE = 'usage: /capture <kind> <words>, the words as you want them kept'

// The words are taken as typed; one pair of quotes around all of them is a shell habit, not
// part of them, and is dropped.
export function parse(args: string): { kind: string; words: string } | null {
  const m = /^\s*(\S+)\s+([\s\S]*\S)\s*$/.exec(args)
  if (!m) return null
  const quoted = /^"([\s\S]*)"$/.exec(m[2]) ?? /^'([\s\S]*)'$/.exec(m[2])
  return { kind: m[1], words: quoted ? quoted[1] : m[2] }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'capture', description: 'Capture a reminder, task, friction or note into the KGME vault, verbatim' })
    return next(e)
  })

  on('command.run', { command: 'capture' }, async ($, e) => {
    const asked = parse(e.args)
    if (!asked) return { text: USAGE }
    try {
      const ran = await $.process.run(['uv', 'run', '--frozen', 'kgme', 'capture', asked.kind, asked.words])
      const printed = `${ran.stdout}${ran.stderr}`.replace(/\s+$/, '')
      return { text: printed || `kgme capture exited ${ran.exitCode} and printed nothing` }
    } catch (err) {
      return { text: `kgme capture did not run: ${err instanceof Error ? err.message : String(err)}` }
    }
  })
}
