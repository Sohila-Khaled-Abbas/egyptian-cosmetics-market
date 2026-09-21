---
name: Data Quality Anomaly Report
about: Report an unhandled anomaly, new alias, or referential integrity breach in source data
title: '[DQ ANOMALY] '
labels: 'data-quality'
assignees: ''
---

### Source Entity
- [ ] `orders.csv`
- [ ] `customers.csv`
- [ ] `products.csv`
- [ ] `stores.csv`
- [ ] `inventory_monthly.csv`
- [ ] `commercial_reference_data.xlsx`
- [ ] `exchange_rates.json`

### Anomaly Description
Describe the data anomaly (e.g. unmapped currency notation, unexpected customer phone format, broken foreign key, negative inventory quantity).

### Sample Corrupt Records
Provide sample values or rows demonstrating the problem:
```
order_id: ORD2025...
corrupt_field: "..."
```

### Proposed Remediation
Should this issue be:
- [ ] Cleaned deterministically in `04_Cleansed`
- [ ] Routed to Quarantine in `05_Validated` (`rejected_*`)
- [ ] Added to Reference Mapping (`03_Reference`)
