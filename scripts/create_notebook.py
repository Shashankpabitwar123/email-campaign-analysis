"""Build and execute the reviewable analysis companion."""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
cells=[]
def md(s): cells.append(nbf.v4.new_markdown_cell(s))
def code(s): cells.append(nbf.v4.new_code_cell(s))
md('''# Email Campaign Analysis
**Shashank Pabitwar · September 2026 · Independent analysis of a historical experiment**

## tl;dr
The men's-merchandise email increased purchase conversion by **0.68 percentage points** versus no email; the women's-merchandise email increased it by **0.31 points**. Both planned comparisons pass the Holm-adjusted 5% threshold. Revenue is variable, so an editable budget scenario and a fresh experiment are more useful than a claim of guaranteed profit.

This notebook reproduces the reasoning, checks key numbers, and keeps plotting code editable. It does not claim that I ran the original experiment or delivered a business revenue increase.''')
md('''## Context & Methods
The [original MineThatData challenge](https://blog.minethatdata.com/2008/03/minethatdata-e-mail-analytics-and-data.html) describes random assignment to two emails and a no-email control, with two-week outcomes. The analysis population is every assigned customer, including zero-spend customers.

Primary outcome: purchase conversion. Two-sided Fisher exact tests compare each email with control; Holm controls the two-test family. Newcombe difference intervals are shown at 97.5% individually for a Bonferroni family coverage of at least approximately 95%. These are approximate intervals, distinct from the exact Fisher test. Secondary revenue intervals are individual 95% percentile bootstrap intervals (5,000 draws, fixed seed). Segments and adjusted regression are sensitivity/exploratory analyses.

The analysis plan in `docs/analysis-plan.md` was written before this project's calculations but is retrospective, not a preregistration. The dataset has long been publicly studied.''')
code('''from pathlib import Path
import json, sys
import numpy as np
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from IPython.display import display

ROOT=Path.cwd()
if ROOT.name == 'artifacts': ROOT=ROOT.parent
assert (ROOT/'sql/01_prepare.sql').exists(), 'Run from the repository root or artifacts directory.'
sys.path.insert(0,str(ROOT/'scripts'))
from analyze import contrast, bootstrap_means, budget
result=json.loads((ROOT/'data/processed/results.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':130})
FIG=ROOT/'artifacts/figures'; FIG.mkdir(exist_ok=True,parents=True)
print('Analysis seed:',result['meta']['seed'],'| Bootstrap draws:',result['meta']['bootstrap_draws'])''')
md('''## Data
Download the original extract with `python scripts/fetch_data.py`, then run the pipeline. The public repository distributes aggregate analysis outputs, not a copy of the source records.

There is no customer identifier. The generated row key identifies an extract row only. Exact repeated profiles are retained: dropping them would remove valid-looking customers without evidence that they are accidental duplicates. `Surburban` is standardized to `Suburban` in a derived field. Campaign names describe merchandise, not recipient gender.''')
code('''raw=pd.read_csv(ROOT/'data/raw/hillstrom.csv')
con=duckdb.connect()
con.register('raw_customers',raw)
con.execute((ROOT/'sql/01_prepare.sql').read_text())
summary=con.sql((ROOT/'sql/02_arm_summary.sql').read_text()).df()
summary=summary.set_index('campaign').loc[['No email',"Men's merchandise","Women's merchandise"]].reset_index()
quality=pd.DataFrame(result['quality'])
assert len(raw)==64000 and quality.passed.all()
assert int(summary.purchasers.sum())==578
assert np.isclose(summary.total_revenue.sum(),67258.13)
print(f'{len(quality)} of {len(quality)} quality checks passed; {raw.duplicated().sum():,} repeated profiles retained.')
display(summary[['campaign','customers','purchasers','conversion_rate','total_revenue','revenue_per_customer']])''')
md('''## Results
### Purchase conversion
Rates are purchases divided by assigned customers, not visitors. A visitor-only denominator would condition on a behavior the email could itself change.''')
code('''fig,ax=plt.subplots(figsize=(8,4.5))
bars=ax.bar(['No email',"Men's merchandise","Women's merchandise"],summary.conversion_rate,color=['#8B98A5','#176B88','#6A69A5'],width=.56)
ax.yaxis.set_major_formatter(PercentFormatter(1)); ax.set_ylim(0,.015)
ax.set_ylabel('Purchasers / assigned customers'); ax.set_title('Both email groups purchased more often')
for bar,v in zip(bars,summary.conversion_rate): ax.text(bar.get_x()+bar.get_width()/2,v+.0003,f'{v:.2%}',ha='center',fontweight='bold')
ax.text(0,-.24,'Historical 2008 experiment · 64,000 customers · two-week outcomes',transform=ax.transAxes,fontsize=9,color='#586778')
fig.tight_layout();fig.savefig(FIG/'conversion.png',bbox_inches='tight');plt.show()''')
code('''customers=con.sql('SELECT * FROM customers').df()
control=customers.loc[customers.campaign=='No email','purchased'].to_numpy()
verified=[]
for e in result['effects']:
    treatment=customers.loc[customers.campaign==e['campaign'],'purchased'].to_numpy()
    calculated=contrast(treatment,control,alpha=.025)
    assert np.isclose(calculated['difference'],e['difference'])
    assert np.isclose(calculated['ci_low'],e['family_ci_low'])
    verified.append({'Campaign':e['campaign'],'Uplift (pp)':100*calculated['difference'],
                     'Family lower (pp)':100*calculated['ci_low'],'Family upper (pp)':100*calculated['ci_high'],
                     'Holm p':e['p_holm']})
display(pd.DataFrame(verified).round(6))''')
md('''A **0.68 percentage-point** increase is about 6.8 extra purchasers per 1,000 assigned customers. It is not a 0.68% relative increase. Statistical significance supports a historical effect under the assignment assumptions; it does not tell us today's budget return.''')
md('''### Revenue, including uncertainty
Spending is mostly zero and highly skewed. The empirical bootstrap resamples all customers, including non-purchasers. Compressing repeated dollar values with multinomial counts is mathematically equivalent to sampling customer indices, while using less memory.''')
code('''rng=np.random.default_rng(result['meta']['seed'])
boot={arm:bootstrap_means(customers.loc[customers.campaign==arm,'revenue'],5000,rng)
      for arm in ['No email',"Men's merchandise","Women's merchandise"]}
fig,ax=plt.subplots(figsize=(8,4))
for i,e in enumerate(result['effects']):
    delta=boot[e['campaign']]-boot['No email']
    low,high=np.quantile(delta,[.025,.975])
    assert np.isclose(low,e['revenue_ci_low']) and np.isclose(high,e['revenue_ci_high'])
    x=e['incremental_revenue']
    ax.errorbar(x,i,xerr=[[x-low],[high-x]],fmt='o',color=['#176B88','#6A69A5'][i],capsize=5,markersize=8)
    ax.text(high+.02,i,f'${x:.2f}  [${low:.2f}, ${high:.2f}]',va='center',fontsize=10)
ax.axvline(0,color='#9EAAB4',linestyle='--');ax.set_yticks([0,1],["Men's merchandise","Women's merchandise"])
ax.set_xlim(-.05,1.65);ax.set_ylim(-.6,1.6);ax.set_xlabel('Additional USD per assigned customer versus no email')
ax.set_title('Revenue estimates are positive, but uncertain')
fig.tight_layout();fig.savefig(FIG/'revenue_uncertainty.png',bbox_inches='tight');plt.show()
print('Top 64 customers account for {:.2%} of observed revenue.'.format(result['diagnostics']['top_revenue_share']))
display(pd.DataFrame(result['revenue_sensitivity']))''')
md('''The 99.9th-percentile spending cap is a sensitivity analysis, not a replacement outcome. Capping reduces the influence of extreme observations and changes the estimand. The main result keeps the original revenue values.''')
md('''### Segment exploration and balance
Prior purchase channel and recency existed before assignment. Comparisons within these groups are exploratory and do not validate whom to target. An effect significant in one segment and non-significant in another does not by itself prove that the segment effects differ.''')
code('''channel=con.sql((ROOT/'sql/05_exploratory_channel_comparison.sql').read_text()).df()
display(channel[['campaign','prior_channel','customers','control_customers','conversion_difference','exploratory_channel_rank']])
print('Equal-allocation chi-square p: {:.4f}'.format(result['diagnostics']['allocation_p']))
print('Maximum absolute pre-treatment standardized difference: {:.4f}'.format(result['diagnostics']['max_abs_smd']))
display(pd.DataFrame(result['regression']))''')
md('''The allocation and balance checks are diagnostics; they cannot prove randomization was implemented correctly. Adjusted conversion estimates are close to the unadjusted ones. The linear probability model uses robust HC3 standard errors and pre-treatment covariates only.''')
md('''### Budget scenarios and the next experiment
The source does not supply campaign costs or margin. A business model must therefore expose those assumptions and avoid calling its output realized profit.''')
code('''scenario=[]
for e in result['effects']:
    scenario.append({'Campaign':e['campaign'],
        'Modeled contribution':budget(10000,e['incremental_revenue'],.5,.05,500),
        'Historical effect lower':budget(10000,e['revenue_ci_low'],.5,.05,500),
        'Historical effect upper':budget(10000,e['revenue_ci_high'],.5,.05,500)})
display(pd.DataFrame(scenario).round(2))
display(pd.DataFrame(result['power']))
con.close()''')
md('''## Takeaways
1. Use the men's-merchandise creative as the lead candidate in a fresh randomized test. The historical evidence supports increased purchases, not guaranteed current profit.
2. Budget with explicit costs and margin. The default 10,000-contact scenario is approximately **$2,849** contribution for the men's email; the range accounts only for uncertainty in the historical revenue estimate.
3. Investigate segment hypotheses in a new test. Do not deploy a targeting policy selected from noisy in-sample subgroup rankings.
4. For a three-arm study detecting **0.3 percentage points** at 80% power, the normal approximation gives **14,989 customers per arm**, or **44,967 total**, under the historical baseline and multiplicity allowance. Update these assumptions first.

See `docs/decision-memo.md`, `docs/future-experiment.md`, and `docs/methodology.md` for the decision, measurement plan and limitations. No current business deployment or realized revenue improvement is claimed.''')
nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
nbf.validate(nb)
NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbf.write(nb,ROOT/'artifacts/Email_Campaign_Analysis.ipynb')
assert all(not any(o.output_type=='error' for o in c.get('outputs',[])) for c in nb.cells)
print(f'Executed {len(nb.cells)} cells successfully; notebook and two figures saved.')
