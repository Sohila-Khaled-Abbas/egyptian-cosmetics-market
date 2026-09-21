# Security & Data Privacy Policy

## 1. Synthetic Data & PII Disclaimer

**This repository contains 100% synthetic, randomly generated mock data.**
- All customer names, Egyptian mobile numbers (`010...`), email addresses, and physical addresses were generated programmatically using `generate_egyptian_cosmetics_data.py`.
- **No real personally identifiable information (PII)** or commercial operational data from any actual Egyptian company is present in this project.
- Any resemblance to real persons, telephone numbers, or commercial entities is purely coincidental.

---

## 2. Reporting a Vulnerability

If you discover a potential security flaw, credential leak, or unintended sensitive artifact in this repository, please do **NOT** file a public GitHub issue.

Instead, please send an email to the repository maintainer with:
1. Description of the vulnerability or affected file.
2. Steps to reproduce or locate the artifact.
3. Potential impact assessment.

Maintainers will acknowledge receipt within 48 hours and provide a remediation timeline.

---

## 3. Data Governance Best Practices

When deploying this project within your corporate environment:
- Ensure database connection strings and storage access keys are managed via Azure Key Vault or Power BI Service OAuth Credentials, never committed to git.
- Ensure row-level security (RLS) is applied if customer contact fields are exposed to external report readers.
