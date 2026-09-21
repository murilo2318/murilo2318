"""Gera o card "Projetos selecionados" a partir da API pública do GitHub.

Lê metadados e bytes por linguagem de cada repositório listado em PROJECTS e
grava assets/featured-work-light.svg e assets/featured-work-dark.svg.
Usa apenas a biblioteca padrão do Python.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "murilo2318")
TOKEN = os.environ.get("GITHUB_TOKEN")

PROJECTS = [
    {
        "repo": "forzy-sprint3",
        "title": "Forzy — Gêmeo Digital",
        "label": "INTELIGÊNCIA INDUSTRIAL",
        "summary": "Digital twin · alertas · recomendações de manutenção",
    },
    {
        "repo": "fiap-chatbot-rag",
        "title": "FIAP AI Chatbot",
        "label": "IA GENERATIVA",
        "summary": "RAG · FastAPI · banco vetorial Qdrant",
    },
    {
        "repo": "UrbanSense-2.0",
        "title": "UrbanSense 2.0",
        "label": "IOT & TELEMETRIA",
        "summary": "ESP32 · sensores ambientais · MQTT",
    },
]

LANGUAGE_COLORS = {
    "C": "#555555",
    "C++": "#f34b7d",
    "CSS": "#663399",
    "Dockerfile": "#5c7f8c",
    "HTML": "#e34c26",
    "JavaScript": "#d4a900",
    "Jupyter Notebook": "#c85d13",
    "Python": "#3572a5",
    "Shell": "#6f9f45",
    "TypeScript": "#3178c6",
}

THEMES = {
    "light": {
        "background": "#f5f1e8",
        "eyebrow": "#8a5a20",
        "heading": "#17251b",
        "text": "#34483a",
        "muted": "#657368",
        "rule": "#d9d2c3",
        "track": "#e5ded0",
    },
    "dark": {
        "background": "#171e19",
        "eyebrow": "#e3a857",
        "heading": "#f0eadf",
        "text": "#c6d1c8",
        "muted": "#8fa095",
        "rule": "#344239",
        "track": "#29342d",
    },
}

MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def github(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{OWNER}-profile-visuals",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def language_mix(languages):
    entries = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    total = sum(size for _, size in entries)
    if total == 0:
        return [{"name": "Sem código detectado", "ratio": 1, "percentage": "100"}]

    visible = entries[:4]
    hidden = sum(size for _, size in entries[4:])
    if hidden:
        visible.append(("Outros", hidden))

    mix = []
    for name, size in visible:
        ratio = size / total
        pct = ratio * 100
        mix.append({
            "name": name,
            "ratio": ratio,
            "percentage": f"{pct:.1f}" if pct < 1 else str(round(pct)),
        })
    return mix


def month_year(iso_date):
    date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return f"{MONTHS[date.month - 1]} {date.year}"


def render(projects, theme_name):
    theme = THEMES[theme_name]
    width, bar_width, row_start, row_height = 900, 804, 132, 104
    height = row_start + len(projects) * row_height + 32
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    rows = []
    for index, project in enumerate(projects):
        y = row_start + index * row_height
        mix = language_mix(project["languages"])
        offset = 48.0
        segments, legend = [], []
        for lang_index, lang in enumerate(mix):
            seg_width = max(2.0, bar_width * lang["ratio"])
            color = LANGUAGE_COLORS.get(lang["name"], "#8b948d")
            delay = index * 90 + lang_index * 55
            segments.append(
                f'<rect class="bar-segment" style="animation-delay:{delay}ms" '
                f'x="{offset:.2f}" y="{y + 47}" width="{seg_width:.2f}" height="10" fill="{color}" />'
            )
            offset += seg_width
            x = 48 + lang_index * 158
            legend.append(
                f'<circle cx="{x + 4}" cy="{y + 76}" r="4" fill="{color}" />'
                f'<text x="{x + 15}" y="{y + 80}" class="legend">{escape(lang["name"])} {lang["percentage"]}%</text>'
            )

        rows.append(f"""<g>
    <text x="48" y="{y}" class="eyebrow">{escape(project["label"])}</text>
    <text x="48" y="{y + 28}" class="project">{escape(project["title"])}</text>
    <text x="360" y="{y + 28}" class="summary">{escape(project["summary"])}</text>
    <text x="852" y="{y + 28}" text-anchor="end" class="updated">atualizado {month_year(project["pushed_at"])}</text>
    <rect x="48" y="{y + 47}" width="{bar_width}" height="10" fill="{theme["track"]}" />
    {"".join(segments)}
    {"".join(legend)}
    <line x1="48" y1="{y + 95}" x2="852" y2="{y + 95}" stroke="{theme["rule"]}" />
  </g>""")

    rows_svg = "\n  ".join(rows)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
  <title id="title">Projetos selecionados, direto do GitHub</title>
  <desc id="description">Composição de linguagens e última atualização pública de projetos selecionados de Murilo Benhossi.</desc>
  <style>
    text {{ font-family: "Segoe UI", "Trebuchet MS", sans-serif; }}
    .kicker {{ fill: {theme["eyebrow"]}; font-size: 12px; font-weight: 700; letter-spacing: 2.4px; }}
    .title {{ fill: {theme["heading"]}; font-size: 28px; font-weight: 650; letter-spacing: -0.4px; }}
    .caption {{ fill: {theme["muted"]}; font-size: 13px; }}
    .eyebrow {{ fill: {theme["eyebrow"]}; font-size: 10px; font-weight: 700; letter-spacing: 1.6px; }}
    .project {{ fill: {theme["heading"]}; font-size: 18px; font-weight: 650; }}
    .summary {{ fill: {theme["text"]}; font-size: 13px; }}
    .updated {{ fill: {theme["muted"]}; font-size: 12px; }}
    .legend {{ fill: {theme["text"]}; font-size: 11px; }}
    .footer {{ fill: {theme["muted"]}; font-size: 10px; letter-spacing: 0.3px; }}
    .bar-segment {{ transform-box: fill-box; transform-origin: left; animation: reveal 650ms cubic-bezier(0.16, 1, 0.3, 1) both; }}
    @keyframes reveal {{ from {{ transform: scaleX(0); opacity: 0.65; }} to {{ transform: scaleX(1); opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .bar-segment {{ animation: none; }} }}
  </style>
  <rect width="{width}" height="{height}" fill="{theme["background"]}" />
  <text x="48" y="38" class="kicker">CÓDIGO PÚBLICO</text>
  <text x="48" y="72" class="title">Projetos selecionados, direto do GitHub</text>
  <text x="48" y="98" class="caption">Metadados dos repositórios e bytes por linguagem · apenas trabalhos públicos</text>
  {rows_svg}
  <text x="852" y="{height - 18}" text-anchor="end" class="footer">GITHUB REST API · GERADO EM {generated}</text>
</svg>"""


def main():
    data = []
    for project in PROJECTS:
        repo = github(f"/repos/{OWNER}/{project['repo']}")
        languages = github(f"/repos/{OWNER}/{project['repo']}/languages")
        data.append({**project, "pushed_at": repo["pushed_at"], "languages": languages})

    out = Path("assets")
    out.mkdir(exist_ok=True)
    for theme_name in THEMES:
        (out / f"featured-work-{theme_name}.svg").write_text(render(data, theme_name), encoding="utf-8")


if __name__ == "__main__":
    main()
