"""Reproduce Email Campaign Analysis from the original Hillstrom extract."""
from pathlib import Path
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import duckdb
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint, proportion_effectsize
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower

ROOT = Path(__file__).resolve().parents[1]
RAW_URL = 'http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv'
SOURCE_URL = 'https://blog.minethatdata.com/2008/03/'
ARMS = ['No email', "Men's merchandise", "Women's merchandise"]
SEED = 20260917


def scalar(x):
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.floating,)): return float(x)
    if isinstance(x, (np.bool_,)): return bool(x)
    raise TypeError(type(x).__name__)


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=scalar, allow_nan=False) + '\n')


def contrast(a, b, alpha=.05):
    """Newcombe interval for purchase-rate difference; Fisher exact test."""
    na, nb = len(a), len(b)
    ca, cb = int(a.sum()), int(b.sum())
    pa, pb = ca / na, cb / nb
    lo, hi = confint_proportions_2indep(ca, na, cb, nb, method='newcomb', compare='diff', alpha=alpha)
    p = stats.fisher_exact([[ca, na-ca], [cb, nb-cb]], alternative='two-sided').pvalue
    return {'difference': pa-pb, 'ci_low': float(lo), 'ci_high': float(hi),
            'p_value': float(p), 'relative_lift': (pa/pb-1) if pb else None,
            'treatment_n': na, 'control_n': nb, 'treatment_purchases': ca, 'control_purchases': cb}


def bootstrap_means(values, draws, rng):
    """Exact empirical nonparametric bootstrap, compressed by unique dollar amounts."""
    values, counts = np.unique(np.asarray(values, dtype=float), return_counts=True)
    n = int(counts.sum())
    samples = rng.multinomial(n, counts/n, size=draws)
    return samples @ values / n


def budget(contacts, uplift, margin, cost, fixed):
    if contacts < 0 or not 0 <= margin <= 1 or cost < 0 or fixed < 0:
        raise ValueError('Budget inputs outside their allowed ranges')
    return contacts * (uplift * margin - cost) - fixed


def main(draws=5000):
    output = ROOT/'data/processed'; output.mkdir(exist_ok=True, parents=True)
    raw_path = ROOT/'data/raw/hillstrom.csv'
    raw = pd.read_csv(raw_path)
    checks=[]
    def check(name, passed, detail):
        checks.append({'check':name,'passed':bool(passed),'detail':str(detail)})
    expected=['recency','history_segment','history','mens','womens','zip_code','newbie','channel','segment','visit','conversion','spend']
    check('Expected source columns',list(raw.columns)==expected, ', '.join(raw.columns))
    check('Source population',len(raw)==64000,len(raw))
    check('No missing source values',raw.isna().sum().sum()==0,raw.isna().sum().sum())
    for c in ['mens','womens','newbie','visit','conversion']:
        check(f'{c} is binary',raw[c].isin([0,1]).all(), sorted(int(v) for v in raw[c].unique()))
    check('Recency between 1 and 12 months',raw.recency.between(1,12).all(),f'{raw.recency.min()} to {raw.recency.max()}')
    check('Nonnegative historical spending',raw.history.ge(0).all(), raw.history.min())
    check('Nonnegative outcome spending',raw.spend.ge(0).all(),raw.spend.min())
    check('Three expected source arms',set(raw.segment)=={'No E-Mail','Mens E-Mail','Womens E-Mail'},sorted(raw.segment.unique()))
    check('Expected prior channels',set(raw.channel)=={'Phone','Web','Multichannel'},sorted(raw.channel.unique()))
    check('Expected area categories',set(raw.zip_code)=={'Rural','Surburban','Urban'},sorted(raw.zip_code.unique()))
    check('Purchase implies visit',(raw.conversion<=raw.visit).all(),int((raw.conversion>raw.visit).sum()))
    check('Positive spending matches purchase',((raw.spend>0)==(raw.conversion==1)).all(),int(((raw.spend>0)!=(raw.conversion==1)).sum()))
    check('Source monetary values have cent precision',np.allclose(raw.spend*100,np.round(raw.spend*100)), 'Cent-level spending')
    if not all(c['passed'] for c in checks):
        save_json(output/'quality_checks.json',checks)
        raise ValueError('Source quality check failed; inspect quality_checks.json')
    con=duckdb.connect(str(output/'analysis.duckdb'))
    con.register('raw_customers',raw)
    con.execute((ROOT/'sql/01_prepare.sql').read_text())
    customers=con.sql('SELECT * FROM customers ORDER BY row_id').df()
    summary=con.sql((ROOT/'sql/02_arm_summary.sql').read_text()).df()
    summary=summary.set_index('campaign').loc[ARMS].reset_index()
    segments=con.sql((ROOT/'sql/03_segment_summary.sql').read_text()).df()
    check('All assigned customers retained',len(customers)==len(raw),len(customers))
    check('Extract row keys are unique',customers.row_id.nunique()==len(raw),customers.row_id.nunique())
    check('Campaign mapping complete',customers.campaign.notna().all(),'No unmapped assignments')
    check('Arm counts reconcile',summary.customers.sum()==len(raw),summary.customers.sum())
    check('Purchases reconcile',summary.purchasers.sum()==raw.conversion.sum(),summary.purchasers.sum())
    check('Visitors reconcile',summary.visitors.sum()==raw.visit.sum(),summary.visitors.sum())
    check('Revenue reconciles',abs(summary.total_revenue.sum()-raw.spend.sum())<1e-7,summary.total_revenue.sum())
    for dimension,g in segments.groupby('dimension'):
        check(f'{dimension} population reconciles',int(g.customers.sum())==len(raw),g.customers.sum())
    control=customers[customers.campaign==ARMS[0]]
    rng=np.random.default_rng(SEED)
    boot={a:bootstrap_means(customers.loc[customers.campaign==a,'revenue'],draws,rng) for a in ARMS}
    effects=[]
    for arm in ARMS[1:]:
        a=customers[customers.campaign==arm]
        c=contrast(a.purchased.to_numpy(),control.purchased.to_numpy())
        simultaneous=contrast(a.purchased.to_numpy(),control.purchased.to_numpy(),alpha=.025)
        rev_dist=boot[arm]-boot[ARMS[0]]
        rev_ci=np.quantile(rev_dist,[.025,.975])
        welch=stats.ttest_ind(a.revenue,control.revenue,equal_var=False)
        effects.append({'campaign':arm, **c,
            'family_ci_low':simultaneous['ci_low'],'family_ci_high':simultaneous['ci_high'],
            'incremental_revenue':float(a.revenue.mean()-control.revenue.mean()),
            'revenue_ci_low':float(rev_ci[0]),'revenue_ci_high':float(rev_ci[1]),
            'revenue_welch_p':float(welch.pvalue),
            'incremental_visits':float(a.visited.mean()-control.visited.mean())})
    adjusted=multipletests([e['p_value'] for e in effects],alpha=.05,method='holm')
    for i,e in enumerate(effects): e.update(p_holm=float(adjusted[1][i]),significant=bool(adjusted[0][i]))
    direct=contrast(customers.loc[customers.campaign==ARMS[1],'purchased'].to_numpy(),customers.loc[customers.campaign==ARMS[2],'purchased'].to_numpy())
    direct['comparison']="Men's merchandise minus women's merchandise"
    direct['revenue_difference']=float(summary.loc[1,'revenue_per_customer']-summary.loc[2,'revenue_per_customer'])
    direct['revenue_ci_low'],direct['revenue_ci_high']=map(float,np.quantile(boot[ARMS[1]]-boot[ARMS[2]],[.025,.975]))
    for i,row in summary.iterrows():
        lo,hi=proportion_confint(int(row.purchasers),int(row.customers),method='wilson')
        summary.loc[i,'conversion_ci_low']=lo;summary.loc[i,'conversion_ci_high']=hi
    seg_effects=[]
    dims={'Prior channel':'prior_channel','Purchase recency':'recency_band','Newbie flag':'newbie'}
    for dim,col in dims.items():
        for value,g in customers.groupby(col):
            b=g[g.campaign==ARMS[0]]
            for arm in ARMS[1:]:
                a=g[g.campaign==arm]
                vals=contrast(a.purchased.to_numpy(),b.purchased.to_numpy())
                seg_effects.append({'dimension':dim,'segment':f'Newbie = {value}' if col=='newbie' else str(value),
                    'campaign':arm, **vals, 'revenue_difference':float(a.revenue.mean()-b.revenue.mean()),
                    'scope':'Exploratory; unadjusted 95% interval'})
    # Diagnostics are pre-treatment only; none determines exclusions.
    x=customers[['recency_months','prior_year_spend','bought_mens','bought_womens','newbie']].astype(float).copy()
    x['log_prior_spend']=np.log1p(x.pop('prior_year_spend'))
    x=pd.concat([x,pd.get_dummies(customers[['prior_channel','area_type']],dtype=float)],axis=1)
    balances=[]
    for arm in ARMS[1:]:
        for col in x.columns:
            a=x.loc[customers.campaign==arm,col];b=x.loc[customers.campaign==ARMS[0],col]
            denom=math.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
            balances.append({'campaign':arm,'covariate':col,'smd':float((a.mean()-b.mean())/denom) if denom else 0.,'treatment_mean':float(a.mean()),'control_mean':float(b.mean())})
    srm=stats.chisquare(summary.customers.to_numpy(),np.repeat(len(raw)/3,3))
    # Drop one level per categorical predictor to avoid collinearity.
    design=customers[['recency_months','bought_mens','bought_womens','newbie']].astype(float).copy()
    design['log_prior_spend']=np.log1p(customers.prior_year_spend)
    design['email_mens']=(customers.campaign==ARMS[1]).astype(float)
    design['email_womens']=(customers.campaign==ARMS[2]).astype(float)
    design=pd.concat([design,pd.get_dummies(customers[['prior_channel','area_type']],drop_first=True,dtype=float)],axis=1)
    model=sm.OLS(customers.purchased.astype(float),sm.add_constant(design)).fit(cov_type='HC3')
    regress=[]
    for a,col in zip(ARMS[1:],['email_mens','email_womens']):
        low,high=model.conf_int().loc[col]
        regress.append({'campaign':a,'adjusted_difference':float(model.params[col]),'ci_low':float(low),'ci_high':float(high),'p_value':float(model.pvalues[col]),'method':'Linear probability model; HC3 robust standard errors'})
    cap=float(customers.revenue.quantile(.999))
    sensitivity=[]
    for arm in ARMS[1:]:
        a=customers.loc[customers.campaign==arm,'revenue']; b=control.revenue
        sensitivity.append({'campaign':arm,'original_difference':float(a.mean()-b.mean()),'capped_difference':float(a.clip(upper=cap).mean()-b.clip(upper=cap).mean()),'pooled_cap':cap})
    top_n=max(1,math.ceil(len(customers)*.001))
    top_share=float(customers.revenue.nlargest(top_n).sum()/customers.revenue.sum())
    power=[];p0=float(control.purchased.mean())
    for mde_pp in [.1,.2,.3,.5]:
        for target_power in [.8,.9]:
            n=math.ceil(NormalIndPower().solve_power(effect_size=proportion_effectsize(p0+mde_pp/100,p0),alpha=.025,power=target_power,ratio=1,alternative='two-sided'))
            power.append({'baseline_rate':p0,'absolute_uplift_pp':mde_pp,'power':target_power,'alpha_per_comparison':.025,'customers_per_arm':n,'total_three_arms':3*n})
    result={'meta':{'title':'Email Campaign Analysis','author':'Shashank Pabitwar','source_name':'Kevin Hillstrom — MineThatData email experiment (2008)',
        'source_url':SOURCE_URL,'raw_url':RAW_URL,'sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        'generated_at':datetime.now(timezone.utc).isoformat(),'source_year':2008,'outcome_window':'Two weeks following the email campaign',
        'n':len(raw),'bootstrap_draws':draws,'seed':SEED,'identical_rows_retained':int(raw.duplicated().sum())},
        'summary':summary.to_dict('records'),'effects':effects,'direct_comparison':direct,'segments':seg_effects,
        'segment_summary':segments.to_dict('records'),'balance':balances,'regression':regress,
        'revenue_sensitivity':sensitivity,'power':power,'quality':checks,
        'diagnostics':{'allocation_p':float(srm.pvalue),'allocation_statistic':float(srm.statistic),
            'max_abs_smd':max(abs(b['smd']) for b in balances),'top_revenue_customers':top_n,'top_revenue_share':top_share,'spend_cap':cap},
        'default_assumptions':{'contacts':10000,'margin':.5,'send_cost':.05,'fixed_cost':500}}
    summary.to_csv(output/'campaign_summary.csv',index=False)
    segments.to_csv(output/'segment_summary.csv',index=False)
    pd.DataFrame(effects).to_csv(output/'campaign_effects.csv',index=False)
    pd.DataFrame(seg_effects).to_csv(output/'segment_effects.csv',index=False)
    pd.DataFrame(balances).to_csv(output/'covariate_balance.csv',index=False)
    pd.DataFrame(power).to_csv(output/'sample_size_plan.csv',index=False)
    pd.DataFrame(regress).to_csv(output/'adjusted_effects.csv',index=False)
    # Full cleaned observations are local and downloadable only from original source.
    customers.to_csv(output/'customers.csv',index=False)
    save_json(output/'results.json',result);save_json(output/'quality_checks.json',checks)
    con.close()
    print(json.dumps({'summary':result['summary'],'effects':effects,'direct':direct,'diagnostics':result['diagnostics'],'quality':f'{sum(c["passed"] for c in checks)}/{len(checks)}'},indent=2,default=scalar))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--bootstrap-draws',type=int,default=5000)
    args=parser.parse_args();main(args.bootstrap_draws)
