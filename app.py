import os
import pymysql
from flask import Flask, Response

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME", "farm")

def get_conn():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS,
                           database=DB_NAME, cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def index():
    rows = []
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, url FROM datasources ORDER BY name;")
                rows = cur.fetchall()
    except Exception as e:
        return Response(f"DB error: {e}", status=500, mimetype="text/plain")

    html = ["<!doctype html><meta charset='utf-8'><title>AGCO PTx Demo – Data Sources</title>",
            "<style>body{font-family:system-ui,Arial;padding:2rem;max-width:720px;margin:auto;background:#0f172a;color:#e2e8f0}a{color:#93c5fd}</style>",
            "<h1>Public Data Sources</h1><ul>"]
    for r in rows:
        html.append(f"<li><a href='{r['url']}' target='_blank' rel='noopener'>{r['name']}</a></li>")
    html.append("</ul>")
    return "\n".join(html)

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
