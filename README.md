# My Tasks

A lightweight personal task manager built as a **Progressive Web App (PWA)**. Installable on iOS and Android with no App Store required, fully offline-capable, and stores all data locally in your browser's IndexedDB.

**Live app:** [saadmaghani.github.io/Task-Manager](https://saadmaghani.github.io/Task-Manager)
**Current version:** v8.0.0 — "search & notes"
**Conversation history:** [`CONVERSATION.md`](./CONVERSATION.md) — the full dev story behind this app

---

## Table of Contents

1. [Installation](#installation)
2. [Features](#features)
3. [How Storage Works](#how-storage-works)
4. [Coding Architecture](#coding-architecture)
5. [Beta Build](#beta-build)
6. [File Structure](#file-structure)
6. [Version History](#version-history)
7. [Roadmap](#roadmap)

---

## Installation

### iPhone (iOS)
1. Open the link above in **Safari**
2. Tap the **Share** button (box with arrow icon)
3. Tap **Add to Home Screen**
4. Tap **Add** — the app icon appears on your home screen and launches fullscreen

### Android
1. Open the link above in **Chrome**
2. Tap the **three-dot menu**
3. Tap **Add to Home Screen** or **Install App**

Once installed, the app behaves like a native app — fullscreen, offline-capable, no browser chrome.

---

## Features

### Tasks Tab

The main hub where all tasks live as cards in a two-column grid.

- **Add tasks** — Type in the input bar at the top, hit `+` or Enter
- **Selection-based workflow** — Tap any task card to select it for your daily focus. Selected cards fill with their category color (or accent green) and show white text.
- **Selection threshold (N)** — A confirm button at the bottom unlocks only after selecting at least N tasks (configurable in Settings, default 3). You can select fewer if you want — but a popup asks for confirmation if you try to exceed N: "You've already selected N tasks. Add more?" After saying Yes once, further selections proceed silently.
- **Confirm button** — Sends selected tasks to the Current tab as your "focus list" for the day.
- **Category filter pills** — Scroll along the top to filter tasks by category. "All" shows everything.
- **Search icon** — Tap the ⌕ icon in the header to reveal a search bar. Type to filter tasks live by name *or* category. Matched text is highlighted in yellow.
- **Long-press action sheet** — Hold a task for ~0.5s to open a menu with:
  - ✎ Rename task
  - ⊕ Set/change category
  - 🗑 Delete task (with confirmation)
- **Category color borders** — Tasks with a category show a tinted border in that color. Selected tasks fill solid.
- **Last completed display** — Each card shows "Today", "Yesterday", or "3d ago" in small grey text below the task name.
- **Subtask indicator** — If a task has subtasks, a small `☰ 2/5` counter shows progress.
- **Visibility toggles** (in Settings) — Hide completed tasks, or push them to the bottom.

### Current Tab

Your focused list for today.

- **Background gradient** — As you complete tasks, the entire app background shifts from cream → spring green, smoothly interpolating through 4 stops.
- **Checkboxes** — Each task has a square check. Tap to mark done.
- **Subtasks (bullet list under each task)** — Always visible below the task. Tap `+ Add subtask` to add bullet points. Tap a subtask's checkbox to cross it off. If a task has subtasks, the parent checkbox is **locked** — the task auto-completes only when all subtasks are checked. Unchecking a subtask uncompletes the parent.
- **Progress bar** at the top shows X/Y done.
- **Well done popup** 🌱 — When all current tasks are complete, a celebration screen appears.

### Notes Tab

A standalone notes section separate from tasks. Survives daily resets.

- **Plain or rich text** — Toolbar appears when editing: **B** Bold / *I* Italic / U Underline / • Bullet list / 1. Numbered list
- **Inline editing** — Tap inside any note to edit. Auto-saves 600ms after you stop typing.
- **Archive vs delete:**
  - **Archive** (✓ archive) — Crosses the note out and moves it to a collapsible archive section at the bottom. Text becomes lighter.
  - **Unarchive** (↩ unarchive) — Brings an archived note back to active.
  - **Delete** (✕) — Permanently removes the note (with confirmation).
- **Archive section** — Collapsed by default. Tap to expand and see all archived notes with their counts.
- **Creation date** shown on each note in small mono font.
- **Tab badge** shows count of active (non-archived) notes.

### Settings Tab

#### Insights
- **Task history** — Opens a full-screen view with:
  - 4 stat cards: Total completions, Day streak, Active days, This week
  - **12-week heatmap** (calendar grid like GitHub contributions) — deeper green = more completions that day, today is outlined
  - **By category** — Horizontal bar chart of completion counts per category
  - **Most completed tasks** — Top 5 leaderboard

#### Selection
- **Minimum tasks (N)** — Stepper (1-20) for how many tasks unlock the Confirm button

#### Categories
- **Add category** — Custom name + color picker (10 spring-themed presets)
- **Edit/rename/delete** — Inline name editing, color swatch tap to change color
- Tasks assigned to a deleted category become uncategorized

#### Daily Reset
- **Reset time** — Configurable, default 5:00 AM
- **Next reset** display — Shows when the next automatic reset will fire
- **Reset now** — Manual reset button. On reset: all tasks leave Current, are marked incomplete and unselected. Subtasks are wiped. Notes are NOT affected.

#### Display
- **Show completed tasks** toggle
- **Move done to bottom** toggle

#### Data
- Total tasks count
- Completed today count
- **Clear completed tasks** — Removes all done tasks
- **Clear archived notes** — Permanently deletes the archive
- **Clear all data** — Wipes everything (tasks, notes, history, with confirmation)

---

## How Storage Works

The app uses **IndexedDB** via the **Dexie.js** library — a robust, async, structured local database in your browser. This was a deliberate move away from the more fragile `localStorage` after early versions kept losing data on updates.

### Why IndexedDB (not localStorage)

| Property | localStorage | IndexedDB |
|----------|--------------|-----------|
| Storage limit | ~5MB | Hundreds of MB |
| Data shape | Strings only (JSON blobs) | Structured records |
| Updates | Read entire blob, parse, modify, rewrite | Update individual rows |
| Risk of clearing | Higher (browser sometimes purges) | Lower |
| Multi-user safe | No | Each user's IndexedDB is isolated |

### Database Schema

The database is called `MyTasksDB` and has these tables:

```
┌─────────────────┬───────────────────────────────────────────┐
│ Table           │ Purpose                                   │
├─────────────────┼───────────────────────────────────────────┤
│ tasks           │ Main task records                         │
│ settings        │ App preferences (key-value rows)          │
│ notes           │ Subtask lists (one row per parent task)   │
│ history         │ Permanent record of every task completion │
│ standaloneNotes │ Notes tab content (rich text + archive)   │
│ meta            │ Internal flags                            │
└─────────────────┴───────────────────────────────────────────┘
```

### Sample Records

**tasks**
```js
{
  id: 'abc123',
  text: 'Write the README',
  done: false,
  selected: false,
  current: false,
  categoryId: 'cat_xyz',
  lastCompletedAt: 1716480000000  // ms timestamp
}
```

**history** (every completion is recorded)
```js
{
  id: 42,  // auto-incrementing
  taskId: 'abc123',
  taskText: 'Write the README',
  categoryId: 'cat_xyz',
  completedAt: 1716480000000
}
```

**standaloneNotes**
```js
{
  id: 'note_abc',
  html: '<p>Pick up <strong>milk</strong></p><ul><li>2%</li></ul>',
  createdAt: 1716480000000,
  archived: false,
  archivedAt: null
}
```

### What Persists vs Resets

| Data | Daily reset wipes? | Persists across days? |
|------|--------------------|------------------------|
| Tasks | Only `current` and `done` flags | ✅ |
| Subtasks | ✅ Wiped | ❌ |
| Standalone notes | ❌ Never wiped automatically | ✅ |
| Task history | ❌ Never wiped automatically | ✅ |
| Categories | ❌ Never wiped | ✅ |
| Settings | ❌ Never wiped | ✅ |

### Migration & Schema Upgrades

Dexie handles schema versioning automatically. The app declares schema versions explicitly:

```js
db.version(1).stores({tasks: '...', settings: '...', notes: '...'});
db.version(2).stores({..., history: '++id, ...'});
db.version(3).stores({..., standaloneNotes: 'id, archived, ...'});
```

When a user opens the app for the first time after an update, Dexie automatically upgrades their database to the latest version without losing data.

On first install, a one-time `migrate()` routine also checks for legacy `localStorage` keys from old versions (`mytasks_v4_tasks`, `mytasks_v3_tasks`, etc.) and imports any found data into IndexedDB.

---

## Coding Architecture

The entire app lives in a **single HTML file** with embedded CSS and JavaScript. No build step, no bundler, no frameworks. Just vanilla JS + Dexie.

### High-Level Flow

```
┌──────────────────────────────────────────────┐
│  1. Page loads                               │
│  2. Loading screen shown                     │
│  3. init() runs:                             │
│     - migrate() — pull legacy localStorage   │
│     - loadAll() — read all rows from Dexie   │
│       into in-memory state arrays            │
│     - checkAndRunReset() — daily reset?      │
│     - render() — full UI paint               │
│  4. Loading screen hidden, app shown         │
└──────────────────────────────────────────────┘
```

### State Model

All state is held in module-level variables. Render is synchronous and always reads from these:

```js
let tasks = [];                  // array of task objects
let settings = { ... };          // user preferences
let subtasks = {};               // { taskId: [{id, text, done}] }
let standaloneNotes = [];        // notes tab
let activeFilter = null;         // current category filter
let searchQuery = '';            // active search text
// ... plus UI flags (deleteMode, welldoneShown, etc.)
```

**Pattern:** Action functions modify state → call `saveTask()`/`saveSettings()` → call `render()` to repaint.

### Render Functions

Each tab has its own render function. The master `render()` calls all of them:

```js
function render() {
  renderTasks();
  renderCurrent();
  renderNotes();
  renderSettings();
  updateBadges();
}
```

Each render function builds its HTML as a template literal string and replaces `innerHTML` of the relevant container. This is simple, fast, and avoids the complexity of a virtual DOM or framework.

### Save Layer

Save functions are thin wrappers around Dexie operations:

```js
async function saveTask(task)     { await db.tasks.put(task); }
async function saveTasks(arr)     { await db.tasks.bulkPut(arr); }
async function deleteTaskFromDB(id) { await db.tasks.delete(id); ... }
async function saveSettings()     { await Promise.all([...]); }
async function saveNote(n)        { await db.standaloneNotes.put(n); }
async function recordCompletion(t) { await db.history.add({...}); }
```

This means every modification is **atomic** at the row level. If the user closes the app mid-action, only the changed record is at risk — never the whole dataset.

### UI Patterns

- **Bottom tab bar** — 4 tabs: Tasks, Current, Notes, Settings. Each is a `.screen` div with absolute positioning; switching toggles the `.active` class.
- **Modal overlays** — Popups (rename, confirm delete, well-done, etc.) use full-screen overlays with `position: fixed`.
- **Action sheet** — Bottom-sheet style menus slide up from the bottom (long-press menu, category assignment).
- **Long-press detection** — Custom `attachLongPress()` uses `touchstart` + timeout, cancelled on `touchend` or `touchmove`. ~550ms threshold.
- **Search highlighting** — `highlightMatch()` wraps matched substrings in a span with a yellow background, regex-escaped for safety.
- **Color theme** — All colors are CSS custom properties (`--bg`, `--accent`, etc.) on `:root`. The Current tab dynamically updates `--bg` based on completion progress.

### Daily Reset Mechanism

```
┌──────────────────────────────────────────────────────────┐
│  Every 30 seconds:                                       │
│  - checkAndRunReset() runs                               │
│  - Reads last reset timestamp from settings table        │
│  - Computes today's reset target (e.g. today @ 5:00 AM)  │
│  - If now >= target AND last_reset < target:             │
│    - Clear .current and .done on all tasks               │
│    - Clear all subtasks                                  │
│    - Update last_reset to now                            │
│  - else: no-op                                           │
└──────────────────────────────────────────────────────────┘
```

The check runs every 30 seconds via `setInterval`, plus once on app load. This ensures the reset fires whether the app is open at the reset time or first opened later in the day.

### Service Worker (Offline Support)

A separate `sw.js` file caches the app shell. On first visit, the app downloads `index.html`, `manifest.json`, and itself; afterwards the app loads instantly from cache even without an internet connection.

### PWA Configuration

`manifest.json` declares the app metadata: name, icons, theme color, display mode (`standalone`), and start URL. This is what makes "Add to Home Screen" produce a real app icon instead of a browser bookmark.

---

## Beta Build

A second copy of the app lives at `/beta/` so changes can be tried before they go live.

**URLs**
- Production: `https://saadmaghani.github.io/Task-Manager/`
- Beta: `https://saadmaghani.github.io/Task-Manager/beta/`

### Which file do I edit?

**`beta/index.html`.** That is the working copy. Production (`index.html`) is a frozen snapshot that only moves when you promote.

```
beta/index.html   <- you edit this. Testers see it immediately.
      |
      |  python3 release.py promote v10.0.0
      v
index.html        <- frozen. Untouched until you promote.
```

Never hand-edit `index.html`; promote overwrites it.

### Shared data

**Beta and production share the same data.** Same IndexedDB database (`MyTasksDB`), same Firestore paths (`users/{uid}/...`, `sharedLists/...`), same Google sign-in. A task added in beta appears in production immediately, and vice versa. This is intentional so testers work with real data.

The consequence is that a bug in beta can damage real data:

1. Click through anything you push to `/beta/` before handing it to testers.
2. Be careful with schema changes. If a beta build bumps the Dexie version or changes a record's shape, that migration runs against the shared database and the older production build may not understand the result. Promote schema changes promptly rather than leaving them in beta for long.

### Versioning

Versions are `vMAJOR.NN`. The major number is the release line; `NN` counts the
beta iterations inside it. Promoting gives production the beta version verbatim.

```
production   v9.00
beta         v10.01  ->  v10.02  ->  v10.03
promote      production becomes v10.03
beta         v11.01  ->  v11.02  ...
```

The next line starts on its own: once beta and production are level, the next
`bump` jumps to `v11.01` rather than continuing to `v10.04`.

Each beta build gets a version bump and an entry in
[`CHANGELOG.md`](./CHANGELOG.md). Since the version shows at the bottom of the
Settings tab, a tester can read it straight off their screen when reporting
something.

### Commands

```bash
# Has beta drifted from production? Shows both version numbers.
python3 release.py status

# Advance the beta version: v10.01 -> v10.02
python3 release.py bump
python3 release.py bump v12.01     # or set one explicitly

# Ship beta to everyone. Production takes the beta version verbatim.
python3 release.py promote

# Abandon a beta experiment and start again from production
python3 release.py reset-beta
```

`promote` strips every beta-only artefact, sets the version label, and bumps the
production service-worker cache so clients pick up fresh files. If the
`BETA:START` / `BETA:END` markers have been edited by hand it refuses to run
rather than leaking beta markup into production.

`status` ignores the version label when comparing, so it reports a difference
only when actual code differs.

### Recovering an older beta

Only the latest beta exists in the working tree — bumping to `v10.02` overwrites
`v10.01`. Git history is what makes older builds recoverable, so commit each
bump separately:

```bash
git log --oneline -- beta/index.html    # find the build you want
git checkout <sha> -- beta/index.html   # restore it
python3 release.py promote              # ship that one instead
```

### What differs in beta

- An amber `BETA` badge next to every screen title and on the splash logo, plus a thin amber strip across the top
- Its own PWA manifest, so it installs as a separate home-screen icon (`Tasks Beta`)
- Its own service worker cache, so the builds never serve each other stale files
- Settings shows the beta version, e.g. `my tasks / v10.02`

All of it sits between `BETA:START` and `BETA:END` markers and is removed on promote. Don't delete those markers.

### Typical cycle

```bash
# 1. edit beta/index.html
# 2. bump the beta version and note the change in CHANGELOG.md
python3 release.py bump

# 3. push - testers get it in about a minute
git add . && git commit -m "beta v10.02: new deadline picker" && git push

# 4. once it's proven, release it
python3 release.py promote
git add . && git commit -m "release v10.02" && git push
```

Both service workers are network-first, so a reload always fetches the newest build rather than serving from cache.

---

## File Structure

```
taskapp/
├── index.html            — production snapshot (generated by promote)
├── manifest.json         — PWA metadata
├── sw.js                 — service worker (network-first)
├── release.py            — status / bump / promote / reset-beta
├── CHANGELOG.md          — what changed in each version
├── beta/
│   ├── index.html        — THE working copy; edit this one
│   ├── manifest.beta.json
│   └── sw.js             — separate cache name
├── FIREBASE_SETUP.md     — one-time Firebase setup guide
└── README.md             — this file
```

`beta/index.html` is the file you edit. `index.html` is generated by `release.py promote`; hand edits to it are overwritten.

Everything else (Dexie, fonts) is loaded from CDN.

---

## Version History

| Version | Theme | Key additions |
|---------|-------|---------------|
| v1.0.0 | Tasks  | Basic task list, Current/Settings tabs, localStorage |
| v2.0.0 | Selection flow | N-task selection, Confirm button, daily reset |
| v3.0.0 | Categories | Categories with colors, filters, action sheet, completion timestamps |
| v4.0.0 | Spring theme | Light theme, category-filled cards, long-press action sheet |
| v5.0.0 | Dexie | localStorage → IndexedDB migration |
| v6.0.0 | Polish | Spring color palette, refined UI |
| v7.0.0 | History & Subtasks | Task history view, subtasks that drive completion, heatmap |
| v8.0.0 | Search & Notes | Search bar, standalone Notes tab with rich text, archive section |

---

## Roadmap

Possible additions for future versions:

- **Drag to reorder** tasks manually
- **Streaks** — fire emoji + counter for consecutive days
- **Recurring tasks** — daily/weekly tasks that auto-appear
- **Task templates** — save groups of tasks (e.g. "morning routine")
- **Sound effects** — soft chime on task completion
- **Custom accent color** — let users override the spring green
- **Backup & restore** — export/import all data as JSON
- **Custom domain** — point a real domain at GitHub Pages
- **Optional Firebase sync** for cross-device support

---

## Tech Stack

- Vanilla HTML / CSS / JavaScript — no frameworks
- **Dexie.js** (3.2.4) — IndexedDB wrapper, loaded from CDN
- PWA manifest + Service Worker for offline support
- Google Fonts: **DM Sans** and **DM Mono**
- Hosted on **GitHub Pages**

---

## Privacy

All data lives in your browser's IndexedDB. Nothing is sent to any server. No account, no tracking, no analytics. If you uninstall the PWA or clear your browser data, the data is gone — but as long as you don't, it persists indefinitely.

---

## License

Personal use.
