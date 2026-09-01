# IAM Security Audit & Access Governance

A hands-on simulation of an IAM security audit for a small AWS environment — building role-based access from scratch, identifying real misconfigurations, and remediating them like a Cloud Security / SOC Analyst would.

> 📄 **Full audit report:** [AUDIT_REPORT.md](./AUDIT_REPORT.md)

---

## What This Project Covers

- Designed a **role-based IAM structure** (4 groups, 5 users) following least-privilege principles
- Identified and **remediated a real misconfiguration** — a user with direct-attached admin permissions bypassing the group model
- Authored a **custom, condition-based IAM policy** restricting EC2 actions to tagged resources only
- Implemented **MFA enforcement** via a deny-unless-MFA policy applied account-wide
- Ran **AWS IAM Access Analyzer** and investigated a real public S3 bucket finding — made and documented a risk-based decision rather than blanket remediation

---

## Architecture

| Group | Access Level | Members |
|---|---|---|
| `Admins` | Full administrative access | 1 |
| `Developers` | Scoped EC2 + S3 access (tag-restricted) | 2 |
| `Auditors` | Read-only (IAM) | 1 |
| `Finance` | Read-only (billing) | 1 |

All access is granted through **groups, not individual users** — no direct policy attachments — for full auditability.

---

## Key Findings Summary

| # | Finding | Status |
|---|---|---|
| 1 | User had directly-attached admin policy, bypassing group model | ✅ Remediated |
| 2 | MFA not enforced by default | ✅ Remediated (policy-enforced) |
| 3 | S3 bucket publicly accessible | ✅ Reviewed — confirmed intentional (live demo site), read-only scope verified |

Full details, JSON policies, and rationale for every decision are in the [audit report](./AUDIT_REPORT.md).

---

## Custom Policies Written

- [`DevTeamScopedEC2Access.json`](./policies/DevTeamScopedEC2Access.json) — restricts developers to Start/Stop/Reboot on `Environment=Dev` tagged EC2 instances only; explicitly denies termination
- [`EnforceMFAPolicy.json`](./policies/EnforceMFAPolicy.json) — denies all actions account-wide unless the session is MFA-authenticated

---

## Tools Used

AWS IAM · AWS IAM Access Analyzer · AWS S3

---

## Screenshots

*(See `/screenshots` folder — IAM users & groups, MFA setup, Access Analyzer findings, policy configuration)*

---

## Why This Project

IAM misconfiguration is one of the most common real-world causes of cloud security incidents. This project was built to practice the full loop of a real access review: **design access → find gaps → investigate before fixing → remediate or justify → document.**
