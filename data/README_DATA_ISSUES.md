# Intentional Data Quality Problems

This dataset is intentionally imperfect. Do not clean these problems manually
before building the ETL project. They are included as test cases.

## Customer Master
- Exact duplicate customer rows
- Near-duplicate phone formatting
- Upper/lower-case email inconsistency
- Missing phone, email and area
- Governorate casing inconsistency

## Product / Reference Data
- Bilingual Arabic/English naming
- Currency values such as `EGP`, `EGP ` and `جنيه`
- Local/imported product mix
- Cosmetics categories: skincare, makeup, haircare, fragrance, body care

## Orders
- Duplicate order IDs
- Missing/invalid foreign keys
- Quantity = 0
- Negative quantity
- Negative price
- Future-dated transactions
- 1900-01-01 date anomaly
- Status values such as `Completed`, `completed`, `Complete`
- Currency inconsistency
- Mixed Arabic/English channel and payment labels

## Inventory
- Negative closing stock
- Negative damaged quantity
- Implausibly high sold quantity

## Targets
- Missing monthly store targets
- Duplicate target records

## Suggested Data Quality Checks
1. Primary-key uniqueness
2. Foreign-key integrity
3. NOT NULL constraints
4. Accepted-value constraints
5. Positive quantity and price
6. Date validity / freshness
7. Duplicate detection
8. Standardization of bilingual labels
9. Inventory reconciliation
10. Source-to-target row-count reconciliation

The goal is to build a repeatable pipeline that detects, logs and handles these
issues instead of silently fixing them.
