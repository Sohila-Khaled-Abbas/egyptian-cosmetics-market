## Pull Request Description

### Summary of Changes
Provide a concise overview of what this pull request changes, adds, or fixes.

### Type of Change
- [ ] `feat`: New Power Query M transformation, DAX measure, or report page
- [ ] `fix`: Bug fix in data cleansing, quarantine routing, or calculation
- [ ] `docs`: Documentation update in `docs/powerbi/`
- [ ] `perf`: VertiPaq performance optimization or table buffering
- [ ] `test`: New automated data integrity test

---

## Architectural & Data Quality Verification

- [ ] **Power Query Grouping:** Changes adhere to the 8 standard query groups (`00_Parameters & Functions` through `99_Admin`).
- [ ] **Load Discipline:** Intermediate staging/cleansed queries have `Enable Load = False`.
- [ ] **Data Quality Assertions:** Automated tests in `tests/` pass (`pytest tests/`).
- [ ] **M Bracket Balance:** Verified matching `()`, `[]`, `{}` in all modified `.m` files.
- [ ] **DAX Hygiene:** Measures reside in `_Measures`, use `DIVIDE()`, and include format strings.
- [ ] **Bilingual Support:** Arabic and English attributes are preserved.

---

## Related Issues
Closes #(issue_number)
