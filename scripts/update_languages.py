#!/usr/bin/env python3
"""Generate images/languages.svg showing aggregated GitHub language stats."""
import json
import os
import urllib.request

USER = "annabergite"
EXCLUDE = {"HTML", "CSS", "JavaScript", "TypeScript", "Vue", "SCSS", "Sass", "Less"}  # 前端语言不计入

COLORS = {
    "Java": "#b07219",
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "Go": "#00ADD8",
    "Rust": "#dea584",
    "Kotlin": "#A97BFF",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Shell": "#89e051",
    "FreeMarker": "#0050b2",
    "Vue": "#41b883",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
}


def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", "token " + token)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "annabergite-profile-lang-bot")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main():
    repos = api("/users/%s/repos?per_page=100" % USER)
    langs = {}
    for repo in repos:
        try:
            data = api("/repos/%s/%s/languages" % (USER, repo["name"]))
        except Exception:
            continue
        for lang, size in data.items():
            if lang in EXCLUDE:
                continue
            langs[lang] = langs.get(lang, 0) + size

    total = sum(langs.values()) or 1
    items = sorted(langs.items(), key=lambda kv: -kv[1])[:3]

    width = 400
    pad = 18
    title_y = pad + 18
    bar_x = 118
    pct_w = 46
    bar_w = width - bar_x - pct_w - pad
    bar_h = 14
    row_h = 34
    height = pad + 40 + len(items) * row_h + pad

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect width="%d" height="%d" rx="10" fill="#ffffff"/>' % (width, height),
        '<text x="%d" y="%d" text-anchor="middle" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="15" font-weight="700" fill="#212121">语言分布 / Top Languages</text>' % (width / 2, title_y),
    ]

    y = pad + 40
    for lang, size in items:
        pct = size / total * 100
        fill_w = max(bar_w * pct / 100, 2)
        color = COLORS.get(lang, "#9e9e9e")
        mid = y + bar_h / 2 + 4
        parts.append('<text x="%d" y="%d" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="12" fill="#212121">%s</text>' % (pad, mid, lang))
        parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="7" fill="#ececec"/>' % (bar_x, y, bar_w, bar_h))
        parts.append('<rect x="%d" y="%d" width="%.1f" height="%d" rx="7" fill="%s"/>' % (bar_x, y, fill_w, bar_h, color))
        parts.append('<text x="%d" y="%d" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="#6b7280">%.1f%%</text>' % (bar_x + bar_w + 8, mid, pct))
        y += row_h

    parts.append("</svg>")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "languages.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s with %d languages" % (out, len(items)))


if __name__ == "__main__":
    main()
