"""Export a small, additive reporting cube without publishing customer-level data."""
from pathlib import Path
import json
import duckdb

ROOT = Path(__file__).resolve().parents[1]
con = duckdb.connect(str(ROOT/'data/processed/analysis.duckdb'), read_only=True)
cube = con.sql((ROOT/'sql/04_excel_cube.sql').read_text()).df()
assert cube.customers.sum() == 64000
assert cube.purchasers.sum() == 578
assert abs(cube.total_revenue.sum() - 67258.13) < 1e-7
cube.to_csv(ROOT/'data/processed/excel_cube.csv', index=False)
(ROOT/'data/processed/excel_cube.json').write_text(cube.to_json(orient='records', indent=2))
con.sql((ROOT/'sql/05_exploratory_channel_comparison.sql').read_text()).df().to_csv(
    ROOT/'data/processed/channel_comparison.csv', index=False)
print(f'Exported {len(cube)} disjoint source cells; counts and revenue reconcile.')
