# Validation Lifecycle

## Validation Objective

Verify that KPIs, recommendations, and memory records remain internally consistent.

## Inputs

- SQL operational tables
- SQL memory tables
- KPI dictionary
- semantic contract
- scenario assumptions

## Methods

- SQL validation queries
- Python unit tests
- recommendation rule checks
- memory completeness checks

## Acceptance Criteria

- Stockout risk is between 0 and 1.
- Service level is between 0 and 1.
- High stockout risk requires human review.
- Recommendations reference governed KPIs.
- Memory records include claim boundaries.
