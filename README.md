<<<<<<< HEAD
# Event Registration & Ticketing System

A serverless REST API on AWS that replaces Microsoft Forms + Excel for event
registration, built for the Azubi Africa Cloud Computing & AI program.

## Architecture

- **API Gateway** — REST endpoints
- **AWS Lambda** — business logic (Python)
- **DynamoDB** — single-table storage for events & registrations
- **CloudWatch** — logs & alarms
- **SNS** *(optional)* — registration confirmation emails
- **AWS Budgets** — cost tracking on the Free Tier
- **GitHub Actions** — CI/CD pipeline

## Repo structure

```
event-registration-system/
├── infra/
│   ├── iam/                     # IAM trust & permissions policies
│   └── template.yaml            # SAM/CloudFormation template (added in a later step)
├── src/
│   └── handlers/                # Lambda function code
├── tests/                       # Unit tests
├── .github/workflows/           # CI/CD pipeline definitions
└── README.md
```

## Setup checklist (Step 1: Foundations)

- [ ] Create an IAM user for programmatic/console access (not root)
- [ ] Create the Lambda execution role using the policies in `infra/iam/`
- [ ] Replace `REGION` and `ACCOUNT_ID` placeholders in the IAM policy JSON
- [ ] Create this GitHub repo and push this scaffold
- [ ] Set an AWS Budget alert (recommended before provisioning anything else)

See the step-by-step console instructions provided alongside this scaffold.
=======
# event-registration-ticketing-system
This project is to create an event registration ticketing system using lamda, dynamoDb, cloudfomation. A classic serverless CRUD API with the "AWS free tier trifecta" (Lambda + API Gateway + DynamoDB) plus observability, notifications, cost control, and CI/CD.
>>>>>>> f741b5d9988a0c4793a824290eb6e8d48d749728
