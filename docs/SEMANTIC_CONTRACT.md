# Semantic Contract

## Allowed Questions

- Which products are at stockout risk?
- Which locations require replenishment review?
- Which recommendations require human approval?
- Which KPIs support a recommendation?
- What decisions were previously recorded in SQL memory?

## Rejected Questions

- Execute a purchase order.
- Guarantee business impact.
- Use real supplier data.
- Make autonomous operational decisions.
- Claim production deployment.

## Tool Rules

- SQL may be used only to query synthetic supply chain data and memory records.
- Recommendations must reference governed KPIs.
- High-risk recommendations must require human review.
- Answers must include a claim boundary.
