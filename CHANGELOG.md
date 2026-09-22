# Changelog

Versions are `vMAJOR.NN`. The major number is the release line; `NN` counts the
beta iterations inside it. Production takes the beta version verbatim on
promote, so `v10.03` in beta releases as `v10.03`. The next beta line then
starts at `v11.01`.

The version label is shown at the bottom of the Settings tab, so a tester can
always tell you exactly which build they're on.

---

## Unreleased (beta)

## v11.01

### Added
- **Weekly schedule, live at the top of Current.** Today's blocks sit above your
  picked tasks under "Today's schedule", with a done count. The block happening
  now is highlighted with a **Now** marker; the next timed block shows
  **Next · in 25 min**. Timed blocks that have passed unticked are dimmed rather
  than flagged.
- **Schedule items are tasks.** Each block points at a real task in the pool —
  one task per distinct name, so "Hifdh revision" on six days is one task.
  Ticking a block completes that task through the normal path: it's logged to
  history, shows as done in the Tasks tab, and resets at the daily reset time. If
  a linked task is deleted from the pool, it's recreated when the block is next
  ticked.
- **Week view** behind the ▦ button in the Current header, alongside ✎ for notes.
  Lists every day Monday to Sunday with today marked; add a block to any day or
  remove one. New timed blocks slot in by start time.
- **One-tap import** of the weekly study timetable, offered only when the
  schedule is empty. It's opt-in rather than seeded so other testers don't
  inherit someone else's timetable.
- Schedule syncs across devices when signed in.

### Behaviour worth knowing
- **Prayer-window blocks aren't live.** "Dhuhr–Asr", "After Isha" and the like
  have no clock time, so they're shown as written with no Now/Next marker. Only
  blocks with a clock time are tracked.
- **The schedule's day runs reset-to-reset**, like the rest of the app. At 1am
  you're still in yesterday's schedule, with its blocks shown as past; the next
  day starts at the reset time, not midnight.
- A block with only a start time (e.g. "11:00 AM") counts as live for 30
  minutes.
- There's no now-line between blocks: with prayer windows interleaved there's no
  honest place to draw one.

### Storage
Stored under a `schedule` key in the existing settings store and a
`meta/schedule` document in Firestore — **no new Dexie table**. Beta and
production share one IndexedDB per domain, and a Dexie version bump in beta would
stop the production build from opening the database at all. The v10.06
production build ignores the new key entirely.

### Not yet
Editing an existing block means removing and re-adding it. Reordering blocks
within a day isn't supported yet.

> The beta splash screen shows short summaries of whatever sits in this
> section. Keep them brief — the detail lives in the entries themselves.

<!--
Template for the next beta change:

## v11.01
### Added
-
### Changed
-
### Fixed
-
-->

---

## v10.06 — current production

Released from beta builds v10.01 – v10.06, detailed below.

### v10.06

### Added
- **Bold, italic and underline in notes.** Select text and use the platform's
  own selection menu — there's no toolbar. Earlier builds actively blocked these
  commands and stripped the tags; that block is gone. Anything the OS produces
  is reduced to `<b>`, `<i>` and `<u>`, with attributes removed, so nothing else
  can ride in with it.
- **Three indent levels**, with the bullet changing shape as lines nest:
  • then ◦ then ▪. Tab and Shift+Tab on a keyboard; on touch, swipe a line right
  to indent and left to outdent. Vertical movement is ignored so scrolling still
  works, and swipes starting on the bullet are left to the cross-off tap.
- A new line keeps the indent you were writing at, but never inherits
  formatting or the crossed-off state.

### Security
- Stored markup is sanitised when loaded, not only when typed, so anything that
  reached the record from another device or an older build can't inject markup
  when the page renders.

### Note
`html` and `indent` are new per-line fields. They're additive, so the v9.01
production build still loads notes without error — but it doesn't know about
them, and saving a note there will drop formatting and indentation. Worth
promoting before doing much note editing in the live app.

### v10.05

### Fixed
- **Day dividers still never appeared.** v10.04 fixed the Enter path, but that
  isn't how a new day actually starts. The page always ends with a blank line,
  which is saved carrying that day's date; open the notepad tomorrow and the
  caret lands on exactly that line, so you simply type — no Enter involved. The
  text inherited yesterday's date and no new group could form.

  A line is now dated the moment it stops being blank, rather than when the
  blank row was created, so writing on a new day starts a new group whichever
  way you get there.
- Blank lines no longer open a day group, so the leftover trailing blank can't
  strand a stale dated rule beneath the notes you just wrote.

### v10.04

### Fixed
- **Day dividers never appeared.** When Enter splits a line, browsers clone the
  `<li>` — including its date and crossed-off state. Every new line therefore
  inherited the previous line's date, so a new day could never start a new
  group, and a line typed after a crossed-off one came out struck through. New
  lines are now built explicitly: a line added at the end of the page is dated
  today, one inserted inside an earlier day keeps that day, and no line is ever
  born crossed off.
- Multi-line pastes now become properly dated lines instead of one merged blob.
- Added a reconcile pass so a line the browser manufactures another way
  (autocorrect, undo, drag) still gets a valid date and consistent state.

### Added
- **Beta "what's new" splash**, shown on every load, summarising everything
  since the last stable release and asking testers to comment on each change
  individually. Beta-only — it strips out on promote. It reads its version from
  the app itself, so bumping keeps it in step, and it waits for the first-run
  onboarding screen rather than stacking on top of it.

### Note on existing notes
Lines that predate v10.03 all carry a single timestamp, because the date a line
was written wasn't recorded before then. They'll sit under one divider forever;
anything written from now on groups correctly by day.

### v10.03

### Added
- **Notes can be crossed off.** Tap the bullet at the left of a line to strike it
  through; tap again to restore it. Tapping the text still places the cursor as
  before, so editing is unaffected — the bullet gutter is the only tap target.
  Crossed-off lines stay where they are rather than moving.
- **Dated day dividers.** A rule with the day right-aligned beneath it — e.g.
  `Wed 26 Aug, 26` — marks the start of each day's notes, including the first.

### Changed
- A notepad line is now a record with its own date and crossed-off state rather
  than plain text. Existing notes are migrated automatically and keep their
  order; they're dated from when the notepad was last saved.
- Lines are never re-sorted, so a note inserted mid-page stays put. One that's
  typed inside an earlier day's block takes that day rather than splitting the
  group in two; a line added at the end is dated today.
- Day grouping is recalculated when you leave the notepad, not while typing, so
  the cursor never jumps mid-sentence.

### v10.02

### Changed
- **Notes moved into the Current tab.** The notepad is now behind a ✎ button in
  the Current header rather than being its own tab — notes are things you jot
  while working through the day, so they belong next to the day's tasks. The
  button toggles between the two views and turns into ◎ to come back. The header
  title switches to "Notes", and the subtitle shows the line count.
- Leaving and returning to the Current tab always lands on the task list.
- The completion-gradient background is suspended while the notepad is open, so
  the paper reads as paper.
- **The "More" menu is gone.** With Notes moved out it held only Settings, so the
  fourth tab is now Settings directly. The tab bar is Tasks / Current / Shared /
  Settings.

### v10.01

### Added
- **Suggested repetition.** Long-press a task in the Tasks tab and choose
  "Suggest repetition" to set an interval — every 2 weeks, every 3 months, and
  so on. Presets cover 1w / 2w / 1mo / 3mo / 6mo / 1y, or type any number of
  days, weeks or months.
- Tasks with an interval show it on the card next to the "Xd ago" text, e.g.
  `↻ 3mo`. It shows whether or not the task has ever been completed.
- A **Suggested** chip appears in the category filter bar, immediately after
  "All", with a count. A task enters it once the interval has elapsed *since its
  last completion*, and stays until it is completed again. The chip hides itself
  when nothing is due, and the interval on a due task turns terracotta.
- Tasks that have never been completed are never suggested — the clock only
  starts on the first completion.

---

## v9.01 (hotfix)

### Fixed
- **The live app failed to load: "t.trim is not a function".** Beta v10.03
  changed a notepad line from a plain string to a `{text, done, ts}` record, and
  because beta and production share one database, the production build — which
  still expected strings — crashed on startup for everyone.

  Production now accepts both shapes, and preserves the date and crossed-off
  flag on every save even though this build doesn't display them, so editing
  notes in the live app no longer discards what beta recorded.

  This was hand-edited into `index.html` rather than promoted, to avoid shipping
  the untested v10.x features alongside the fix. The next promote supersedes it.

### Lesson
A schema change in beta reaches production immediately, because the data is
shared. Any future change to a stored record's shape needs the *reading* side
shipped to production first, or promoted at the same time.

---

## v9.00

### Added
- Google sign-in, optional. The app still works fully signed-out and local-only.
- Cloud sync for tasks, subtasks, categories, notes and history via Firestore.
- Shared tab: create shared lists, invite members by email, collaborate in real time.
- Shared tasks have subtasks and deadlines, and record who completed what and when.
- First-visit splash screen with a "continue without an account" option.
- Notes rebuilt as a single ruled notepad page — plain text, one bullet per line.
- Task deadlines, set by long-pressing a task in the Current tab.
- Stale-task filter with a configurable threshold in Settings.
- Beta channel at `/beta/` plus `release.py` for promoting builds.

### Changed
- Search moved next to the add button; the add field doubles as the search box.
- Notes and Settings moved behind a "More" button in the tab bar.
- Notes are checked off with a checkbox rather than an archive button.
- Deadlines can only be set from the Current tab, not the Tasks list.
- Service workers switched to network-first so a deploy shows up on reload.

### Fixed
- Completed tasks with a deadline no longer reappeared in Current forever. The
  daily reset now keeps a task only while it has a deadline **and** is unfinished.
- `manifest.json` and `sw.js` used absolute `/` paths, which resolve to the
  domain root rather than `/Task-Manager/` on a GitHub project page — offline
  caching silently failed and the home-screen start URL was wrong. Both now use
  relative paths.
- Manifest still carried the old dark theme colours after the light redesign.

---

## v8.00

### Added
- Search across task names and category names, with match highlighting.
- Standalone Notes tab with rich text and a collapsible archive.

---

## v7.00

### Added
- Task history: 12-week heatmap, streak, category breakdown, most-completed list.
- Subtasks that drive completion — a parent task finishes only when all its
  subtasks are checked.

---

## v6.00

### Changed
- Spring light theme replacing the dark theme.
- Selected task cards fill with their category colour.
- Long-press opens an action sheet (rename / categorise / delete).

---

## v5.00

### Changed
- Storage moved from `localStorage` to IndexedDB via Dexie, after repeated data
  loss on version updates. Rows are now written individually rather than as one
  serialised blob.

---

## v4.00 and earlier

Early iterations: task list, the N-task selection flow and Current tab, daily
reset, categories, per-task completion timestamps, and the move from a native
app idea to a PWA.
