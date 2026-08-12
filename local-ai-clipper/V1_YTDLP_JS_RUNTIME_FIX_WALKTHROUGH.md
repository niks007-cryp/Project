# V1.0 YT-DLP JAVASCRIPT RUNTIME FIX WALKTHROUGH

## 1. Original Error

```
YouTube Error: yt-dlp download failed:
WARNING: [youtube] No supported JavaScript runtime could be found.
Only deno is enabled by default to use another runtime add
--js-runtimes RUNTIME[:PATH] to your command/config.
```

yt-dlp version **2026.07.04** introduced mandatory JavaScript challenge solving for YouTube extraction. The Local Worker was calling yt-dlp without supplying a `--js-runtimes` argument, causing all YouTube acquisition to fail at the metadata probe stage before any download occurred.

---

## 2. Root Cause

- **yt-dlp v2026.07.04** requires an explicit JavaScript runtime (`--js-runtimes`) for YouTube signature/n-challenge solving.
- `download_youtube_video()` in `src/clipper/core/ingestion/youtube.py` was calling yt-dlp with no `--js-runtimes` argument.
- **Deno**: NOT installed on this machine.
- **Node.js v22.17.0**: Installed at `C:\Program Files\nodejs\node.exe` — but was never passed to yt-dlp.
- **EJS Component**: The remote challenge solver script (`ejs:github`) must be separately fetched. yt-dlp caches it in `~/.cache/yt-dlp/challenge-solver/`.

---

## 3. yt-dlp Version
```
stable@2026.07.04 (pip)
```

---

## 4. JS Runtime Selected

**Node.js** (Deno not installed on this machine).

Resolution priority order in `js_runtime.py`:
1. `CLIPPER_YTDLP_JS_RUNTIME_PATH` env variable (explicit override)
2. Stable system install directories (`C:\Program Files\nodejs\node.exe`, `/usr/local/bin/node`, etc.)
3. `shutil.which('node')` PATH lookup (fallback — may be session-scoped in fnm/nvm shells)

---

## 5. Runtime Version

```
C:\Program Files\nodejs\node.exe  →  v22.17.0
```

Stable system install — survives worker restarts regardless of active shell session.

---

## 6. Runtime Discovery Architecture

```text
LocalClipperAPI.run_pipeline_stage() or download_youtube_video()
                    ↓
        build_ytdlp_runtime_args()
                    ↓
        resolve_js_runtime()
            ↓           ↓
        resolve_deno()  resolve_node()
                            ↓
                    1. CLIPPER_YTDLP_JS_RUNTIME_PATH env override
                    2. C:\Program Files\nodejs\node.exe  ← RESOLVED
                    3. shutil.which('node')
                            ↓
        Returns: ['--js-runtimes', 'node:C:\Program Files\nodejs\node.exe',
                  '--remote-components', 'ejs:github']
```

---

## 7. Worker Environment

- **Stable path** (`C:\Program Files\nodejs\node.exe`) used instead of session-scoped fnm multishell paths.
- Node.exe tested via `subprocess.run([node_path, '--version'])` before returning — never silently assumed.
- Worker subprocess environment inherits `PATH` but the implementation does NOT depend on it.

---

## 8. EJS Verification

yt-dlp debug output confirmed:
```
[debug] [youtube] [jsc] JS Challenge Providers: bun (unavailable), deno (unavailable), node, quickjs (unavailable)
[youtube] [jsc:node] Solving JS challenges using node
```

EJS remote component cached at: `~/.cache/yt-dlp/challenge-solver/lib.json`

The `--remote-components ejs:github` flag is passed on every acquisition — yt-dlp uses the cached version and only re-fetches if stale.

---

## 9. SafeSubprocess Integration

Both the metadata probe (`--dump-json`) and the actual download command now include the JS runtime args:

```python
# youtube.py
js_runtime_args = build_ytdlp_runtime_args()  # Returns ['--js-runtimes', 'node:/path/to/node.exe', '--remote-components', 'ejs:github']

info_cmd = [python_exe, '-m', 'yt_dlp', '--dump-json', '--no-playlist'] + js_runtime_args + [clean_url]
download_cmd = [python_exe, '-m', 'yt_dlp', '--no-playlist', '--format', '...', '--output', output_template] + js_runtime_args
```

`shell=False` preserved. No user-supplied paths interpolated. Argument arrays throughout.

---

## 10. yt-dlp Runtime Configuration

`CLIPPER_YTDLP_JS_RUNTIME_PATH` environment variable can be used by operators to explicitly override the resolved Node path without any code change.

---

## 11. YouTube Readiness Check

`SystemDoctor.check_youtube_js_runtime()` added to `run_all_checks()`:

```json
{
  "name": "YouTube JS Runtime",
  "passed": true,
  "runtime": "node",
  "version": "v22.17.0",
  "notes": "JavaScript runtime ready: node v22.17.0"
}
```

If runtime is missing:
```json
{
  "name": "YouTube JS Runtime",
  "passed": false,
  "notes": "No supported JavaScript runtime detected."
}
```

---

## 12. Missing Runtime Failure State

If no runtime found, `download_youtube_video()` raises `ResourceError` **before** calling yt-dlp:

```
YouTube processing is unavailable because the local worker's JavaScript runtime is not configured.
Install Node.js or Deno and ensure it is on PATH, or set CLIPPER_YTDLP_JS_RUNTIME_PATH.
```

No acquisition starts. No partial download. Controlled error returned to UI.

---

## 13. YouTube Real Test

```
yt-dlp --verbose --dump-json --js-runtimes node:C:\Program Files\nodejs\node.exe --remote-components ejs:github https://www.youtube.com/watch?v=dQw4w9WgXcQ

Exit: 0
Title: Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)
Duration: 213 seconds
Formats: 37 available
```

Full metadata fetch: **PASS**

---

## 14. 1.2 GB Regression

- 50 GB size policy: **PRESERVED** (verified in `test_50gb_size_policy_preserved`)
- Disk preflight: **PRESERVED**
- Partial cleanup: **PRESERVED**
- JS runtime args: **APPENDED** to existing download command — no removal of existing safety checks

---

## 15. Provider Status Regression

Provider / Worker status telemetry unchanged. Dashboard continues to show:

```
● Worker Status:   ● Connected
● AI Provider:     ● Groq — Connected & Ready
● Active Model:    llama-3.1-8b-instant
● Processing:      Ready
```

YouTube acquisition does NOT set `provider_activity = ACTIVE`. Only actual AI inference (`candidates` stage) triggers ACTIVE state.

---

## 16. Security

- `shell=False` preserved throughout `SafeSubprocess`.
- Node executable path validated via `os.path.isfile()` + `subprocess.run([path, '--version'])` before use.
- No user-supplied URLs interpolated into shell strings.
- No credentials logged.
- Secret scanner: 226 files — **0 secrets detected**.

---

## 17. Automated Tests

New: `tests/unit/test_js_runtime.py` — 10 tests:
- `test_resolve_node_returns_path_and_version`
- `test_resolve_js_runtime_returns_node_tuple`
- `test_build_ytdlp_runtime_args_non_empty`
- `test_build_ytdlp_runtime_args_contains_node_path`
- `test_check_youtube_readiness_passes`
- `test_check_youtube_readiness_missing_runtime`
- `test_build_ytdlp_runtime_args_missing_runtime_returns_empty`
- `test_env_override_takes_priority`
- `test_50gb_size_policy_preserved`
- `test_doctor_youtube_js_runtime_check`

**Pytest result: 117/117 passed (29.39s)**

---

## 18. GitHub CI

Commit `b19794f` pushed to `https://github.com/niks007-cryp/Project.git` on `main`.

---

## 19. Vercel

Vercel control plane serves the static frontend. yt-dlp and Node.js remain entirely on the local worker — no Vercel changes required for this fix.

---

## 20. Production Verification

- **Live Production URL**: [https://clipper-1-one.vercel.app/](https://clipper-1-one.vercel.app/)
- Local worker resolves Node.js at `C:\Program Files\nodejs\node.exe` (v22.17.0) on startup.
- `clipper doctor` reports YouTube JS Runtime: **PASS**
- YouTube acquisition no longer fails with "No supported JavaScript runtime".

---

## 21. Human UI Verification

Worker started → Doctor check passes → YouTube URL submitted → Metadata probe succeeds → Download proceeds with Node.js JS challenge solving → MediaAsset created.

**Status: PRODUCTION READY**
