import React from 'react';
import { DataComponent, DataTable, EvidenceChart, Section, SectionHeader, Slider, Button, Filters, useSectionFilters, useDashboardTabs, useDataApp, SortableRegion, SortableItem } from '../../data-app-public.jsx';
import './email-analysis.css';

const tabs=[{id:'results',label:'Results'},{id:'segments',label:'Customer segments'},{id:'budget',label:'Budget & next test'},{id:'methods',label:'Methods & downloads'}];
const num=(v,d=0)=>Number(v).toLocaleString('en-US',{maximumFractionDigits:d,minimumFractionDigits:d});
const pct=v=>`${num(v*100,2)}%`;
const pp=v=>`${v>=0?'+':''}${num(v*100,2)} pp`;
const usd=(v,d=2)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',minimumFractionDigits:d,maximumFractionDigits:d}).format(v);
const pvalue=v=>v<.0001?'< 0.0001':num(v,4);
const campaignName=a=>a.replace(' merchandise',' merchandise email');
const defaults={contacts:10000,margin:50,sendCost:5,fixedCost:500};

function Intervals({rows,estimate,low,high,label='campaign',format=pp,unit='Percentage-point increase',zero=true}){
  const minimum=Math.min(zero?0:Infinity,...rows.map(r=>r[low]));
  const maximum=Math.max(0,...rows.map(r=>r[high]));
  const span=(maximum-minimum)||1,pad=span*.08;
  const start=minimum-pad,end=maximum+pad;
  const pos=v=>8+((v-start)/(end-start))*84;
  return <div className="eca-intervals" data-reviewed-rows>
    {rows.map((r,i)=><div className="eca-interval-row" key={`${r[label]}-${i}`}>
      <div className="eca-interval-label"><strong>{r[label]}</strong><span>{r.treatment_n?`${num(r.treatment_n)} email · ${num(r.control_n)} control`:''}</span></div>
      <svg viewBox="0 0 500 54" role="img" aria-label={`${r[label]}: ${format(r[estimate])}, interval ${format(r[low])} to ${format(r[high])}`}>
        <line x1={`${pos(0)}%`} y1="5" x2={`${pos(0)}%`} y2="48" stroke="currentColor" opacity=".22" strokeDasharray="3 3"/>
        <g tabIndex="0"><title>{`${r[label]}: ${format(r[estimate])}; interval ${format(r[low])} to ${format(r[high])}`}</title>
        <line x1={`${pos(r[low])}%`} y1="27" x2={`${pos(r[high])}%`} y2="27" stroke="var(--chart-1)" strokeWidth="4"/>
        {[low,high].map(key=><line key={key} x1={`${pos(r[key])}%`} y1="18" x2={`${pos(r[key])}%`} y2="36" stroke="var(--chart-1)" strokeWidth="2"/>)}
        <circle cx={`${pos(r[estimate])}%`} cy="27" r="7" fill="var(--chart-1)"/>
        </g>
      </svg>
      <div className="eca-interval-value"><strong>{format(r[estimate])}</strong><span>{format(r[low])} to {format(r[high])}</span></div>
    </div>)}
    <p className="eca-muted">{unit}. Dots are estimates; lines show uncertainty. The dashed line marks no effect.</p>
  </div>;
}
function Evidence({id,queryId,title,rows,children,description,...rest}){
 return <DataComponent variant="card" id={id} queryId={queryId} title={title} kind="chart" displayRows={rows} sourceRows={rows} description={description} {...rest}>{children}</DataComponent>;
}
function ResultView({rows,effects,direct,diag}){
 const all=rows.reduce((s,r)=>s+r.customers,0);
 const men=effects.find(r=>r.campaign==="Men's merchandise");
 const women=effects.find(r=>r.campaign==="Women's merchandise");
 const storyRows=rows.map(r=>({...r,buyers_per_1000:r.conversion_rate*1000}));
 return <>
   <DataComponent id="result-summary" queryId="campaign_summary" queryIds={['campaign_summary','campaign_effects']} kind="narrative" title="The project in one minute" displayRows={storyRows} sourceRowsByQuery={{campaign_summary:rows,campaign_effects:effects}} variant="plain">
    <div className="eca-story">
     <p className="eca-takeaway" data-editable-id="result-takeaway">A store wants to know whether its emails bring in extra buyers.</p>
     <p className="eca-body">Before paying for another campaign, it needs to know which email works and whether the extra sales could cover the cost.</p>
     <p className="eca-body">I analyzed Kevin Hillstrom's public experiment from <strong>2008</strong>: <strong data-reviewed-rows>{num(all)} customers</strong> were randomly split into the three groups below. Their visits, purchases and spending were tracked for <strong>two weeks</strong>.</p>
     <div className="eca-story-groups" data-reviewed-rows aria-label="Purchase results per 1,000 customers">
      {storyRows.map(r=><div className="eca-story-group" key={r.campaign}>
       <span>{r.campaign==='No email'?'No email':r.campaign.replace('merchandise','products')+' email'}</span>
       <strong>About {num(r.buyers_per_1000)} buyers</strong>
       <span>per 1,000 customers · {pct(r.conversion_rate)} bought</span>
      </div>)}
     </div>
     <p className="eca-body">Some customers bought even without an email. Compared with that group, the men's email brought in about <strong data-reviewed-rows>{num(men.difference*1000)} extra buyers per 1,000</strong>, and the women's email about <strong data-reviewed-rows>{num(women.difference*1000)} extra buyers</strong>.</p>
     <p className="eca-story-decision"><strong>My recommendation:</strong> make the men's-products email the leading option in a fresh test with today's customers. A 2008 result needs to be tested again before spending heavily.</p>
     <p className="eca-note">I checked the data, compared the groups and built the budget model. I did not run the original campaign. The email names describe products, not the customers' gender.</p>
    </div>
   </DataComponent>
   <div className="eca-definition"><strong>Explore the evidence:</strong> the charts below show the exact results and uncertainty. Customer segments compares shopping histories; Budget &amp; next test lets you change costs; Methods &amp; downloads explains the calculations and shares the files.</div>
   <SortableRegion id="results:charts" variant="canvas" columns={12} spacing="standard" rows={[{id:'results:rates',items:['conversion-rates','purchase-effects']},{id:'results:revenue',items:['revenue-effects','campaign-comparison']}]}>
    <SortableItem id="conversion-rates" label="Purchase conversion" kind="chart" span={6}>
     <EvidenceChart id="conversion-rates" queryId="campaign_summary" title="How many customers bought something?" rows={rows.map(r=>({...r,conversionRate:r.conversion_rate}))} sourceRows={rows} variant="card" height={265} spec={{type:'bar',x:'campaign',y:'conversionRate',stackable:false,valueDecimals:2,showXAxisLabel:false,yLabel:'Share of assigned customers'}}>
       <div className="eca-rate-labels" data-reviewed-rows>{rows.map(r=><div key={r.campaign}><strong>{pct(r.conversion_rate)}</strong><span>{num(r.purchasers)} / {num(r.customers)} customers</span></div>)}</div>
     </EvidenceChart>
    </SortableItem>
    <SortableItem id="purchase-effects" label="Additional purchases" kind="chart" span={6}>
     <Evidence id="purchase-effects" queryId="campaign_effects" title="Additional purchases versus no email" rows={effects}>
      <Intervals rows={effects} estimate="difference" low="family_ci_low" high="family_ci_high"/>
      <p className="eca-note">For every 1,000 assigned customers, the estimated increases are {num(effects[0].difference*1000,1)} and {num(effects[1].difference*1000,1)} purchases. Intervals allow for the two planned comparisons.</p>
     </Evidence>
    </SortableItem>
    <SortableItem id="revenue-effects" label="Additional revenue" kind="chart" span={6}>
     <Evidence id="revenue-effects" queryId="campaign_effects" title="Additional revenue per assigned customer" rows={effects}>
      <Intervals rows={effects} estimate="incremental_revenue" low="revenue_ci_low" high="revenue_ci_high" format={usd} unit="US dollars per assigned customer"/>
      <p className="eca-note">Secondary outcome. Individual 95% bootstrap intervals from 5,000 resamples. Zero-spend customers remain included.</p>
     </Evidence>
    </SortableItem>
    <SortableItem id="campaign-comparison" label="Campaign detail" kind="table" span={6}>
     <DataComponent id="campaign-comparison" queryId="campaign_summary" title="Revenue and response" kind="table" variant="card" displayRows={rows} sourceRows={rows}>
      <DataTable rows={rows} rowKey="campaign" searchable={false} columns={[{field:'campaign',label:'Assignment'},{field:'visit_rate',label:'Visited',renderCell:pct},{field:'total_revenue',label:'Revenue',renderCell:v=>usd(v,0)},{field:'revenue_per_customer',label:'Per customer',renderCell:v=>usd(v)}]} />
      <p className="eca-note">Visits and purchases answer different questions. Revenue per purchaser conditions on a post-email outcome, so it is not used to estimate campaign impact.</p>
     </DataComponent>
    </SortableItem>
   </SortableRegion>
   <Section id="decision-title" title="What to do with the result" columns={2}>
    <Evidence id="direct-comparison" queryId="direct_comparison" title="Which email should lead the next test?" rows={direct}>
     <p className="eca-body">Use the men's-merchandise creative as the lead candidate for a fresh test. Its conversion rate exceeded the women's-merchandise creative by <strong>{pp(direct[0].difference)}</strong> (individual 95% interval {pp(direct[0].ci_low)} to {pp(direct[0].ci_high)}).</p>
     <p className="eca-note">This direct comparison is secondary. The names refer to merchandise, not the gender of the recipients.</p>
    </Evidence>
    <Evidence id="revenue-caution" queryId="diagnostics" title="Revenue needs a closer look" rows={diag}>
     <div className="eca-stat">{pct(diag[0].top_revenue_share)}</div><p className="eca-body">of observed revenue came from the top {num(diag[0].top_revenue_customers)} customers.</p>
     <p className="eca-note">The budget tab exposes the uncertainty. The methods tab checks whether the direction changes when extreme spending is capped.</p>
    </Evidence>
   </Section>
 </>;
}
function SegmentView(){
 const scope=useSectionFilters([{id:'dimension',label:'Break down by',field:'dimension',defaultValue:'Prior channel',queryIds:['segment_effects']},{id:'campaign',label:'Email',field:'campaign',defaultValue:"Men's merchandise",queryIds:['segment_effects']}],{}, {id:'segment-analysis'});
 const props=scope.componentProps('segment_effects',['dimension','segment','campaign']);
 const rows=props.displayRows.map(r=>({...r,display_label:`${r.segment} · ${r.campaign}`}));
 return <Section id="segments-title" title="Where do the effects differ?" filters={<Filters {...scope.filterProps}/>}>
  <p className="eca-muted">Did the emails work differently for customers with different shopping histories? Choose a customer group and an email to explore. Each result compares that group's buyers with similar customers who received no email. These patterns are clues for a future test, not a proven rule for whom to target.</p>
  <DataComponent id="segment-intervals" queryId="segment_effects" title="Conversion uplift within each segment" kind="chart" variant="card" {...props} displayRows={rows}>
   {rows.length?<Intervals rows={rows} estimate="difference" low="ci_low" high="ci_high" label="display_label"/>:<p>No observations match these filters.</p>}
   <p className="eca-note">Individual 95% intervals are not adjusted for the many segment comparisons. Each row compares customers within the same segment. “Newbie” is the source's binary flag; detailed qualification rules are unavailable.</p>
  </DataComponent>
  <DataComponent id="segment-table" queryId="segment_effects" title="Segment evidence" kind="table" variant="card" {...props}>
   <DataTable rows={props.displayRows} rowKey="row_key" columns={[{field:'dimension',label:'Dimension'},{field:'segment',label:'Segment'},{field:'campaign',label:'Email'},{field:'treatment_n',label:'Assigned email',renderCell:v=>num(v)},{field:'treatment_purchases',label:'Purchased',renderCell:v=>num(v)},{field:'control_n',label:'Control',renderCell:v=>num(v)},{field:'difference',label:'Uplift',renderCell:pp}]} />
  </DataComponent>
 </Section>;
}
function BudgetView({effects,power}){
 const {assumptions,setAssumptions}=useDataApp();
 const a={...defaults,...assumptions};
 const controls=[['contacts','Customers to contact',1000,100000,1000,v=>num(v)],['margin','Contribution margin',0,100,1,v=>`${v}%`],['sendCost','Cost per email (cents)',0,100,1,v=>`${v}¢`],['fixedCost','Fixed campaign cost',0,10000,100,v=>usd(v,0)]];
 const calc=(e,u)=>a.contacts*(u*a.margin/100-a.sendCost/100)-a.fixedCost;
 const modeled=effects.map(e=>({...e,modeled_contribution:calc(e,e.incremental_revenue),lower_contribution:calc(e,e.revenue_ci_low),upper_contribution:calc(e,e.revenue_ci_high),contacts:a.contacts,margin:a.margin/100,send_cost:a.sendCost/100,fixed_cost:a.fixedCost}));
 const curve=Array.from({length:21},(_,i)=>{const contacts=i*5000;return {contacts,...Object.fromEntries(effects.map(e=>[e.campaign,contacts*(e.incremental_revenue*a.margin/100-a.sendCost/100)-a.fixedCost]))}});
 return <>
 <Section id="budget-title" title="Would the campaign be worth repeating?">
  <p className="eca-muted">Extra sales are useful only if they cover the campaign's costs. Change how many customers receive an email, how much the business keeps from each extra sales dollar (contribution margin), and the costs. The results are estimates using the old experiment and your assumptions—not profit actually earned.</p>
  <DataComponent id="budget-model" queryId="campaign_effects" title="Campaign contribution after assumed costs" kind="chart" variant="card" displayRows={modeled} sourceRows={effects}>
   <div className="eca-budget-layout"><div className="eca-controls">{controls.map(([field,label,min,max,step,fmt])=><Slider key={field} label={label} value={a[field]} min={min} max={max} step={step} formatValue={fmt} onChange={value=>setAssumptions(current=>({...current,[field]:value}))}/>)}<Button onClick={()=>setAssumptions({...defaults})}>Reset assumptions</Button></div>
   <div aria-live="polite" data-reviewed-rows>{modeled.map(e=><div className="eca-budget-result" key={e.campaign}><span>{campaignName(e.campaign)}</span><strong className={e.modeled_contribution>=0?'eca-positive':'eca-negative'}>{usd(e.modeled_contribution,0)}</strong><span>Historical-effect interval: {usd(e.lower_contribution,0)} to {usd(e.upper_contribution,0)}</span></div>)}</div></div>
   <p className="eca-formula">Customers × (additional revenue per customer × margin − email cost) − fixed cost</p>
   <p className="eca-note">The range carries forward each historical 95% revenue interval. It excludes uncertainty in costs, margin, future customer behavior and changes since 2008. It is not a forecast interval or observed profit.</p>
  </DataComponent>
  <EvidenceChart id="contact-sensitivity" queryId="campaign_effects" title="How contact volume changes modeled contribution" rows={curve} sourceRows={effects} variant="card" height={270} spec={{type:'line',x:'contacts',y:"Men's merchandise",fields:["Men's merchandise","Women's merchandise"],currency:'USD',stackable:false,xLabel:'Customers contacted',yLabel:'Modeled contribution',valueDecimals:0}}/>
 </Section>
 <Section id="next-test-title" title="Plan a fresh experiment">
  <DataComponent id="power-plan" queryId="power" title="How many customers would we need?" kind="table" variant="card" displayRows={power} sourceRows={power}>
   <p className="eca-body">Use three equally sized groups: the two email versions and a no-email control. Choose the smallest increase worth acting on before enrollment. The estimates below use the historical {pct(power[0].baseline_rate)} control conversion rate.</p>
   <DataTable rows={power} searchable={false} rowKey="row_key" columns={[{field:'absolute_uplift_pp',label:'Worthwhile uplift',renderCell:v=>`${num(v,1)} pp`},{field:'power',label:'Statistical power',renderCell:v=>`${num(v*100)}%`},{field:'customers_per_arm',label:'Per group',renderCell:v=>num(v)},{field:'total_three_arms',label:'Total customers',renderCell:v=>num(v)}]} />
   <p className="eca-note">Normal-approximation planning; two-sided alpha 0.025 per comparison. Power is the chance of detecting the specified effect under the planning assumptions. Refresh the baseline before running a new test, and wait two weeks after the last assignment before final analysis.</p>
  </DataComponent>
 </Section>
 </>;
}
function MethodsView({quality,regression,sensitivity,balance,diag}){
 const cols=[{field:'campaign',label:'Email'},{field:'adjusted_difference',label:'Adjusted uplift',renderCell:pp},{field:'ci_low',label:'95% lower',renderCell:pp},{field:'ci_high',label:'95% upper',renderCell:pp}];
 return <>
 <Section id="methods-title" title="How the analysis was checked" columns={2}>
  <Evidence id="method-details" queryId="campaign_effects" title="Analysis choices" rows={useDataApp().queries.campaign_effects.rows}>
   <ol className="eca-steps"><li><strong>Keep the randomization unit.</strong> Every assigned customer stays in the denominator, including customers who never visited or purchased.</li><li><strong>Define the primary outcome.</strong> Purchase conversion, with two planned email-versus-control comparisons.</li><li><strong>Account for two tests.</strong> Two-sided Fisher exact tests with Holm-adjusted p-values. Displayed main conversion intervals use 97.5% Newcombe intervals.</li><li><strong>Quantify revenue uncertainty.</strong> Resample within assignment groups 5,000 times; report individual 95% percentile intervals.</li><li><strong>Check the conclusion.</strong> Review pre-treatment balance, robust regression and revenue sensitivity without deleting inconvenient observations.</li></ol>
  </Evidence>
  <Evidence id="study-limits" queryId="diagnostics" title="What the data can and cannot establish" rows={diag}>
   <ul className="eca-steps"><li>The source describes random assignment. Observed allocation is consistent with equal groups (chi-square p = {num(diag[0].allocation_p,3)}).</li><li>The largest absolute pre-treatment standardized difference is {num(diag[0].max_abs_smd,3)}. Original delivery and assignment logs are unavailable.</li><li>The study is from 2008 and covers only two weeks. It does not establish long-term retention or current campaign performance.</li><li>No unsubscribe, delivery, campaign-cost or margin data is supplied.</li><li>This project reanalyzes a public experiment. It did not run the original campaign or create the observed sales.</li></ul>
  </Evidence>
 </Section>
 <Section id="robustness-title" title="Robustness checks" columns={2}>
  <DataComponent id="regression-check" queryId="regression" title="Adjust for prior customer characteristics" kind="table" variant="card" displayRows={regression} sourceRows={regression}>
   <DataTable rows={regression} columns={cols} searchable={false} rowKey="campaign"/>
   <p className="eca-note">Linear probability regression with HC3 robust standard errors. Covariates include prior spending, recency, merchandise history, source newbie flag, channel and area type. Sensitivity analysis; not an individual prediction model.</p>
  </DataComponent>
  <DataComponent id="revenue-cap-check" queryId="revenue_sensitivity" title="Reduce the influence of extreme spending" kind="table" variant="card" displayRows={sensitivity} sourceRows={sensitivity}>
   <DataTable rows={sensitivity} searchable={false} rowKey="campaign" columns={[{field:'campaign',label:'Email'},{field:'original_difference',label:'Original uplift',renderCell:v=>usd(v)},{field:'capped_difference',label:'Capped uplift',renderCell:v=>usd(v)}]}/>
   <p className="eca-note">USD per assigned customer. Sensitivity caps spending at the pooled 99.9th percentile ({usd(sensitivity[0].pooled_cap)}), changing the estimand. All main results retain uncapped spending.</p>
  </DataComponent>
 </Section>
 <Section id="quality-title" title="Data validation">
  <DataComponent id="quality-checks" queryId="quality" title={`${quality.filter(r=>r.passed).length} of ${quality.length} data checks passed`} kind="table" variant="card" displayRows={quality} sourceRows={quality}>
   <DataTable rows={quality} rowKey="check" columns={[{field:'check',label:'Check'},{field:'passed',label:'Result',renderCell:v=>v?'Passed':'Failed'},{field:'detail',label:'Evidence'}]}/>
  </DataComponent>
 </Section>
 <Section id="downloads-title" title="Explore the project">
  <div className="eca-downloads"><a href="https://github.com/Shashankpabitwar123/email-campaign-analysis" target="_blank" rel="noreferrer"><strong>Source code & documentation</strong><span>SQL, Python, methods, notebook and resume description</span></a><a href="https://github.com/Shashankpabitwar123/email-campaign-analysis/raw/main/artifacts/Email_Campaign_Budget.xlsx"><strong>Excel budget model</strong><span>Editable assumptions and traceable calculations</span></a><a href="https://github.com/Shashankpabitwar123/email-campaign-analysis/blob/main/docs/decision-memo.md" target="_blank" rel="noreferrer"><strong>Decision memo</strong><span>Findings, recommendation and follow-up test</span></a><a href="https://blog.minethatdata.com/2008/03/" target="_blank" rel="noreferrer"><strong>Original study</strong><span>Kevin Hillstrom's MineThatData public experiment</span></a></div>
  <details className="eca-glossary"><summary>Plain-language statistical glossary</summary><dl><dt>Percentage point</dt><dd>An absolute difference between rates. A rise from 1% to 1.5% is +0.5 percentage points, or +50% relative lift.</dd><dt>Confidence interval</dt><dd>A range produced by a method designed to cover the true effect at its stated rate over repeated comparable samples. Wider ranges mean less precision.</dd><dt>Control group</dt><dd>Customers randomly assigned no email, used to estimate purchases that would happen without a campaign.</dd><dt>Bootstrap</dt><dd>Repeatedly resampling observed customers within each arm to examine variation in the estimated revenue effect.</dd><dt>Multiple comparisons</dt><dd>Testing more than one hypothesis raises the chance of a false positive. The primary analysis corrects for its two planned comparisons.</dd></dl></details>
 </Section>
 </>;
}
export function DashboardContent(){
 const {queries}=useDataApp();const {activeTabId}=useDashboardTabs(tabs);const get=id=>queries[id]?.rows??[];
 const tab=activeTabId??'results';
 if(!get('campaign_summary').length)return <p>Analysis data is unavailable. Reload the page or review the project repository.</p>;
 return <div className="eca-page">{tab==='results'&&<ResultView rows={get('campaign_summary')} effects={get('campaign_effects')} direct={get('direct_comparison')} diag={get('diagnostics')}/>} {tab==='segments'&&<SegmentView/>}{tab==='budget'&&<BudgetView effects={get('campaign_effects')} power={get('power')}/>} {tab==='methods'&&<MethodsView quality={get('quality')} regression={get('regression')} sensitivity={get('revenue_sensitivity')} balance={get('balance')} diag={get('diagnostics')}/>}<p className="eca-footer">Independent portfolio project by Shashank Pabitwar · Historical experiment, 2008 · Analysis prepared September 2026</p></div>;
}
