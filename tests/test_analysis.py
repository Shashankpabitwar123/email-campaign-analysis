"""Behavior and reconciliation tests, independent of dashboard presentation."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import pytest
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from analyze import contrast, bootstrap_means, budget

def test_identical_groups_have_no_effect():
    a=np.array([0]*90+[1]*10)
    r=contrast(a,a)
    assert r['difference']==0
    assert r['ci_low']<0<r['ci_high']
    assert r['p_value']==1

def test_contrast_reverses_direction_and_preserves_test():
    a=np.array([0]*80+[1]*20); b=np.array([0]*95+[1]*5)
    r,s=contrast(a,b),contrast(b,a)
    assert r['difference']==pytest.approx(-s['difference'])
    assert r['ci_low']==pytest.approx(-s['ci_high'])
    assert r['p_value']==pytest.approx(s['p_value'])
    wide=contrast(a,b,alpha=.025)
    assert wide['ci_low']<r['ci_low'] and wide['ci_high']>r['ci_high']

def test_zero_control_rate_does_not_invent_relative_uplift():
    r=contrast(np.array([0,0,1]),np.zeros(3))
    assert r['relative_lift'] is None
    assert np.isfinite(r['ci_low'])

def test_bootstrap_keeps_zero_spending_and_is_reproducible():
    values=np.array([0,0,0,100])
    a=bootstrap_means(values,10000,np.random.default_rng(1))
    b=bootstrap_means(values,10000,np.random.default_rng(1))
    assert np.array_equal(a,b)
    assert a.min()==0 and a.max()==100
    assert a.mean()==pytest.approx(25,abs=1)
    assert a.var()==pytest.approx(values.var()/len(values),rel=.05)

@pytest.mark.parametrize('contacts,margin,cost,fixed,expected',[
    (10000,.5,.05,500,3000), (0,.5,.05,500,-500),
    (10000,0,.05,500,-1000), (10000,1,0,0,8000)])
def test_budget_boundaries(contacts,margin,cost,fixed,expected):
    assert budget(contacts,.8,margin,cost,fixed)==pytest.approx(expected)

@pytest.mark.parametrize('args',[(-1,.8,.5,0,0),(1,.8,1.1,0,0),(1,.8,-.1,0,0),(1,.8,.5,-1,0),(1,.8,.5,0,-1)])
def test_budget_rejects_invalid_inputs(args):
    with pytest.raises(ValueError): budget(*args)

def test_all_reported_quality_checks_pass():
    checks=json.loads((ROOT/'data/processed/quality_checks.json').read_text())
    assert len(checks)==27
    assert all(c['passed'] for c in checks)

def test_aggregate_results_against_independent_counts():
    s=pd.read_csv(ROOT/'data/processed/campaign_summary.csv').set_index('campaign')
    assert s.customers.sum()==64000
    assert s.purchasers.sum()==578
    assert s.total_revenue.sum()==pytest.approx(67258.13)
    assert (s.conversion_rate==s.purchasers/s.customers).all() or np.allclose(s.conversion_rate,s.purchasers/s.customers)
    for arm,purchases,n in [("Men's merchandise",267,21307),("Women's merchandise",189,21387)]:
        assert s.loc[arm,'purchasers']==purchases
        assert s.loc[arm,'customers']==n
        assert s.loc[arm,'conversion_rate']-s.loc['No email','conversion_rate']>0

def test_cube_has_no_double_counting():
    c=pd.read_csv(ROOT/'data/processed/excel_cube.csv')
    s=pd.read_csv(ROOT/'data/processed/campaign_summary.csv').set_index('campaign')
    assert not c.duplicated(['campaign','prior_channel','recency_band','newbie']).any()
    for arm,g in c.groupby('campaign'):
        assert g.customers.sum()==s.loc[arm,'customers']
        assert g.purchasers.sum()==s.loc[arm,'purchasers']
        assert g.total_revenue.sum()==pytest.approx(s.loc[arm,'total_revenue'])

def test_holm_values_match_independent_fisher_tests():
    e=pd.read_csv(ROOT/'data/processed/campaign_effects.csv')
    raw=[stats.fisher_exact([[267,21307-267],[122,21306-122]]).pvalue,
         stats.fisher_exact([[189,21387-189],[122,21306-122]]).pvalue]
    # First ordered p is multiplied by two, second by one; monotonic step-down.
    assert np.allclose(e['p_holm'],[2*raw[0],max(2*raw[0],raw[1])],rtol=1e-9,atol=0)
