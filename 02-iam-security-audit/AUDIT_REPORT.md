# IAM Security Audit & Access Governance — Audit Report

**Environment:** AWS Account (simulated small-team environment — "CloudNova Solutions")
**Region:** Asia Pacific (Sydney) — ap-southeast-2
**Auditor:** Aman Nasir
**Audit type:** Internal IAM access review, self-initiated
**Scope:** IAM users, groups, policies, MFA configuration, and public resource exposure (via AWS IAM Access Analyzer)

---

## Executive Summary

An internal IAM access audit was conducted across a 5-user AWS environment to evaluate adherence to least-privilege access principles, multi-factor authentication (MFA) enforcement, and public resource exposure. The audit identified **2 findings**, both of which were reviewed, and **1 was remediated**. A least-privilege, group-based access model was implemented across all accounts, and a custom, condition-scoped IAM policy was written to further restrict developer access to tagged resources only.

| Metric | Result |
|---|---|
| IAM users reviewed | 5 |
| IAM groups reviewed | 4 |
| Users with excessive/misconfigured permissions found | 1 (`admin-aman`) |
| Users corrected | 1 |
| MFA enforcement policy applied to | 4/4 groups (100%) |
| MFA device actively configured | 1/5 users (demonstration account) |
| Custom least-privilege policies authored | 2 |
| Access Analyzer findings | 1 |
| Findings remediated | 0 remediated / 1 reviewed & accepted with justification |

---

## 1. Access Structure Review

A role-based access model was implemented using four IAM groups, replacing any direct-to-user policy attachment:

| Group | Purpose | Members |
|---|---|---|
| `Admins` | Full administrative access | `admin-aman` |
| `Developers` | Scoped EC2/S3 access for application development | `dev-hassam`, `dev-hassan` |
| `Auditors` | Read-only visibility for security/compliance review | `audit-eman` |
| `Finance` | Read-only billing and cost visibility | `finance-ayesha` |

**Finding 1 — Direct policy attachment (Remediated):**
During initial setup, the `admin-aman` user was found to have `AdministratorAccess` and `IAMUserChangePassword` attached **directly** to the user rather than inherited through the `Admins` group. This is a common misconfiguration that reduces auditability, since access reviews conducted at the group level would not surface this permission.

*Remediation:* The directly-attached policies were removed, `AdministratorAccess` was attached to the `Admins` group instead, and `admin-aman` was added as a group member. Access is now fully traceable through group membership, consistent with the rest of the environment.

**Additional control — Root account restriction:**
The AWS root account was used only for the initial creation of the first administrative IAM user. All subsequent administrative actions were performed using the dedicated `admin-aman` IAM identity, in line with AWS root-account best practices (root should not be used for routine operations).

---

## 2. Least-Privilege Policy Assignment

Each group was scoped to the minimum permissions required for its function, rather than being granted broad or administrative access:

| Group | Policies Applied | Rationale |
|---|---|---|
| `Admins` | `AdministratorAccess` | Full control required for account administration; access restricted to a single named identity, not shared |
| `Developers` | `AmazonEC2FullAccess`, `AmazonS3FullAccess`, custom `DevTeamScopedEC2Access` | Broad managed policies were supplemented with a custom condition-based policy (see Section 3) to tighten actual usable scope |
| `Auditors` | `IAMReadOnlyAccess` | Read-only visibility into IAM configuration for review purposes, no write access |
| `Finance` | `AWSBillingReadOnlyAccess` | Read-only cost/billing visibility; the broader `Billing` managed policy (which includes budget-editing permissions) was deliberately avoided to preserve least-privilege |

---

## 3. Custom Least-Privilege Policy — `DevTeamScopedEC2Access`

To demonstrate hands-on policy authorship (rather than relying solely on AWS-managed policies), a custom JSON policy was written and attached to the `Developers` group:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowEC2ActionsOnDevTaggedInstancesOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:RebootInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeInstanceStatus"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:ResourceTag/Environment": "Dev"
        }
      }
    },
    {
      "Sid": "DenyTerminateAlways",
      "Effect": "Deny",
      "Action": "ec2:TerminateInstances",
      "Resource": "*"
    }
  ]
}
```

**Design rationale:**
- Developers can only Start, Stop, or Reboot EC2 instances explicitly tagged `Environment=Dev`, preventing accidental interaction with production or other-environment resources.
- Instance **termination is explicitly denied for all resources, regardless of tag** — an intentional safety guard against accidental or malicious deletion, a common cause of real-world outages.

---

## 4. Multi-Factor Authentication (MFA)

**Finding 2 — MFA not enforced by default (Remediated via policy control):**
By default, IAM users with console access can sign in using only a password, with no secondary verification factor. This represents a significant risk, as compromised credentials alone would be sufficient for account access.

*Remediation:* A custom policy, `EnforceMFAPolicy`, was authored and attached to all four IAM groups. The policy denies all actions except MFA self-service actions (device registration, session token retrieval) unless the session is authenticated with MFA (`aws:MultiFactorAuthPresent = true`).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowViewAccountInfo",
      "Effect": "Allow",
      "Action": ["iam:GetAccountPasswordPolicy", "iam:ListVirtualMFADevices"],
      "Resource": "*"
    },
    {
      "Sid": "AllowManageOwnMFA",
      "Effect": "Allow",
      "Action": [
        "iam:CreateVirtualMFADevice", "iam:EnableMFADevice", "iam:ListMFADevices",
        "iam:ResyncMFADevice", "iam:DeactivateMFADevice", "iam:DeleteVirtualMFADevice"
      ],
      "Resource": [
        "arn:aws:iam::*:mfa/${aws:username}",
        "arn:aws:iam::*:user/${aws:username}"
      ]
    },
    {
      "Sid": "DenyAllExceptListedIfNoMFA",
      "Effect": "Deny",
      "NotAction": [
        "iam:CreateVirtualMFADevice", "iam:EnableMFADevice", "iam:GetUser",
        "iam:ListMFADevices", "iam:ListVirtualMFADevices", "iam:ResyncMFADevice",
        "sts:GetSessionToken"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": { "aws:MultiFactorAuthPresent": "false" }
      }
    }
  ]
}
```

**Status:** MFA enforcement is active at the policy level for all 5 users. A virtual MFA device (authenticator app) was fully configured and verified on the `admin-aman` account as a proof-of-concept. Remaining accounts have not yet had a physical MFA device registered — under the current policy, these accounts are technically restricted from performing most actions until MFA is configured, which itself validates that the enforcement mechanism is working as intended.

---

## 5. AWS IAM Access Analyzer — External Access Review

An external access analyzer (`CloudNova-Security-Audit-Analyzer`) was created to scan the account for resources unintentionally exposed outside the account boundary.

**Finding 3 — Public S3 bucket exposure (Reviewed & Accepted):**

| Field | Detail |
|---|---|
| Resource | S3 bucket `aman-s3-static-website-001` |
| Access type | Public access (all principals) |
| Finding ID | `65f83f46-5303-4191-bb10-cde8e90842e3` |

*Investigation:* Rather than remediating this finding by default, the bucket contents and configuration were reviewed before taking action. The bucket was found to host a live static website (`index.html`) that is actively referenced as a public demo link in a separate GitHub portfolio project. Removing public access would have broken an intentional, in-use deployment.

The bucket policy was reviewed and confirmed to grant only the `s3:GetObject` (read) action to the public principal — no write or delete permissions are exposed:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::aman-s3-static-website-001/*"
    }
  ]
}
```

*Decision:* Accepted as an intentional, minimal-scope exception rather than remediated. This reflects a risk-based approach to access review — not every public-access finding indicates a misconfiguration, and blanket remediation without investigation can break legitimate functionality. The finding is documented here for audit-trail purposes and should be re-reviewed if the associated demo project is retired.

---

## 6. Summary of Findings & Actions

| # | Finding | Severity | Status | Action Taken |
|---|---|---|---|---|
| 1 | `admin-aman` had directly-attached policies bypassing group-based access model | Medium | ✅ Remediated | Migrated to group-based access; direct attachments removed |
| 2 | MFA not enforced by default on any account | High | ✅ Remediated (policy-level) | `EnforceMFAPolicy` deny-condition policy applied to all 4 groups |
| 3 | S3 bucket `aman-s3-static-website-001` publicly accessible | Low (reviewed) | ✅ Accepted with justification | Confirmed intentional, read-only scope verified, no action needed |

---

## 7. Recommendations for Future Review

- Complete MFA device registration for the remaining 4 IAM users.
- Revisit attaching the `SecurityAudit` managed policy to the `Auditors` group for broader read-only visibility into CloudTrail/Config.
- Periodically re-run Access Analyzer to catch new external-access findings as the environment evolves.
- Consider enabling AWS CloudTrail for ongoing logging of IAM and console activity (see Stage 4 of this portfolio).
- Re-review the public S3 bucket exception if the associated demo project is ever deprecated.

---

*This audit was conducted as part of a self-directed cloud security portfolio project, simulating governance and access-review practices used in real-world SOC/Cloud Security Analyst roles.*
