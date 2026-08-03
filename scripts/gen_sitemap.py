#!/usr/bin/env python3
"""
LocalRestoreHub — Direct Sitemap Generator
============================================
Generates public/sitemap.xml — a SINGLE, direct sitemap (no index indirection).
This is the most robust format for Google: one file, all URLs, no sub-sitemaps.

Called automatically by expand_weekly.py after each city batch.
Manual run: python3 scripts/gen_sitemap.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "src", "data", "cities.json")
OUT_PATH = os.path.join(ROOT, "public", "sitemap.xml")

SITE = "https://www.localrestorehub.com"

# Static pages (always present)
STATIC_PAGES = [
    "/",
    "/about/",
    "/contact/",
    "/privacy-policy/",
    "/terms-of-service/",
]


def main():
    with open(DATA_PATH, encoding="utf-8") as f:
        cities = json.load(f)

    urls = list(STATIC_PAGES)
    for c in cities:
        urls.append(f"/{c['slug']}/")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        lines.append(f"  <url><loc>{SITE}{u}</loc></url>")
    lines.append("</urlset>")

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"✅ public/sitemap.xml — {len(urls)} URLs (fichier direct, pas d'index)")


if __name__ == "__main__":
    main()
