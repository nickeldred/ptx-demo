# Setup

## Networking
- **DNS:** `ptx.nickeldred.com` → CNAME to ALB DNS name (HTTPS via ACM).  
- **VPC:** 2 public subnets (ALB across 2 AZs) + 1 private subnet (EC2).  
- **ALB:** Listeners on 80/443 → Target Group on port 5000 (health check `/health`).  
- **Security Groups:**  
  - ALB SG allows 80/443 from internet.  
  - App SG allows TCP 5000 from ALB SG.  

## Compute & Data
- **EC2 (private):** Amazon Linux + Docker. Container listens on 80; host maps `5000→80`.  
- **RDS MariaDB (private):** App connects via SG; creds are pulled at runtime from AWS Secrets Manager.  

## CI/CD
- **GitHub Actions (OIDC):**  
  Build → Test/Scan (`pip-audit`, `Bandit`, `Hadolint`, `Trivy`) → Push to ECR → Deploy via SSM.  
- **Deploy:**  
  SSM script logs into ECR, pulls the image tag, injects DB env vars from Secrets Manager, and restarts the container.  

## IAM
- **EC2 role:** `AmazonSSMManagedInstanceCore`, `AmazonEC2ContainerRegistryReadOnly`, and `secretsmanager:GetSecretValue` on the DB secret.  
- **GitHub role:** Assumed via OIDC; minimal permissions to ECR and SSM `send-command`.  
