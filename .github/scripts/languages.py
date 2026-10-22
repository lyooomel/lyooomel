"""Render metrics.languages.svg from the languages of every owned repo (private included)."""
import json, os, sys, urllib.request
from collections import Counter
from html import escape

TOKEN = os.environ["GH_TOKEN"]
OUT = sys.argv[1] if len(sys.argv) > 1 else "metrics.languages.svg"
TOP = 8
COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26", "CSS": "#663399",
    "Go": "#00ADD8", "C++": "#f34b7d", "Python": "#3572A5", "Dart": "#00B4AB",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "PHP": "#4F5D95", "Shell": "#89e051",
}


def get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


repos, page = [], 1
while batch := get(f"https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}"):
    repos += batch
    page += 1

total = Counter()
for repo in repos:
    if not repo["fork"]:
        total.update(get(repo["languages_url"]))

top = total.most_common(TOP)
size = sum(total.values()) or 1

W, BAR_Y, ROW_H = 420, 40, 22
rows = (len(top) + 1) // 2
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{BAR_Y + 26 + rows * ROW_H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
       '<text x="0" y="20" font-size="15" font-weight="600" fill="#58a6ff">Most Used Languages</text>']
x = 0.0
for name, b in top:
    w = b / size * W
    svg.append(f'<rect x="{x:.2f}" y="{BAR_Y}" width="{w:.2f}" height="8" fill="{COLORS.get(name, "#8b949e")}"/>')
    x += w
for i, (name, b) in enumerate(top):
    cx, cy = (i % 2) * W / 2, BAR_Y + 30 + (i // 2) * ROW_H
    svg.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS.get(name, "#8b949e")}"/>')
    svg.append(f'<text x="{cx + 16}" y="{cy}" font-size="12" fill="#8b949e">{escape(name)} {b / size:.1%}</text>')
svg.append("</svg>")

with open(OUT, "w") as f:
    f.write("\n".join(svg) + "\n")
print(f"{len(repos)} repos -> {OUT}: " + ", ".join(f"{n} {b / size:.1%}" for n, b in top))
