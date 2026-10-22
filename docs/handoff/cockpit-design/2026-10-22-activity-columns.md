---
id: CDH-0025
type: handoff
created: 2026-10-22T02:10:00-07:00
from: cowork
to: codex
model: gpt-6-astra
tier: 2
status: proposed
depends_on: [CDH-0019]
design_track: HANDOFF-0036
---

# CDH-0025: Activity as columns (CW29, F7)

## Outcome and authority

CW29 was decided at 2 × 0.4 = 0.8 (AUDIT-CDH-0019-CYCLE-2-REVIEW). The F4 repair made the activity grids correct but turned them into tables of digits, so the picture (where activity clusters and where it turned blocking) is gone. This row draws them as columns whose height is the count. It's built with F7's bucket contract (AUDIT-CDH-0022, 0.4), defined here: the desk shows 60 one-minute buckets, the wall 240 one-minute buckets.

It's independent of CDH-0023 and may be built right after it. Adopted when the builder prompt takes this row as the first `ready` one.

## Do

1. **The columns.** In the activity panels of 3 Live, 4 Blocking, 5 Pending, 6 Disconnected and 9 Wall, each bucket becomes a column.
   - **Height:** proportional to its count on a fixed 0–5 scale; 5 or more is full height with a `+` cap mark.
   - **B and P:** blocking and pending buckets carry a glyph mark on their column, not colour alone.
   - **Colour:** the cyan ramp may still tint a column but carries nothing by itself.
   - **Exact values:** each column's accessible label carries its count and its time.
   - **Summary:** one line under the panel gives peak, total and where any blocking falls (for example "peak 5/min at 19:51 · 64 events · blocking 19:45").
   - Remove the digits and the "Values are events, in sample order" caption.
2. **The samples.**
   - The desk takes the last 60 values of each existing 96-value array.
   - The wall keeps its 240.
   - The B and P sentinels stay on their buckets.
   - Label the time axis: 60 minutes on the desk, 4 hours on the wall.
3. **Board 1's "run grid" specimen** becomes the column specimen with its legend.
4. Keep the panel sizes. The run-grid panel's height may change by the summary line only.

## Verify

- A source check: values in order, B and P on the right buckets, and every column labelled.
- The CSS fixture at 1440, and 2560 for the wall: column heights against values, the summary text, contrast of the marks and the summary.
- `make check` green.

Report, close out and commit as for CDH-0023, then stop for Cowork's native pass.

## Acceptance

- The activity reads as a picture again, with no colour-only value.
- Every exact value is reachable.
- The bucket contract is labelled.
