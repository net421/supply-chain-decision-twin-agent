# Validation Report

Initial validation targets:

- Stockout risk is between 0 and 1.
- Service level is between 0 and 1.
- High stockout risk requires human review.
- Decision memory includes claim boundaries.

Run:

```bash
pytest
python src/validate_outputs.py
```
