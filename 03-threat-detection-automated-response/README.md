# 🔍 Threat Detection & Automated Response — AWS

![Project Overview](screenshots/00-project-overview-illustration.png)

## Overview

This project implements an automated threat detection and response pipeline on AWS. Rather than just enabling monitoring services, this builds a full detect → respond → alert cycle: when GuardDuty flags suspicious activity, the system automatically investigates the affected IAM identity, revokes its access, and notifies the security team in real time — with no manual intervention required.

## Architecture

![Architecture Diagram](screenshots/02-architecture-diagram.png)

**Flow:** CloudTrail logs all account activity → GuardDuty analyzes it for anomalies → EventBridge routes any finding to a Lambda function → Lambda deactivates the associated IAM user's access keys and publishes an alert via SNS.

## What it does

1. **CloudTrail** — continuously logs all API activity in the account (management events).
2. **GuardDuty** — analyzes CloudTrail, VPC Flow Logs, and DNS logs to detect anomalous or unauthorized behavior.
3. **EventBridge** — listens for GuardDuty findings and triggers a Lambda function in response.
4. **Lambda (auto-response)** — parses the finding, identifies the IAM user involved (if any), and deactivates their access keys to contain the threat.
5. **SNS** — sends a real-time email alert summarizing the finding and the action taken.
6. **Security Hub** — aggregates findings from GuardDuty into a single dashboard for centralized visibility.

## Simulated incident example

> A GuardDuty finding was generated to simulate unauthorized API activity. EventBridge routed the finding to the response Lambda within seconds. The Lambda function identified the associated IAM user, deactivated their access keys, and published an alert via SNS — confirmed by email delivery within seconds of the finding being generated.

## Proof of deployment

![GuardDuty Findings](screenshots/01-guardduty-findings-summary.png)

## Security notes

- The Lambda execution role in this demo uses `IAMFullAccess` and `AmazonSNSFullAccess` for simplicity. **In a production environment, this would be replaced with a scoped-down custom policy** granting only `iam:UpdateAccessKey` and `iam:ListAccessKeys` on specific resources, and `sns:Publish` on the specific topic — following the principle of least privilege.
- All services (GuardDuty, Security Hub) were run within their 30-day free trial window and disabled afterward to avoid ongoing charges.
- Testing was done using GuardDuty's built-in sample findings feature rather than live attack simulation, to keep the environment safe and cost-free.

## Tech stack

`AWS CloudTrail` · `AWS GuardDuty` · `Amazon EventBridge` · `AWS Lambda (Python)` · `AWS IAM` · `Amazon SNS` · `AWS Security Hub`
