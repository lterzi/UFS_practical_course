"""Build a single self-contained HTML page with a scrubber/slider to step
through CAMS aod550 leadtime frames over a date range.

Reuses the PNGs already produced by plot_cams_aod550.py (in OUT_DIR),
downsamples + re-encodes them as JPEG to keep the page small, and embeds
them as base64 data URIs so the page has no external dependencies.

Usage (activate MTG_env first):
    source ~/MTG_env/bin/activate
    python make_day_viewer.py --start 20260807 --end 20260812
"""
import argparse
import base64
import datetime
import io
import json
import os

from PIL import Image

PLOTS_DIR = "plots"
FRAME_WIDTH = 700
JPEG_QUALITY = 80


def normalize_date(date: str) -> str:
    fmt = "%Y-%m-%d" if "-" in date else "%Y%m%d"
    return datetime.datetime.strptime(date, fmt).strftime("%Y-%m-%d")


def build_frames(start_date: str, end_date: str) -> list[dict]:
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    frames = []
    t = start
    leadtime = 0
    while t <= end:
        ts = t.strftime("%Y-%m-%d_%H")
        path = os.path.join(PLOTS_DIR, f"cams_aod550_{ts}.png")
        if os.path.exists(path):
            im = Image.open(path).convert("RGB")
            scale = FRAME_WIDTH / im.width
            im = im.resize((FRAME_WIDTH, round(im.height * scale)), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=JPEG_QUALITY)
            data_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

            frames.append({
                "leadtime": leadtime,
                "valid": t.strftime("%Y-%m-%d %H:%M"),
                "day_start": t.hour == 0,
                "src": data_uri,
            })
        t += datetime.timedelta(hours=1)
        leadtime += 1
    return frames


HTML_TEMPLATE = r"""<!doctype html>
<title>CAMS AOD550 — {start_date} to {end_date}</title>
<style>
@font-face {{
  font-family: "Berkeley Mono Fallback";
  src: local("Cascadia Code"), local("SF Mono"), local("Consolas");
}}

:root {{
  --bg: #eef1f4;
  --canvas: #dfe4e9;
  --surface: #ffffff;
  --surface-2: #f3f5f7;
  --border: #d3d9e0;
  --text: #171b21;
  --text-dim: #5b6572;
  --accent: #c1571e;
  --accent-soft: #f0dccb;
  --focus: #c1571e;
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #10141a;
    --canvas: #0a0d11;
    --surface: #171d25;
    --surface-2: #1c232c;
    --border: #2b3441;
    --text: #e7ebf0;
    --text-dim: #8a94a3;
    --accent: #e2793c;
    --accent-soft: #3a2a1d;
    --focus: #e2793c;
  }}
}}

:root[data-theme="dark"] {{
  --bg: #10141a;
  --canvas: #0a0d11;
  --surface: #171d25;
  --surface-2: #1c232c;
  --border: #2b3441;
  --text: #e7ebf0;
  --text-dim: #8a94a3;
  --accent: #e2793c;
  --accent-soft: #3a2a1d;
  --focus: #e2793c;
}}

:root[data-theme="light"] {{
  --bg: #eef1f4;
  --canvas: #dfe4e9;
  --surface: #ffffff;
  --surface-2: #f3f5f7;
  --border: #d3d9e0;
  --text: #171b21;
  --text-dim: #5b6572;
  --accent: #c1571e;
  --accent-soft: #f0dccb;
  --focus: #c1571e;
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: ui-sans-serif, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  display: flex;
  justify-content: center;
  padding: 2.5rem 1.25rem 3rem;
}}

.panel {{
  width: 100%;
  max-width: 900px;
}}

.eyebrow {{
  font-family: ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", Menlo, Consolas, monospace;
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 0.6rem;
}}

h1 {{
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  margin: 0 0 0.3rem;
  text-wrap: balance;
}}

.subtitle {{
  color: var(--text-dim);
  font-size: 0.92rem;
  margin: 0 0 1.6rem;
}}

.subtitle b {{ color: var(--text); font-weight: 600; }}

.frame-shell {{
  position: relative;
  background: var(--canvas);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 14px;
}}

.frame-shell::before,
.frame-shell::after,
.corner-br::before,
.corner-br::after {{
  content: "";
  position: absolute;
  width: 14px;
  height: 14px;
  border: 2px solid var(--text-dim);
  opacity: 0.55;
}}
.frame-shell::before {{ top: 6px; left: 6px; border-right: none; border-bottom: none; }}
.frame-shell::after {{ top: 6px; right: 6px; border-left: none; border-bottom: none; }}

.corner-br {{ position: absolute; inset: 0; pointer-events: none; }}
.corner-br::before {{ bottom: 6px; left: 6px; top: auto; border-right: none; border-top: none; }}
.corner-br::after {{ bottom: 6px; right: 6px; top: auto; border-left: none; border-top: none; }}

.frame-img-wrap {{
  border-radius: 2px;
  overflow: hidden;
  background: var(--surface);
  line-height: 0;
}}

.frame-img-wrap img {{
  width: 100%;
  height: auto;
  display: block;
}}

.readout {{
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin: 1.1rem 0 0.9rem;
  font-family: ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", Menlo, Consolas, monospace;
  font-variant-numeric: tabular-nums;
}}

.readout .valid-time {{
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}}

.readout .leadtime {{
  color: var(--text-dim);
  font-size: 0.85rem;
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 0.2rem 0.55rem;
  border-radius: 3px;
  white-space: nowrap;
}}

.transport {{
  display: flex;
  align-items: center;
  gap: 0.75rem;
}}

button.tbtn {{
  appearance: none;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex: none;
}}

button.tbtn:hover {{ border-color: var(--accent); color: var(--accent); }}
button.tbtn:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}

button.tbtn svg {{ width: 15px; height: 15px; fill: currentColor; }}

#playBtn.is-playing .icon-play {{ display: none; }}
#playBtn:not(.is-playing) .icon-pause {{ display: none; }}

.scrub {{
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}}

input[type="range"] {{
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  outline: none;
  margin: 0;
}}

input[type="range"]::-webkit-slider-thumb {{
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--surface);
  box-shadow: 0 0 0 1px var(--accent);
  cursor: pointer;
  margin-top: -6px;
}}

input[type="range"]::-moz-range-thumb {{
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--surface);
  box-shadow: 0 0 0 1px var(--accent);
  cursor: pointer;
}}

input[type="range"]::-webkit-slider-runnable-track {{ height: 4px; border-radius: 2px; }}

.ticks {{
  position: relative;
  height: 1.1rem;
  font-family: ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", Menlo, Consolas, monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
}}

.ticks span {{
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  opacity: 0.75;
  white-space: nowrap;
}}

.ticks span:first-child {{ transform: translateX(0); }}
.ticks span:last-child {{ transform: translateX(-100%); }}

footer {{
  margin-top: 1.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
  color: var(--text-dim);
  font-size: 0.78rem;
  line-height: 1.5;
}}

footer code {{
  font-family: ui-monospace, "SF Mono", "Cascadia Code", "Roboto Mono", Menlo, Consolas, monospace;
  background: var(--surface-2);
  padding: 0.05rem 0.35rem;
  border-radius: 3px;
}}

@media (prefers-reduced-motion: reduce) {{
  * {{ transition: none !important; }}
}}
</style>

<div class="panel">
  <p class="eyebrow">CAMS &middot; Atmosphere Monitoring Service</p>
  <h1>Total Aerosol Optical Depth at 550&nbsp;nm</h1>
  <p class="subtitle"><b>{start_date}</b> &ndash; <b>{end_date}</b> &middot; {n_frames} hourly frames &middot; region 90&deg;W&ndash;65&deg;E, 10&deg;&ndash;75&deg;N</p>

  <div class="frame-shell">
    <div class="corner-br"></div>
    <div class="frame-img-wrap">
      <img id="frameImg" src="" alt="CAMS aod550 map" />
    </div>
  </div>

  <div class="readout">
    <span class="valid-time" id="validTime">&nbsp;</span>
    <span class="leadtime" id="leadtimeBadge">&nbsp;</span>
  </div>

  <div class="transport">
    <button class="tbtn" id="stepBack" title="Previous hour" aria-label="Previous hour">
      <svg viewBox="0 0 16 16"><path d="M4 2h2v12H4zM13 3l-7 5 7 5z"/></svg>
    </button>
    <button class="tbtn" id="playBtn" title="Play / pause" aria-label="Play or pause">
      <svg class="icon-play" viewBox="0 0 16 16"><path d="M4 2l10 6-10 6z"/></svg>
      <svg class="icon-pause" viewBox="0 0 16 16"><path d="M4 2h3v12H4zM9 2h3v12H9z"/></svg>
    </button>
    <button class="tbtn" id="stepFwd" title="Next hour" aria-label="Next hour">
      <svg viewBox="0 0 16 16"><path d="M10 2h2v12h-2zM3 3l7 5-7 5z"/></svg>
    </button>
    <div class="scrub">
      <input type="range" id="slider" min="0" max="{max_index}" value="0" step="1" />
      <div class="ticks" id="ticks"></div>
    </div>
  </div>

  <footer>
    Source: ADS dataset <code>cams-global-atmospheric-composition-forecasts</code>, variable <code>total_aerosol_optical_depth_550nm</code>.
    {n_frames} hourly frames from <b>{start_date}</b> to <b>{end_date}</b>. Use &larr;/&rarr; or drag the scrubber; space toggles play.
  </footer>
</div>

<script>
const frames = {frames_json};

const img = document.getElementById("frameImg");
const validTime = document.getElementById("validTime");
const leadtimeBadge = document.getElementById("leadtimeBadge");
const slider = document.getElementById("slider");
const playBtn = document.getElementById("playBtn");
const stepBack = document.getElementById("stepBack");
const stepFwd = document.getElementById("stepFwd");
const ticks = document.getElementById("ticks");

frames.forEach((f, i) => {{
  if (!f.day_start) return;
  const el = document.createElement("span");
  el.style.left = (i / (frames.length - 1) * 100) + "%";
  el.textContent = f.valid.slice(5, 10);
  ticks.appendChild(el);
}});

let index = 0;
let playing = false;
let timer = null;

function render() {{
  const f = frames[index];
  img.src = f.src;
  validTime.textContent = f.valid + " UTC";
  leadtimeBadge.textContent = "+" + f.leadtime + "h";
  slider.value = index;
}}

function setIndex(i) {{
  index = ((i % frames.length) + frames.length) % frames.length;
  render();
}}

function stopPlaying() {{
  playing = false;
  playBtn.classList.remove("is-playing");
  if (timer) {{ clearInterval(timer); timer = null; }}
}}

function startPlaying() {{
  playing = true;
  playBtn.classList.add("is-playing");
  timer = setInterval(() => setIndex(index + 1), 450);
}}

slider.addEventListener("input", () => {{ stopPlaying(); setIndex(Number(slider.value)); }});
stepBack.addEventListener("click", () => {{ stopPlaying(); setIndex(index - 1); }});
stepFwd.addEventListener("click", () => {{ stopPlaying(); setIndex(index + 1); }});
playBtn.addEventListener("click", () => {{ playing ? stopPlaying() : startPlaying(); }});

document.addEventListener("keydown", (e) => {{
  if (e.key === "ArrowLeft") {{ stopPlaying(); setIndex(index - 1); }}
  else if (e.key === "ArrowRight") {{ stopPlaying(); setIndex(index + 1); }}
  else if (e.key === " ") {{ e.preventDefault(); playing ? stopPlaying() : startPlaying(); }}
}});

render();
</script>
"""


def build_html(start_date: str, end_date: str, frames: list[dict]) -> str:
    return HTML_TEMPLATE.format(
        start_date=start_date,
        end_date=end_date,
        max_index=len(frames) - 1,
        n_frames=len(frames),
        frames_json=json.dumps(frames),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="YYYYMMDD or YYYY-MM-DD, first day to include")
    parser.add_argument("--end", required=True, help="YYYYMMDD or YYYY-MM-DD, last day to include")
    parser.add_argument("--out", default=None, help="output .html path")
    args = parser.parse_args()

    start_date = normalize_date(args.start)
    end_date = normalize_date(args.end)
    frames = build_frames(start_date, end_date)
    if not frames:
        raise SystemExit(f"no frames found in {PLOTS_DIR} between {start_date} and {end_date}")

    html = build_html(start_date, end_date, frames)
    out_path = args.out or os.path.join(
        PLOTS_DIR, f"viewer_{start_date.replace('-', '')}_{end_date.replace('-', '')}.html"
    )
    with open(out_path, "w") as f:
        f.write(html)
    print(f"saved {out_path} ({len(frames)} frames)")
