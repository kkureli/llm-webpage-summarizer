"""Simple web UI for the webpage summarizer."""

from __future__ import annotations

import markdown
from flask import Flask, render_template, request

from summarize import summarize

app = Flask(__name__)


DEFAULT_URL = "https://cnn.com"


@app.route("/", methods=["GET", "POST"])
def index():
    url = DEFAULT_URL
    summary_html = None
    error = None

    if request.method == "POST":
        url = (request.form.get("url") or "").strip() or DEFAULT_URL
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        try:
            summary = summarize(url)
            summary_html = markdown.markdown(summary)
        except Exception as exc:
            error = str(exc)

    return render_template(
        "index.html",
        url=url,
        summary_html=summary_html,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
