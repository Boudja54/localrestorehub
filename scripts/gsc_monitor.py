#!/usr/bin/env python3
"""
LocalRestoreHub — ACCÈS GOOGLE SEARCH CONSOLE (stats SEO réelles).
Usage : python3 gsc_monitor.py [--days 30]

Lit le token OAuth partagé des agents (divertylocassistant@gmail.com),
qui est propriétaire de localrestorehub.com dans Search Console.
Token : /root/divertyloc/data/google_token.json (refresh automatique).
"""
import json, urllib.request, urllib.parse, urllib.error, datetime, sys

TOKEN_PATH = "/root/divertyloc/data/google_token.json"
CLIENT_SECRET = "/root/divertyloc/data/client_secret.json"
SITE = "sc-domain:localrestorehub.com"

def get_token():
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    return tok.get("access_token") or tok.get("token"), tok

def refresh_token(tok):
    with open(CLIENT_SECRET) as f:
        cs = json.load(f)
    installed = cs.get("installed", cs.get("web", {}))
    data = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    tok["token"] = d["access_token"]
    with open(TOKEN_PATH, "w") as f:
        json.dump(tok, f, indent=2)
    return d["access_token"]

def api(url, body=None, access=None):
    headers = {"Authorization": f"Bearer {access}"}
    data = None
    if body:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def main():
    days = 30
    if "--days" in sys.argv:
        try:
            days = int(sys.argv[sys.argv.index("--days") + 1])
        except (ValueError, IndexError):
            pass

    access, tok = get_token()
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    enc = urllib.parse.quote(SITE, safe='')
    base = f"https://www.googleapis.com/webmasters/v3/sites/{enc}"

    out = [f"📊 SEARCH CONSOLE — LocalRestoreHub ({start} → {end})"]

    # 1. Totaux
    try:
        d = api(f"{base}/searchAnalytics/query",
                {"startDate": start.isoformat(), "endDate": end.isoformat()}, access)
        rows = d.get("rows", [])
        if rows:
            r = rows[0]
            out.append(f"🖱️ Clics: {r['clicks']} | 👁️ Impressions: {r['impressions']} | CTR {r['ctr']*100:.1f}% | Pos {r['position']:.1f}")
        else:
            out.append("(aucune donnée sur la période)")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            access = refresh_token(tok)
            d = api(f"{base}/searchAnalytics/query",
                    {"startDate": start.isoformat(), "endDate": end.isoformat()}, access)
            rows = d.get("rows", [])
            if rows:
                r = rows[0]
                out.append(f"🖱️ Clics: {r['clicks']} | 👁️ Impressions: {r['impressions']} | CTR {r['ctr']*100:.1f}% | Pos {r['position']:.1f}")
        else:
            out.append(f"❌ Erreur API: {e.code}")

    # 2. Top pages
    try:
        d = api(f"{base}/searchAnalytics/query",
                {"startDate": start.isoformat(), "endDate": end.isoformat(),
                 "dimensions": ["page"], "rowLimit": 8}, access)
        rows = d.get("rows", [])
        if rows:
            out.append("\n📄 Top pages:")
            for r in rows:
                out.append(f"  {r['clicks']}c | {r['impressions']}imp | pos {r['position']:.1f} | {r['keys'][0][:65]}")
    except Exception as e:
        out.append(f"\n📄 Erreur: {str(e)[:80]}")

    # 3. Mots-clés
    try:
        d = api(f"{base}/searchAnalytics/query",
                {"startDate": start.isoformat(), "endDate": end.isoformat(),
                 "dimensions": ["query"], "rowLimit": 8}, access)
        rows = d.get("rows", [])
        if rows:
            out.append("\n🔑 Mots-clés:")
            for r in rows:
                out.append(f"  {r['clicks']}c | {r['impressions']}imp | pos {r['position']:.1f} | \"{r['keys'][0][:55]}\"")
    except Exception as e:
        out.append(f"\n🔑 Erreur: {str(e)[:80]}")

    return "\n".join(out)

if __name__ == "__main__":
    print(main())
