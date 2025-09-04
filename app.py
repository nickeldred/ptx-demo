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
    html.append("<h2>Resources & Setup</h2>")
    html.append("<h3>GitHub Repo:</h3><p>Repo and CI/CD Pipeline / Workflow that builds the Python container, tests, scans, pushes to ECR and deploys via SSM on EC2 by pulling in latest ECR image.</p><p><a href=\"https://github.com/nickeldred/ptx-demo\">https://github.com/nickeldred/ptx-demo</a></p>")
    html.append("<h3>Networking:</h3><p>ptx CNAME record points to Application LB's FQDN (farm-ec2-alb-2137222498.us-east-1.elb.amazonaws.com)</p><p>ALB listening on port 80 & 443 in public subnet with ACM issued for 443.  Listeners target port 5000 in private subnet.</p>")
    html.append("<h3>Infastructure:</h3><p>VPC with public subnet for Application LB and private subnet for EC2 Instance and corresponding security groups.</p><p>EC2 instance has Docker runtime installed with container running with port 5000->80, and connected to a RDS database</p>")
    html.append("<h3>Security and Monitoring:</h3><p>CloudWatch alarms set up for EC2 and RDS DB</p>")
    html.append("<h3>IaC:</h3><p>Terraform Repo</p>")
    return "\n".join(html)

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
