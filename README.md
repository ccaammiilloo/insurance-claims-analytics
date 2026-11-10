# Insurance Claims & Business Performance Analytics

A reproducible **Data Analytics portfolio project** that uses **synthetic insurance policy records** to explore premiums, submitted claims, approval rates, paid claims and regional trends.

**Tech stack:** Python · SQL / SQLite · Pandas · NumPy · Plotly · pytest.

> All records are synthetic. This is an independent portfolio demonstration, not a real insurer's production system or evidence of real business impact.

## Business questions

- What is the premium volume by product and region?
- How many submitted claims are approved?
- How does the illustrative paid-claims-to-premiums ratio vary across segments?

## How to run

```bash
python -m pip install -r requirements.txt
python pipeline.py
python -m pytest -q
```

The pipeline generates 1,200 synthetic policies, validates integrity, creates a SQLite database, calculates KPIs and saves an interactive HTML dashboard. Open `output/insurance_dashboard.html` in a browser (internet needed to load Plotly from a CDN).

## Project structure

- `pipeline.py`: deterministic data generation, validation, SQL export and dashboard generation
- `sql/business_queries.sql`: example SQL for portfolio KPIs and segmentation
- `tests/test_pipeline.py`: reproducibility and quality tests
- `output/insurance_dashboard.html`: generated, browsable dashboard
- `output/policies.csv`: synthetic dataset
- `output/metrics.json`: calculated KPIs

## Metric definitions

- Approval rate = approved claims / claims submitted; no-claim policies excluded.
- Paid claims = sum of `claim_amount` for approved claims only.
- Illustrative loss ratio = approved claim amounts / all premiums; not an actuarial/statutory loss ratio.

Results describe synthetic generated data only and must not be represented as actual insurance industry findings.
