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

    html = ["<!doctype html><meta charset='utf-8'><title>AGCO PTx Demo – Ag Data Sources</title>",
            "<style>body{font-family:system-ui,Arial;padding:2rem;max-width:720px;margin:auto;background:#0f172a;color:#e2e8f0}a{color:#93c5fd}</style>",
            "<h1>AGCO PTx Demo</h1><h2>Public Data Sources</h2><p>Retrieved from RDS DB</p><ul>"]
    for r in rows:
        html.append(f"<li><a href='{r['url']}' target='_blank' rel='noopener'>{r['name']}</a></li>")
    html.append("</ul>")
    html.append("<hr>")
    html.append("<h2>Resources</h2>")
    html.append("<h3>GitHub Repo:</h3><p>Repo and CI/CD Pipeline / Workflow that builds the Python container, pushes to ECR, and deploys via SSM on EC2 by pulling in latest ECR image.</p><p><a href=\"https://github.com/nickeldred/ptx-demo\">https://github.com/nickeldred/ptx-demo</a></p>")
    html.append("<h3>Video Demo:</h3><p><a href=\"https://www.veed.io/view/a009900c-256e-47de-ab58-555c1eeb46d5?panel=share\">https://www.veed.io/view/a009900c-256e-47de-ab58-555c1eeb46d5?panel=share</a></p>)
    html.append("<h2>Setup</h2>")
    html.append("<h3>Networking</h3>")
    html.append("<ul>")
    html.append("<li><strong>DNS:</strong> <code>ptx.nickeldred.com</code> CNAME → ALB DNS name (HTTPS via ACM).</li>")
    html.append("<li><strong>VPC:</strong> 2 public subnets (ALB across 2 AZs) + 1 private subnet (EC2).</li>")
    html.append("<li><strong>ALB:</strong> Listeners on 80/443 → Target Group on port 5000 (health check <code>/health</code>).</li>")
    html.append("<li><strong>Security Groups:</strong> ALB SG allows 80/443 from internet; App SG allows TCP 5000 <em>from ALB SG</em>.</li>")
    html.append("</ul>")
    html.append("<h3>Compute & Data</h3>")
    html.append("<ul>")
    html.append("<li><strong>EC2 (private):</strong> Amazon Linux + Docker. Container listens on 80; host maps <code>5000→80</code>.</li>")
    html.append("<li><strong>RDS MariaDB (private):</strong> App connects via SG; creds are pulled at runtime from AWS Secrets Manager.</li>")
    html.append("</ul>")
    html.append("<h3>CI/CD</h3>")
    html.append("<ul>")
    html.append("<li><strong>GitHub Actions (OIDC):</strong> Build → Test/Scan (pip-audit, Bandit, Hadolint, Trivy) → Push to ECR → Deploy via SSM.</li>")
    html.append("<li><strong>Deploy:</strong> SSM script logs into ECR, pulls the image tag, injects DB env vars from Secrets Manager, and restarts the container.</li>")
    html.append("</ul>")
    html.append("<h3>IAM</h3>")
    html.append("<ul>")
    html.append("<li><strong>EC2 role:</strong> AmazonSSMManagedInstanceCore, ECR read-only, and <code>secretsmanager:GetSecretValue</code> on the DB secret.</li>")
    html.append("<li><strong>GitHub role:</strong> Assumed via OIDC; minimal permissions to ECR and SSM send-command.</li>")
    html.append("</ul>")
    return "\n".join(html)

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
