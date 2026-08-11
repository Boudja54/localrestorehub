#!/usr/bin/env python3
"""
LocalRestoreHub — Daily Site Monitor (watchdog)
================================================
Checks the live site every day and prints NOTHING when everything is OK
(silent watchdog pattern — no spam), or a clear alert listing every issue.

Checks:
  1. Homepage HTTP 200
  2. A sample of city pages HTTP 200 (first N from sitemap)
  3. Tracking number tel:+18448331048 present
  4. ZERO "mold/moisissure" on every checked page
  5. Marketcall disclaimer present
  6. 301 redirects (pages.dev + apex → www)
  7. Sitemap reachable and lists all expected pages

Exit code 0 = OK, 1 = issues found.
"""

import json
import re
import ssl
import sys
import urllib.error
import urllib.request

BASE = "https://www.localrestorehub.com"
PHONE_TEL = "tel:+18448331048"
DISCLAIMER_MARKER = "All persons depicted in a photo or video are actors or models"
FORBIDDEN = ["mold", "moisissure"]

UA = {"User-Agent": "Mozilla/5.0 (compatible; LRH-Monitor/1.0)"}
CTX = ssl.create_default_context()


def http_status(url, allow_redirect=True, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    if allow_redirect:
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return r.status, r.geturl()
        except urllib.error.HTTPError as e:
            return e.code, url
        except Exception as e:
            return -1, str(e)
    else:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None
        https_handler = urllib.request.HTTPSHandler(context=CTX)
        opener = urllib.request.build_opener(NoRedirect, https_handler)
        try:
            with opener.open(req, timeout=timeout) as r:
                return r.status, r.headers.get("Location", "")
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Location", "")
        except Exception as e:
            return -1, str(e)


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read().decode("utf-8", errors="ignore")


def main():
    issues = []

    # 1. Homepage
    try:
        status, _ = http_status(BASE + "/")
        if status != 200:
            issues.append(f"Homepage HTTP {status} (attendu 200)")
    except Exception as e:
        issues.append(f"Homepage erreur: {e}")

    # 6. Redirects
    for url, label in [("https://localrestorehub.pages.dev/", "pages.dev"),
                       ("https://localrestorehub.com/", "apex")]:
        code, loc = http_status(url, allow_redirect=False)
        if code != 301 or "www.localrestorehub.com" not in loc:
            issues.append(f"Redirect {label}: HTTP {code} → {loc} (attendu 301 → www)")

    # 7. Sitemap (direct single file since Aug 2026 — no more sitemap-0.xml)
    try:
        sm = fetch(BASE + "/sitemap.xml")
        urls = re.findall(r"<loc>(.*?)</loc>", sm)
        if len(urls) < 5:
            issues.append(f"Sitemap: seulement {len(urls)} URLs")
    except Exception as e:
        issues.append(f"Sitemap erreur: {e}")
        urls = []

    # 2+3+4+5. Sample city pages (first 10 from sitemap) + homepage content
    pages_to_check = [BASE + "/"]
    for u in urls:
        if "water-damage-repair-" in u:
            pages_to_check.append(u)
        if len(pages_to_check) >= 11:
            break

    checked = 0
    for page in pages_to_check:
        try:
            html = fetch(page)
            checked += 1
            low = html.lower()
            if PHONE_TEL not in html:
                issues.append(f"Page {page}: numéro tel: manquant")
            for term in FORBIDDEN:
                if term in low:
                    issues.append(f"Page {page}: terme interdit '{term}' trouvé")
            if DISCLAIMER_MARKER not in html:
                issues.append(f"Page {page}: disclaimer Marketcall manquant")
        except Exception as e:
            issues.append(f"Page {page} erreur: {e}")

    # ---- Output ----
    if issues:
        print("🚨 ALERTE LocalRestoreHub — problèmes détectés :")
        for i in issues:
            print(f"  • {i}")
        print(f"\nPages vérifiées: {checked} | Sitemap URLs: {len(urls)}")
        sys.exit(1)
    else:
        # SILENT when OK (watchdog pattern) — no notification spam.
        # For a manual check anytime: python3 scripts/monitor_site.py
        sys.exit(0)


if __name__ == "__main__":
    main()
