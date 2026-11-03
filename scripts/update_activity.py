#!/usr/bin/env python3
"""Generate images/activity.svg showing the last-year contribution heatmap."""
import json
import os
import urllib.request

USER = "annabergite"


def graphql(query, variables):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    req = urllib.request.Request("https://api.github.com/graphql")
    if token:
        req.add_header("Authorization", "bearer " + token)
    req.add_header("User-Agent", "annabergite-activity-bot")
    req.add_header("Content-Type", "application/json")
    body = json.dumps({"query": query, "variables": variables}).encode()
    with urllib.request.urlopen(req, data=body, timeout=30) as r:
        return json.loads(r.read().decode())


QUERY = """
query($u: String!) {
  user(login: $u) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date weekday contributionCount color }
        }
      }
    }
  }
}
"""


def main():
    data = graphql(QUERY, {"u": USER})
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = cal["totalContributions"]
    weeks = cal["weeks"]

    cell = 11
    gap = 3
    pad = 18
    ncols = len(weeks)
    nrows = 7
    grid_w = ncols * (cell + gap) - gap
    grid_h = nrows * (cell + gap) - gap
    title_h = 34
    width = pad * 2 + grid_w
    height = pad + title_h + grid_h + pad

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
        '<rect width="%d" height="%d" rx="10" fill="#ffffff"/>' % (width, height),
        '<text x="%d" y="%d" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="14" font-weight="700" fill="#212121">活动概览 / Activity Overview · %d contributions in the last year</text>' % (pad, pad + 13, total),
    ]

    y0 = pad + title_h
    for wi, week in enumerate(weeks):
        for day in week["contributionDays"]:
            x = pad + wi * (cell + gap)
            y = y0 + day["weekday"] * (cell + gap)
            color = day["color"] or "#ebedf0"
            count = day["contributionCount"]
            parts.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s"><title>%s: %d contributions</title></rect>' % (x, y, cell, cell, color, day["date"], count))

    parts.append("</svg>")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "images")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "activity.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s: %d contributions across %d weeks" % (out, total, ncols))


if __name__ == "__main__":
    main()
