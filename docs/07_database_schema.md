# Database Schema Reference

## Core Tables

### mutual_funds
- id (PK)
- scheme_code (unique)
- fund_name
- category
- sub_category
- benchmark
- aum
- ter
- launch_date

### fund_managers
- id (PK)
- name
- experience_years

### fund_manager_mapping
- fund_id (FK)
- manager_id (FK)

### nav_data
- fund_id (FK)
- nav_date
- nav_value

### benchmark_nav
- benchmark_name
- nav_date
- nav_value

---

## Indexing Strategy
- Composite index on (fund_id, nav_date)