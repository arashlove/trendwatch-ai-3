def render_upload_page(*, error: str | None = None) -> str:
    err_block = ""
    if error:
        err_block = f'<p class="error">{_escape(error)}</p>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>TrendWatch — Full report</title>
  <style>
    :root {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      line-height: 1.5;
      color: #111;
      background: #f6f7f9;
    }}
    body {{ margin: 0; padding: 2rem 1rem; }}
    main {{
      max-width: 40rem;
      margin: 0 auto;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 1.5rem;
      box-shadow: 0 1px 3px rgba(0,0,0,.06);
    }}
    h1 {{ margin: 0 0 .25rem; font-size: 1.35rem; }}
    h2 {{ margin: 1.5rem 0 .5rem; font-size: 1rem; }}
    p {{ margin: .5rem 0; color: #4b5563; }}
    ol {{ margin: .75rem 0; padding-left: 1.25rem; color: #374151; }}
    li {{ margin: .35rem 0; }}
    form {{ margin-top: .75rem; display: grid; gap: .75rem; }}
    textarea {{
      width: 100%;
      min-height: 10rem;
      font-family: ui-monospace, monospace;
      font-size: .8rem;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: .75rem;
      box-sizing: border-box;
    }}
    input[type=file] {{
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      padding: 1rem;
      background: #f8fafc;
    }}
    button {{
      background: #d93900;
      color: #fff;
      border: 0;
      border-radius: 8px;
      padding: .75rem 1rem;
      font-size: 1rem;
      cursor: pointer;
      width: fit-content;
    }}
    button:hover {{ background: #b82f00; }}
    .error {{
      color: #b91c1c;
      background: #fef2f2;
      border: 1px solid #fecaca;
      border-radius: 8px;
      padding: .75rem;
      margin-top: 1rem;
    }}
    .hint {{ font-size: .9rem; }}
    .divider {{
      border: 0;
      border-top: 1px solid #e5e7eb;
      margin: 1.5rem 0;
    }}
  </style>
</head>
<body>
  <main>
    <h1>TrendWatch full assignment report</h1>
    <p class="hint">
      Paste JSON copied from the Devvit app (Step 3). Analysis runs locally with the
      full Python NLP pipeline.
    </p>
    <ol>
      <li>In Reddit playtest, run <strong>Step 1</strong> (collect posts).</li>
      <li>Click <strong>Step 3 — Copy report data</strong>.</li>
      <li>Paste below (or upload a saved <code>.json</code> file).</li>
    </ol>
    {err_block}

    <h2>Paste JSON (recommended)</h2>
    <form action="/upload" method="post">
      <textarea
        name="paste_json"
        placeholder='{{"query":"...","subreddit":"...","posts":[...]}}'
        required
      ></textarea>
      <button type="submit">Run full NLP report</button>
    </form>

    <hr class="divider" />

    <h2>Or upload a file</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input name="file" type="file" accept=".json,application/json" />
      <button type="submit">Upload JSON file</button>
    </form>
  </main>
</body>
</html>"""


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
