# Changelog

Versions are `vMAJOR.NN`. The major number is the release line; `NN` counts the
beta iterations inside it. Production takes the beta version verbatim on
promote, so `v10.03` in beta releases as `v10.03`. The next beta line then
starts at `v11.01`.

The version label is shown at the bottom of the Settings tab, so a tester can
always tell you exactly which build they're on.

---

## Unreleased (beta)

## v10.01

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

<!--
Template for the next beta change:

## v10.01
### Added
-
### Changed
-
### Fixed
-
-->

---

## v9.00 — current production

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
