from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'data/processed/results.json').read_text())
base={'label':'Hillstrom public randomized email experiment (2008)', 'links':[{'label':'Original study and dataset description','url':r['meta']['source_url']}], 'files':['hillstrom.csv'], 'executedAt':r['meta']['generated_at'], 'period':'Two weeks following the 2008 email experiment; exact dates unavailable', 'caveats':['Independent retrospective analysis. Historical effects are not a forecast of current campaign performance.','Campaign names describe merchandise, not customer gender.','Costs, margins, delivery logs and unsubscribe outcomes are unavailable.'], 'evidenceFlow':[{'title':'Original public extract','detail':'Downloaded the original MineThatData CSV. SHA-256: '+r['meta']['sha256']},{'title':'Reproducible analysis','detail':'scripts/analyze.py executes the SQL scripts, statistical estimates, regression, bootstrap and quality checks.'}]}
def q(rows,description,sql=None,definitions=[]):
 s={**base,'description':description,'metricDefinitions':definitions}
 if sql:s['sql']=(ROOT/'sql'/sql).read_text();s['tables']=['raw_customers','customers']
 return {'rows':rows,'source':s,'methods':[{'language':'python','code':'python scripts/analyze.py --bootstrap-draws 5000'}]}
summary=[{**a,'conversion_pct':a['conversion_rate']*100,'visit_pct':a['visit_rate']*100} for a in r['summary']]
effects=[{**a,'uplift_pp':a['difference']*100,'lower_pp':a['family_ci_low']*100,'upper_pp':a['family_ci_high']*100} for a in r['effects']]
queries={
'campaign_summary':q(summary,'One row per randomized assignment arm. All assigned customers remain in denominators.','02_arm_summary.sql',[{'label':'Conversion rate','definition':'Customers who purchased divided by all customers assigned to that arm during the two-week outcome window.'},{'label':'Revenue per customer','definition':'Total two-week spending divided by all assigned customers, including zeros.'}]),
'campaign_effects':q(effects,'Each email minus the no-email control. Conversion is primary; revenue is secondary.',None,[{'label':'Conversion uplift','definition':'Treatment conversion rate minus control conversion rate, in percentage points. Chart intervals are 97.5% Newcombe intervals per comparison, providing approximate conservative 95% family coverage across two planned contrasts.'},{'label':'Incremental revenue','definition':'Difference in mean spending per assigned customer. Individual 95% percentile intervals use 5,000 within-arm bootstrap samples with seed 20260917.'},{'label':'Modeled contribution','definition':'Contacts × (historical incremental revenue × assumed contribution margin − assumed send cost) − assumed fixed cost. A scenario, not realized profit.'}]),
'segment_effects':q([{**x,'row_key':x['dimension']+'|'+x['segment']+'|'+x['campaign']} for x in r['segments']],'Exploratory within-segment treatment comparisons. Individual 95% Newcombe intervals are unadjusted; segment selection is not validated.','03_segment_summary.sql'),
'balance':q(r['balance'],'Standardized mean differences for pre-treatment covariates. Diagnostics support a plausibility check; they do not verify original assignment logs.'),
'quality':q(r['quality'],'Executable source and reconciliation checks. Equal profiles are retained because there is no customer identifier.'),
'regression':q(r['regression'],'Covariate-adjusted linear probability model with HC3 standard errors. Pre-treatment covariates only; sensitivity analysis.'),
'power':q([{**x,'row_key':str(x['absolute_uplift_pp'])+'|'+str(x['power'])} for x in r['power']],'Prospective sample-size scenarios anchored to the historical control rate. Equal allocation, two-sided alpha .025 per contrast. Normal approximation, not a duration forecast.'),
'revenue_sensitivity':q(r['revenue_sensitivity'],'Sensitivity only: cap spending at pooled 99.9th percentile; original spending is retained in all primary results.'),
'direct_comparison':q([r['direct_comparison']],'Secondary direct comparison of the two email variants. Individual 95% Newcombe conversion interval and 95% bootstrap revenue interval; not part of the primary two-comparison family.'),
'diagnostics':q([r['diagnostics']],'Assignment chi-square against equal allocation, maximum absolute covariate standardized difference and concentration of observed revenue.')}
s={'title':'Email Campaign Analysis','surface':'dashboard','status':'reviewed','buildStatus':'creating','generatedAt':r['meta']['generated_at'],'filters':[],'queries':queries}

existing=ROOT/'web/src/data.json'
if existing.exists():
    old=json.loads(existing.read_text())
    s['id']=old['id']
    s['buildStatus']=old.get('buildStatus','creating')
(ROOT/'data/processed/dashboard_snapshot.json').write_text(json.dumps(s,indent=2))
if existing.exists(): existing.write_text(json.dumps(s,indent=2))
