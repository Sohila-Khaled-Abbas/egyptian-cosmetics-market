# Contributing to Egyptian Cosmetics Analytics

Thank you for your interest in contributing to the **Egyptian Cosmetics Analytics** platform! This document outlines the software engineering standards, git conventions, Power Query / M authoring guidelines, and DAX modeling practices expected in this repository.

---

## 1. Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with respect and professionalism.

---

## 2. Git Branching & Workflow

We follow a **Trunk-Based / Feature Branch** workflow:

1. **`main`**: Production-ready, fully validated branch. Direct commits to `main` are restricted.
2. **`feature/<feature-name>`**: For new playbooks, M transformations, or report pages (e.g. `feature/channel-waterfall`).
3. **`fix/<bug-name>`**: For bug fixes, quarantine adjustments, or syntax corrections (e.g. `fix/phone-regex-m`).
4. **`docs/<doc-topic>`**: For documentation updates and translation improvements.

---

## 3. Commit Message Conventions (Conventional Commits)

All commit messages must follow the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short summary in present tense>

[optional body explaining WHY the change was made]

[optional footer with issue reference, e.g. Closes #12]
```

### Allowed Types:
- **`feat`**: New M query, DAX measure, or report visual.
- **`fix`**: Correction to a data cleaning rule, quarantine filter, or calculation bug.
- **`docs`**: Updates to playbooks, architecture diagrams, or README.
- **`perf`**: VertiPaq optimization, table buffering, or cardinality reduction.
- **`test`**: Automated Python or DAX test assertions.
- **`refactor`**: Reorganizing M queries or display folders without altering output.

### Examples:
```bash
feat(m-query): add ref_payment_mapping table for fintech gateways
fix(quarantine): correct date boundary check for leap years
docs(playbook-05): add empirical validation statistics for inventory
perf(orders): buffer cln_products before merging into trf_sales
```

---

## 4. Software Engineering Standards for Power Query (M)

1. **Deterministic Dependency Groups:**
   All queries must be filed into one of the 8 standard groups:
   `00_Parameters & Functions`, `01_Source`, `02_Staging`, `03_Reference`, `04_Cleansed`, `05_Validated`, `06_Transformations`, `07_Model`, `99_Admin`.
2. **Strict Load Discipline:**
   - Intermediate queries (`01_Source`, `02_Staging`, `04_Cleansed`, `06_Transformations`) must have **`Enable Load = False`**.
   - Model entities (`07_Model`) and audit tables (`rejected_*`, `dq_summary`) must have **`Enable Load = True`**.
3. **No Hardcoded Local Paths:**
   Always reference `pRawDataPath`. Never hardcode `C:\Users\...` inside query source steps.
4. **Bilingual Preservation:**
   Never overwrite or drop Arabic attributes (`product_name_ar`, `store_name_ar`). Both Arabic and English versions must be maintained.
5. **Bracket and Token Balance:**
   Run `pytest tests/test_m_code_syntax.py` before submitting PRs to ensure all M expressions are syntactically valid.

---

## 5. Software Engineering Standards for DAX

1. **Centralized in `_Measures` Container:**
   Never place measures scattered across fact or dimension tables. All analytical logic belongs in `_Measures`.
2. **Display Folders:**
   Every measure must be assigned to one of the 7 standard folders (`01 Financial KPIs` through `07 Data Quality & Pipeline Audit`).
3. **Divide-by-Zero Protection:**
   Always use `DIVIDE(Numerator, Denominator, 0)` rather than the raw division operator `/`.
4. **Explicit Measures Over Calculated Columns:**
   Do NOT introduce row-level calculated columns in the model for metrics that can be computed in M or evaluated dynamically in DAX.
5. **Contiguous Date Dimension References:**
   Time intelligence functions must always reference `dim_date[Date]` (the marked Date table), never the transaction timestamp in `fact_sales`.

---

## 6. Pre-Pull Request Checklist

Before submitting a Pull Request:
- [ ] Run automated data integrity tests: `pytest tests/`
- [ ] Verify that all M code files have balanced parentheses, brackets, and braces.
- [ ] Confirm row-count reconciliation matches the ground truth ledger ($502,000$ raw $\rightarrow$ $2,097$ quarantined $\rightarrow$ $499,903$ valid).
- [ ] Ensure markdown documents adhere to GitHub-flavored markdown standards.
- [ ] Link relevant GitHub issues in your PR description using the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md).
