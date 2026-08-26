#!/usr/bin/env python3
"""
release.py — manage the beta and production builds.

Direction of flow:

    beta/index.html   ← you edit this. Testers hit it immediately.
          |
          |  python3 release.py promote
          v
    index.html        ← frozen snapshot. Only moves when you say so.

Commands
--------
  python3 release.py status
      Show whether beta has changes that haven't been promoted yet.

  python3 release.py promote [version]
      Copy beta -> production, stripping all BETA-only markup. Production
      takes the beta version verbatim unless you pass one.
      Bumps the production service-worker cache so clients get fresh files.
      e.g.  python3 release.py promote v10.03

  python3 release.py bump [version]
      Advance the beta version, e.g. v10.01 -> v10.02.
      Pass a version to set one explicitly.

  python3 release.py reset-beta
      Throw away beta work and re-create beta from production.
      Use when a beta experiment didn't pan out.

Versioning
----------
  vMAJOR.NN   major = release line, NN = beta iteration within it

  production  v9.00
  beta        v10.01 -> v10.02 -> v10.03      bump with each beta change
  promote     production becomes v10.03       beta version, verbatim
  beta        v11.01 ...                      next line starts automatically

Everything between BETA:START and BETA:END markers exists only in beta and is
removed on promote. Don't delete those markers by hand.
"""

import io
import os
import re
import sys
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROD_HTML = os.path.join(HERE, 'index.html')
BETA_DIR = os.path.join(HERE, 'beta')
BETA_HTML = os.path.join(BETA_DIR, 'index.html')
PROD_SW = os.path.join(HERE, 'sw.js')

HTML_BLOCK = re.compile(r'[ \t]*<!-- BETA:START -->.*?<!-- BETA:END -->\n?', re.S)
CSS_JS_BLOCK = re.compile(r'[ \t]*/\* BETA:START \*/.*?/\* BETA:END \*/\n?', re.S)
VERSION_LINE = re.compile(r'<div class="app-version">([^<]*)</div>')


def read(path):
    return io.open(path, encoding='utf-8').read()


def write(path, text):
    io.open(path, 'w', encoding='utf-8').write(text)


# ── BETA-only fragments ──────────────────────────────────────────────────────

BETA_CSS = """/* BETA:START */
    .beta-badge{
      display:inline-flex;align-items:center;
      margin-left:8px;padding:2px 7px;border-radius:5px;
      background:#e8c468;color:#4a3c14;
      font-family:'DM Mono',monospace;font-size:9px;font-weight:600;
      letter-spacing:1.2px;vertical-align:middle;position:relative;top:-2px;
    }
    .beta-strip{
      position:fixed;left:0;right:0;top:0;height:3px;
      background:#e8c468;z-index:400;pointer-events:none;
    }
    /* BETA:END */
  </style>"""

BETA_STRIP = """<!-- BETA:START -->
<div class="beta-strip"></div>
<!-- BETA:END -->
<div id="loading">"""

BETA_JS = """
/* BETA:START */
// ═══════════════════════════════════════════
// BETA BUILD MARKER
// Beta shares its database and Firestore paths with production, so changes
// made here appear in the live app too. Removed automatically on promote.
// ═══════════════════════════════════════════
const IS_BETA = true;
function markBetaUI(){
  document.querySelectorAll('.header-left h1').forEach(h=>{
    if(h.querySelector('.beta-badge')) return;
    const b=document.createElement('span');
    b.className='beta-badge'; b.textContent='BETA';
    h.appendChild(b);
  });
  const logo=document.querySelector('.splash-logo-text');
  if(logo && !logo.querySelector('.beta-badge')){
    const b=document.createElement('span');
    b.className='beta-badge'; b.textContent='BETA';
    logo.appendChild(b);
  }
}
document.addEventListener('DOMContentLoaded', markBetaUI);
markBetaUI();
/* BETA:END */
async function init("""

BETA_MANIFEST = """{
  "name": "My Tasks (Beta)",
  "short_name": "Tasks Beta",
  "description": "Beta build \\u2014 shares data with the live app",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#fdf8f0",
  "theme_color": "#e8c468",
  "orientation": "portrait",
  "icons": [
    { "src": "../icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "../icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
"""

BETA_SW = """// Beta service worker — separate cache from production
const CACHE = 'mytasks-beta-v1';
const ASSETS = ['./', './index.html', './manifest.beta.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  // network-first: testers always get the newest beta on reload
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
"""


# ── transforms ───────────────────────────────────────────────────────────────

def to_production(src, version=None):
    """Strip every beta-only artefact from a beta source file."""
    src = HTML_BLOCK.sub('', src)
    src = CSS_JS_BLOCK.sub('', src)
    src = src.replace('<title>My Tasks (Beta)</title>', '<title>My Tasks</title>')
    src = src.replace(
        '<meta name="apple-mobile-web-app-title" content="Tasks Beta"/>',
        '<meta name="apple-mobile-web-app-title" content="My Tasks"/>')
    src = src.replace('href="manifest.beta.json"', 'href="manifest.json"')
    if version:
        src = VERSION_LINE.sub(
            '<div class="app-version">my tasks / %s</div>' % version, src)
    return src


def to_beta(src):
    """Inject the beta-only artefacts into a production source file."""
    src = src.replace('<title>My Tasks</title>', '<title>My Tasks (Beta)</title>')
    src = src.replace(
        '<meta name="apple-mobile-web-app-title" content="My Tasks"/>',
        '<meta name="apple-mobile-web-app-title" content="Tasks Beta"/>')
    src = src.replace('href="manifest.json"', 'href="manifest.beta.json"')
    src = src.replace('  </style>', BETA_CSS, 1)
    src = src.replace('<div id="loading">', BETA_STRIP, 1)
    # version is left untouched: a reset beta is identical to production,
    # so it carries production's version until the next bump.
    src = src.replace('\nasync function init(', BETA_JS, 1)
    return src


def current_version():
    m = VERSION_LINE.search(read(PROD_HTML))
    if not m:
        return None
    label = m.group(1).strip()
    return label.split('/', 1)[1].strip() if '/' in label else label


def beta_version():
    """Version label currently written in beta/index.html."""
    if not os.path.exists(BETA_HTML):
        return None
    m = VERSION_LINE.search(read(BETA_HTML))
    if not m:
        return None
    label = m.group(1).strip()
    return label.split('/', 1)[1].strip() if '/' in label else label


# Versions are vMAJOR.NN — the major is the release line, NN counts the beta
# iterations inside it. Promote ships the beta version verbatim.
#   production v9.00  ->  beta v10.01, v10.02, v10.03  ->  promote v10.03
#                     ->  beta v11.01 ...
VER_RE = re.compile(r'^v(\d+)\.(\d+)$')


def parse_ver(label):
    m = VER_RE.match((label or '').strip())
    return (int(m.group(1)), int(m.group(2))) if m else None


def fmt_ver(major, minor):
    return 'v%d.%02d' % (major, minor)


def next_beta_of(prod_ver):
    """Start a fresh beta line above production: v9.00 -> v10.01"""
    p = parse_ver(prod_ver)
    return fmt_ver((p[0] + 1) if p else 10, 1)


def bump_beta(explicit=None):
    """Advance the beta version.

    Within an open beta line the minor increments (v10.01 -> v10.02). If beta is
    level with production — i.e. the last build was just promoted — a new line
    starts instead (v10.03 promoted, next bump gives v11.01).
    """
    cur = beta_version()
    prod = current_version()
    if explicit:
        new = explicit
    else:
        c, p = parse_ver(cur), parse_ver(prod)
        if c and p and c[0] > p[0]:
            if c[1] >= 99:
                print('WARNING: %s is at the end of its line; '
                      'starting a new one.' % cur)
                new = next_beta_of(prod)
            else:
                new = fmt_ver(c[0], c[1] + 1)
        else:
            new = next_beta_of(prod)
    src = read(BETA_HTML)
    src = VERSION_LINE.sub(
        '<div class="app-version">my tasks / %s</div>' % new, src)
    write(BETA_HTML, src)
    return cur, new


def bump_sw_cache():
    """Increment mytasks-prod-vN so clients drop the old cache."""
    sw = read(PROD_SW)
    m = re.search(r"const CACHE = 'mytasks-prod-v(\d+)';", sw)
    if not m:
        return None
    n = int(m.group(1)) + 1
    sw = sw.replace(m.group(0), "const CACHE = 'mytasks-prod-v%d';" % n)
    write(PROD_SW, sw)
    return n


def fingerprint(text):
    """Hash of a file's actual code, ignoring whitespace and the version label.

    The version label always differs between the two builds ("BETA build" vs a
    version number), so it must be excluded or status would report a difference
    even when the code is identical.
    """
    text = VERSION_LINE.sub('<div class="app-version">#</div>', text)
    return hashlib.sha256(
        re.sub(r'\s+', ' ', text).strip().encode('utf-8')).hexdigest()[:12]


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_status():
    if not os.path.exists(BETA_HTML):
        print('No beta build found. Run:  python3 release.py reset-beta')
        return 1
    beta_as_prod = to_production(read(BETA_HTML))
    same = fingerprint(beta_as_prod) == fingerprint(read(PROD_HTML))
    print('production : %-22s (%s)' % (current_version() or 'unversioned',
                                        fingerprint(read(PROD_HTML))))
    print('beta       : %-22s (%s)' % (beta_version() or 'unversioned',
                                       fingerprint(beta_as_prod)))
    print()
    if same:
        print('Beta matches production. Nothing to promote.')
    else:
        print('Beta has changes that are NOT in production yet.')
        print('Promoting would release as: %s' % (
            beta_version() or 'unversioned'))
        print('Run:  python3 release.py promote')
    return 0


def cmd_promote(version=None):
    if not os.path.exists(BETA_HTML):
        print('ERROR: beta/index.html does not exist.')
        return 1
    version = version or beta_version() or current_version()
    prod = to_production(read(BETA_HTML), version=version)

    leftovers = []
    if 'BETA:START' in prod or 'BETA:END' in prod:
        leftovers.append('unstripped BETA markers')
    if 'IS_BETA' in prod:
        leftovers.append('IS_BETA flag')
    if 'beta-badge' in prod or 'beta-strip' in prod:
        leftovers.append('beta badge markup')
    if 'manifest.beta.json' in prod:
        leftovers.append('beta manifest reference')
    if leftovers:
        print('ERROR: refusing to promote, found %s.' % ', '.join(leftovers))
        print('The BETA:START / BETA:END markers were probably edited by hand.')
        return 1

    write(PROD_HTML, prod)
    n = bump_sw_cache()
    print('Promoted beta -> production.')
    print('  version    : my tasks / %s' % (version or 'unchanged'))
    if n:
        print('  sw cache   : mytasks-prod-v%d' % n)
    print()
    print('Commit and push to publish. Beta and production are now identical.')
    return 0


def cmd_reset_beta():
    os.makedirs(BETA_DIR, exist_ok=True)
    if os.path.exists(BETA_HTML):
        beta_as_prod = to_production(read(BETA_HTML))
        if fingerprint(beta_as_prod) != fingerprint(read(PROD_HTML)):
            reply = input('Beta has unpromoted changes. Discard them? [y/N] ')
            if reply.strip().lower() not in ('y', 'yes'):
                print('Cancelled.')
                return 1
    write(BETA_HTML, to_beta(read(PROD_HTML)))
    write(os.path.join(BETA_DIR, 'manifest.beta.json'), BETA_MANIFEST)
    write(os.path.join(BETA_DIR, 'sw.js'), BETA_SW)
    print('Beta reset from production.')
    print('  beta/index.html')
    print('  beta/manifest.beta.json')
    print('  beta/sw.js')
    return 0


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else 'status'
    if cmd == 'status':
        return cmd_status()
    if cmd == 'promote':
        return cmd_promote(args[1] if len(args) > 1 else None)
    if cmd in ('reset-beta', 'reset'):
        return cmd_reset_beta()
    if cmd == 'bump':
        old, new = bump_beta(args[1] if len(args) > 1 else None)
        print('beta version: %s -> %s' % (old or 'unset', new))
        print('promoting this would release as: %s' % new)
        return 0
    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main())
