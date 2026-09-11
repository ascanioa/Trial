#!/usr/bin/env python3
"""Local browser interface for couples-analyst.

Runs entirely on your machine. The server binds to 127.0.0.1 only, makes no outbound
connections, and stores nothing: the transcript exists in memory for the length of one
request. Nothing is written to disk unless you click a download link.

    python3 serve.py            # then open http://127.0.0.1:8000
    python3 serve.py --port 9000
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))

from couples_analyst import __version__  # noqa: E402
from couples_analyst.compose import analyze  # noqa: E402
from couples_analyst.report import render  # noqa: E402

MAX_BYTES = 1_000_000  # a conversation transcript is never this big; refuse the rest

# --------------------------------------------------------------------------------------
# Minimal markdown rendering for the subset report.py emits. Everything is HTML-escaped
# BEFORE any markup is applied, because the report quotes the transcript verbatim and the
# transcript is untrusted input.
# --------------------------------------------------------------------------------------

_INLINE = (
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\w)_(.+?)_(?!\w)"), r"<em>\1</em>"),
    (re.compile(r"`(.+?)`"), r"<code>\1</code>"),
)


def _inline(text: str) -> str:
    for pattern, repl in _INLINE:
        text = pattern.sub(repl, text)
    return text


def markdown_to_html(md: str) -> str:
    out: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for raw in md.splitlines():
        line = html.escape(raw.rstrip(), quote=False)
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        if stripped == "---":
            close_list()
            out.append("<hr>")
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if stripped.startswith("&gt; "):  # blockquote (escaped '>')
            close_list()
            out.append(f"<blockquote>{_inline(stripped[5:])}</blockquote>")
            continue
        if stripped.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
            continue
        close_list()
        out.append(f"<p>{_inline(stripped)}</p>")
    close_list()
    return "\n".join(out)


# --------------------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------------------

STYLE = """
:root { --bg:#fbfaf8; --fg:#1d1c1a; --muted:#6b6762; --line:#e3dfd9; --accent:#7a5c3e;
        --quote:#f3efe9; --warn:#8a3b2f; --warnbg:#fdf2ef; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#17161a; --fg:#e8e6e3; --muted:#a09a93; --line:#33302e; --accent:#c9a77f;
          --quote:#201e22; --warn:#e8a08f; --warnbg:#2a1d1b; }
}
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.6 -apple-system,
       BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
.wrap { max-width:820px; margin:0 auto; padding:32px 20px 72px; }
h1 { font-size:1.55rem; margin:0 0 4px; letter-spacing:-.01em; }
h2 { font-size:1.2rem; margin:2.2em 0 .6em; padding-bottom:.3em; border-bottom:1px solid var(--line); }
h3 { font-size:1.02rem; margin:1.8em 0 .5em; color:var(--accent); }
h4 { font-size:.9rem; margin:1.4em 0 .4em; text-transform:uppercase; letter-spacing:.06em;
     color:var(--muted); }
p, li { margin:.5em 0; }
blockquote { margin:.35em 0; padding:.5em .8em; background:var(--quote);
             border-left:3px solid var(--accent); border-radius:0 4px 4px 0; font-size:.94rem; }
hr { border:0; border-top:1px solid var(--line); margin:1.6em 0; }
code { background:var(--quote); padding:.1em .35em; border-radius:3px; font-size:.88em; }
.sub { color:var(--muted); font-size:.9rem; margin:0 0 1.6em; }
.privacy { background:var(--quote); border:1px solid var(--line); border-radius:8px;
           padding:12px 16px; font-size:.88rem; color:var(--muted); margin-bottom:24px; }
.privacy strong { color:var(--fg); }
label { display:block; font-size:.85rem; font-weight:600; margin:16px 0 6px; }
textarea, input[type=text], select { width:100%; font-family:ui-monospace,SFMono-Regular,
  Menlo,monospace; font-size:.9rem; padding:10px 12px; background:var(--bg); color:var(--fg);
  border:1px solid var(--line); border-radius:6px; }
textarea { min-height:230px; resize:vertical; }
textarea:focus, input:focus, select:focus { outline:2px solid var(--accent); outline-offset:1px; }
.row { display:flex; gap:14px; flex-wrap:wrap; }
.row > div { flex:1 1 180px; }
.check { display:flex; align-items:center; gap:8px; margin-top:16px; font-size:.9rem; }
.check input { width:auto; }
button { margin-top:20px; background:var(--accent); color:#fff; border:0; border-radius:6px;
         padding:11px 22px; font-size:.95rem; font-weight:600; cursor:pointer; }
button:hover { filter:brightness(1.08); }
.actions { margin:24px 0; display:flex; gap:10px; flex-wrap:wrap; }
.actions a { display:inline-block; padding:8px 14px; border:1px solid var(--line);
             border-radius:6px; color:var(--accent); text-decoration:none; font-size:.88rem; }
.actions a:hover { background:var(--quote); }
.notice { background:var(--warnbg); border:1px solid var(--warn); color:var(--warn);
          border-radius:8px; padding:14px 16px; margin-bottom:20px; font-size:.92rem; }
.drop { border:1px dashed var(--line); border-radius:6px; padding:8px 12px; font-size:.82rem;
        color:var(--muted); margin-top:8px; }
footer { margin-top:48px; padding-top:16px; border-top:1px solid var(--line);
         color:var(--muted); font-size:.8rem; }
"""

FORM = """
<form method="post" action="/">
  <label for="transcript">Transcript</label>
  <textarea id="transcript" name="transcript" required
    placeholder="Ana: I waited an hour last night. You didn't call.&#10;Luis: I know. My phone died.&#10;&#10;Plain text, Speaker: lines, a WhatsApp export, or subtitles - the format is detected."
    >{transcript}</textarea>
  <div class="drop">Or drop a .txt / .srt / .vtt file anywhere on this page.</div>

  <div class="row">
    <div>
      <label for="language">Language</label>
      <select id="language" name="language">
        <option value="">Detect automatically</option>
        <option value="en">English</option>
        <option value="es">Espanol</option>
      </select>
    </div>
    <div>
      <label for="format">Input format</label>
      <select id="format" name="format">
        <option value="">Detect automatically</option>
        <option value="speaker_turns">Speaker: text</option>
        <option value="chat_export">Chat export</option>
        <option value="subtitles">Subtitles</option>
        <option value="plain">Plain text</option>
      </select>
    </div>
  </div>

  <label for="request">What are you hoping to get from this? (optional)</label>
  <input type="text" id="request" name="request"
         placeholder="Screened for uses this instrument declines - see the README.">

  <div class="check">
    <input type="checkbox" id="keepnames" name="keepnames" value="1">
    <label for="keepnames" style="margin:0;font-weight:400">Keep real names (default: anonymize to A / B)</label>
  </div>

  <button type="submit">Analyze</button>
</form>
"""

DROP_JS = """
<script>
(function () {
  var ta = document.getElementById('transcript');
  if (ta) {
    ['dragover','drop'].forEach(function (e) {
      document.addEventListener(e, function (ev) { ev.preventDefault(); });
    });
    document.addEventListener('drop', function (ev) {
      var f = ev.dataTransfer && ev.dataTransfer.files && ev.dataTransfer.files[0];
      if (!f) return;
      var r = new FileReader();
      r.onload = function () { ta.value = r.result; };
      r.readAsText(f);
    });
  }
  // Downloads are built in the browser from text already on this page: still no network.
  document.querySelectorAll('a[data-src]').forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var el = document.getElementById(a.getAttribute('data-src'));
      var blob = new Blob([el.textContent], {type: a.getAttribute('data-type')});
      var url = URL.createObjectURL(blob);
      var tmp = document.createElement('a');
      tmp.href = url; tmp.download = a.getAttribute('data-name');
      document.body.appendChild(tmp); tmp.click(); document.body.removeChild(tmp);
      setTimeout(function () { URL.revokeObjectURL(url); }, 0);
    });
  });
})();
</script>
"""


def page(body: str) -> bytes:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>couples-analyst</title><style>{STYLE}</style></head>
<body><div class="wrap">
<h1>couples-analyst</h1>
<p class="sub">Descriptive coding of one conversation. Not a diagnosis, not a clinical
assessment, not a prediction.</p>
<div class="privacy"><strong>This runs entirely on your machine.</strong> The server is bound
to 127.0.0.1, makes no outbound connections, and keeps nothing: your transcript exists in
memory for one request and is never written to disk. Both partners should know a conversation
is being analyzed.</div>
{body}
<footer>couples-analyst {__version__} &middot; local only &middot; stop with Ctrl-C in the terminal</footer>
</div>{DROP_JS}</body></html>""".encode("utf-8")


def results_page(doc: dict, report_md: str, transcript: str) -> bytes:
    gate = doc["safety_gate"]["halted_analysis"]
    notice = ""
    if gate:
        notice = (
            '<div class="notice"><strong>The safety screen found markers in this '
            "transcript, so the conflict-pattern analysis was withheld rather than "
            "qualified.</strong> The frameworks this instrument implements assume two "
            "partners with roughly symmetric power; where that does not hold, describing "
            "the exchange as a shared cycle would misdescribe it.</div>"
        )
    downloads = (
        '<div class="actions">'
        '<a href="#" data-src="raw-md" data-name="report.md" data-type="text/markdown">'
        "Download report.md</a>"
        '<a href="#" data-src="raw-json" data-name="analysis.json" data-type="application/json">'
        "Download analysis.json</a>"
        '<a href="/">Analyze another</a>'
        "</div>"
    )
    hidden = (
        f'<div hidden id="raw-md">{html.escape(report_md)}</div>'
        f'<div hidden id="raw-json">{html.escape(json.dumps(doc, ensure_ascii=False, indent=2))}</div>'
    )
    return page(notice + downloads + markdown_to_html(report_md) + downloads + hidden)


def refusal_page(reason: str) -> bytes:
    return page(
        f'<div class="notice">{html.escape(reason).replace(chr(10) + chr(10), "<br><br>")}</div>'
        '<div class="actions"><a href="/">Back</a></div>'
    )


class Handler(BaseHTTPRequestHandler):
    server_version = f"couples-analyst/{__version__}"

    def _send(self, body: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # This page never loads anything external; say so to the browser too.
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def _form(self, transcript: str = "") -> bytes:
        # Always escaped: a transcript containing "</textarea>" must not break out of it.
        return page(FORM.format(transcript=html.escape(transcript)))

    def do_GET(self) -> None:  # noqa: N802
        if self.path not in ("/", "/index.html"):
            self._send(page('<div class="notice">Not found.</div>'), 404)
            return
        self._send(self._form())

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BYTES:
            self._send(page('<div class="notice">That input is too large.</div>'), 413)
            return
        fields = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))
        transcript = (fields.get("transcript") or [""])[0]
        if not transcript.strip():
            self._send(self._form())
            return

        result = analyze(
            transcript,
            input_format=(fields.get("format") or [""])[0] or None,
            anonymize=not (fields.get("keepnames") or [""])[0],
            language=(fields.get("language") or [""])[0] or None,
            request_text=(fields.get("request") or [""])[0],
        )
        if isinstance(result, str):  # adversarial-use refusal
            self._send(refusal_page(result))
            return
        doc = result.to_json()
        self._send(results_page(doc, render(doc), transcript))

    def log_message(self, fmt: str, *args: object) -> None:
        # Request logs would record that an analysis happened, with timestamps. Not worth
        # writing anything about a private conversation to a terminal someone may screenshot.
        return


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args()
    # 127.0.0.1, never 0.0.0.0: binding to all interfaces would put a form containing
    # private conversations on the local network.
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    print(f"couples-analyst {__version__} - open http://127.0.0.1:{args.port}")
    print("Local only: bound to 127.0.0.1, no outbound connections, nothing stored.")
    print("Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
