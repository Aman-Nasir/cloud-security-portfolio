# 04: Terraform IaC Security Pipeline

Infrastructure-as-Code recreation of my [Secure VPC project](../01-secure-vpc) using **Terraform**, with a **GitHub Actions CI/CD pipeline** that runs a **Dockerized security scanner (tfsec + Checkov)** on every push.

**Zero AWS cost by design:** the pipeline only runs `fmt`, `validate` and static security scans. `terraform apply` is never run and no AWS resources are created.

## Tech
Terraform, GitHub Actions (CI/CD), Docker, tfsec, Checkov, AWS (VPC, KMS, CloudWatch Logs, IAM)

## What the Terraform code defines
- VPC with public and private subnets, Internet Gateway and route tables
- Security groups (HTTPS only into the web tier, app port only from the web SG) and NACLs
- VPC Flow Logs to a KMS-encrypted CloudWatch log group, with a least-privilege IAM role

## Pipeline flow
`git push` → GitHub Actions → `terraform fmt / init / validate` → build scanner Docker image → run tfsec + Checkov inside the container

## Security findings and what I did about them

The first scan found 7 issues (3 from tfsec, 4 from Checkov).

| Scanner | Finding | Severity | Action |
|---|---|---|---|
| Checkov | Public NACL rule 1024-65535 also covered port 3389 (RDP) | Fail | **Fixed**: split into 1024-3388 and 3390-65535 |
| tfsec / Checkov | Flow log group not encrypted with a CMK | Low | **Fixed**: added KMS key with rotation |
| tfsec | Security group allows `0.0.0.0/0` on port 443 | Critical | **Accepted**: public HTTPS is the purpose of a web tier; only 443 is open, no SSH/RDP |
| tfsec | IAM policy uses `:*` wildcard | High | **Accepted**: standard pattern for flow log streams, resource limited to one log group |
| Checkov | Security groups not attached to a resource (x2) | Fail | **Accepted**: no workloads in this project, SGs are for future servers |

Accepted risks are suppressed inline in `main.tf` with a written reason.

**After fixes:** tfsec reports no problems; Checkov reports 52 passed, 0 failed, 2 skipped (documented).
Raw output: [`scan-before.txt`](scan-before.txt) (tfsec only) and [`scan-after.txt`](scan-after.txt).

## Run it locally
```bash
terraform init -backend=false
terraform validate
docker build -t tf-security-scanner .
docker run --rm tf-security-scanner
```

## What I learned
- Shift-left security: catching misconfigurations in code before anything is deployed
- Writing a CI/CD pipeline with GitHub Actions
- Running security tools in a Docker container for a consistent environment
- Deciding between fixing a finding and documenting an accepted risk

## Next improvements
- Make the pipeline fail on any tfsec finding, not only Checkov
- Add `terraform plan` against a real account and remote state
- Attach an EC2 workload so the security groups are in use