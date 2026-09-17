import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const r=JSON.parse(await fs.readFile(path.join(root,'data/processed/results.json'),'utf8'));
const cube=JSON.parse(await fs.readFile(path.join(root,'data/processed/excel_cube.json'),'utf8'));
const out=path.join(root,'artifacts'); await fs.mkdir(path.join(out,'previews'),{recursive:true});
const wb=Workbook.create();
const sheets=Object.fromEntries(['Budget','Campaigns','Segments','Source data','Guide'].map(n=>[n,wb.worksheets.add(n)]));
const money='$#,##0.00;[Red]($#,##0.00);$0.00';
function setup(s,title,subtitle,cols='H'){
 s.showGridLines=false; s.getRange(`A1:${cols}70`).format.font.name='Arial';
 s.getRange(`A1:${cols}70`).format.font.size=11;
 s.getRange(`A1:${cols}70`).format.rowHeight=23;
 s.getRange(`A:${cols}`).format.columnWidth=17;
 s.getRange('A:A').format.columnWidth=4;
 s.getRange(`B2:${cols}2`).merge(); s.getRange('B2').values=[[title]];
 s.getRange('B2').format.font={bold:true,size:22,color:'#16324F'}; s.getRange('B2').format.rowHeight=37;
 s.getRange(`B3:${cols}4`).merge();s.getRange('B3').values=[[subtitle]];s.getRange('B3').format.wrapText=true;
 s.getRange('B3').format.font.color='#586778'; s.freezePanes.freezeRows(6);
}
function header(s,range,labels){const q=s.getRange(range);q.values=[labels];q.format={fill:'#16324F',font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:34};}
function formula(s,cell,f){s.getRange(cell).formulas=[[f]];}
function note(s,range,text){s.getRange(range).merge();s.getRange(range.split(':')[0]).values=[[text]];s.getRange(range).format.wrapText=true;s.getRange(range).format.font.color='#586778';}
function input(s,cell,value){s.getRange(cell).values=[[value]];s.getRange(cell).format={fill:'#FFF1CD',font:{color:'#195AAC',bold:true},borders:{preset:'outside',style:'thin',color:'#DAC389'}};}

const data=sheets['Source data'];setup(data,'Source data','54 disjoint cells from 64,000 customers. Sum counts and revenue; recompute rates from totals. Historical 2008 experiment.','I');
header(data,'B6:I6',['Campaign','Prior channel','Recency','Newbie flag','Customers','Purchasers','Visitors','Revenue']);
data.getRange(`B7:I${6+cube.length}`).values=cube.map(x=>[x.campaign,x.prior_channel,x.recency_band,x.newbie,x.customers,x.purchasers,x.visitors,x.total_revenue]);
data.getRange('B:B').format.columnWidth=24;data.getRange('C:D').format.columnWidth=20;
data.getRange('F7:H60').setNumberFormat('#,##0');data.getRange('I7:I60').setNumberFormat(money);
data.tables.add('B6:I60',true,'SourceCube');
note(data,'B63:I65','Source: Kevin Hillstrom, MineThatData, March 2008 email challenge. The raw extract has no customer ID; repeated profiles were retained. SQL: sql/04_excel_cube.sql. Each person appears once across these cells.');

const c=sheets.Campaigns;setup(c,'Campaign evidence','Assigned-customer denominators preserve the randomized comparison. Confidence intervals and adjusted p-values are calculated in Python.','L');
c.getRange('B:B').format.columnWidth=25;
header(c,'B6:L6',['Assignment','Customers','Purchases','Conversion','Revenue','Per customer','Extra revenue / customer','95% lower','95% upper','Uplift (pp)','Holm p']);
for(let i=0;i<3;i++){
 const row=7+i, arm=r.summary[i], effect=r.effects.find(e=>e.campaign===arm.campaign);
 c.getRange(`B${row}`).values=[[arm.campaign]];
 formula(c,`C${row}`,`=SUMIFS('Source data'!$F$7:$F$60,'Source data'!$B$7:$B$60,B${row})`);
 formula(c,`D${row}`,`=SUMIFS('Source data'!$G$7:$G$60,'Source data'!$B$7:$B$60,B${row})`);
 formula(c,`E${row}`,`=IFERROR(D${row}/C${row},0)`);
 formula(c,`F${row}`,`=SUMIFS('Source data'!$I$7:$I$60,'Source data'!$B$7:$B$60,B${row})`);
 formula(c,`G${row}`,`=IFERROR(F${row}/C${row},0)`);
 if(effect){formula(c,`H${row}`,`=G${row}-$G$7`);c.getRange(`I${row}:J${row}`).values=[[effect.revenue_ci_low,effect.revenue_ci_high]];formula(c,`K${row}`,`=(E${row}-$E$7)*100`);c.getRange(`L${row}`).values=[[effect.p_holm]];}
}
c.getRange('C7:D9').setNumberFormat('#,##0');c.getRange('E7:E9').setNumberFormat('0.00%');c.getRange('F7:J9').setNumberFormat(money);c.getRange('K7:K9').setNumberFormat('0.00" pp"');c.getRange('L7:L9').setNumberFormat('0.00E+00');
const cc=c.charts.add('bar',[c.getRange('B6:B9'),c.getRange('E6:E9')]);cc.setPosition('B12','H27');cc.title='Purchase conversion by assignment';cc.yAxis={numberFormatCode:'0.0%',numberFormatSourceLinked:false};
note(c,'B29:L31','Primary tests: two-sided Fisher exact tests, Holm adjustment across the two email-versus-control contrasts. Revenue is secondary: individual 95% percentile intervals from 5,000 customer-level bootstrap resamples. Merchandise names do not indicate customer gender.');

const b=sheets.Budget;setup(b,'Email campaign budget','Change the yellow inputs. Results are scenarios using historical response estimates, not observed profit or a forecast.','J');
b.getRange('B:B').format.columnWidth=29;b.getRange('C:C').format.columnWidth=25;
header(b,'B6:D6',['Business assumption','Your input','Meaning']);
[['Campaign',"Men's merchandise",'Email creative'],['Customers to contact',10000,'Assigned recipients'],['Contribution margin',.5,'Share of extra revenue retained'],['Cost per email',.05,'USD per assigned recipient'],['Fixed campaign cost',500,'USD per campaign']].forEach((x,i)=>{const rr=7+i;b.getRange(`B${rr}`).values=[[x[0]]];input(b,`C${rr}`,x[1]);b.getRange(`D${rr}:G${rr}`).merge();b.getRange(`D${rr}`).values=[[x[2]]];});
b.getRange('C7').dataValidation={rule:{type:'list',values:["Men's merchandise","Women's merchandise"]}};
b.getRange('C8').dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:1000000}};
b.getRange('C9').dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1}};
for(const cell of ['C10','C11']) b.getRange(cell).dataValidation={rule:{type:'decimal',operator:'between',formula1:0,formula2:1000000}};
b.getRange('C8').setNumberFormat('#,##0');b.getRange('C9').setNumberFormat('0%');b.getRange('C10:C11').setNumberFormat(money);
header(b,'B14:E14',['Scenario result','Estimate','95% effect lower','95% effect upper']);
for(const [row,label] of [[15,'Extra revenue / customer'],[16,'Extra total revenue'],[17,'Contribution before costs'],[18,'Email + fixed costs'],[19,'Contribution after costs']]) b.getRange(`B${row}`).values=[[label]];
for(const [col,source] of [['C','H'],['D','I'],['E','J']]){
 formula(b,`${col}15`,`=_xlfn.XLOOKUP($C$7,Campaigns!$B$8:$B$9,Campaigns!$${source}$8:$${source}$9)`);
 formula(b,`${col}16`,`=$C$8*${col}15`);formula(b,`${col}17`,`=${col}16*$C$9`);
 formula(b,`${col}18`,'=$C$8*$C$10+$C$11');formula(b,`${col}19`,`=${col}17-${col}18`);
}
b.getRange('C15:E19').setNumberFormat(money);b.getRange('B19:E19').format.fill='#E8F2EF';b.getRange('B19:E19').format.font.bold=true;
b.getRange('C19:E19').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#A52734'}}});
b.getRange('B21').values=[['Break-even customers']];formula(b,'C21','=IF(C15*C9-C10>0,ROUNDUP(C11/(C15*C9-C10),0),"No break-even")');b.getRange('C21').setNumberFormat('#,##0');
note(b,'B23:J25','The interval changes only the estimated historical revenue effect. It excludes uncertainty about future customers, costs, margin, and changes since 2008. Negative values are possible. A positive estimate is not a guarantee of profit.');
header(b,'B28:C28',['Contact volume','Modeled contribution']);
for(let i=0;i<=5;i++){const row=29+i;b.getRange(`B${row}`).values=[[i*10000]];formula(b,`C${row}`,`=B${row}*($C$15*$C$9-$C$10)-$C$11`);}
b.getRange('B29:B34').setNumberFormat('#,##0');b.getRange('C29:C34').setNumberFormat(money);
const bc=b.charts.add('line',b.getRange('B28:C34'));bc.setPosition('E28','K43');bc.title='How contact volume changes the decision';bc.yAxis={numberFormatCode:'$#,##0',numberFormatSourceLinked:false};
note(b,'B45:J47','Decision rule: validate the response on a current audience before committing a larger budget. At the default inputs, the men’s creative produces a modeled contribution of about $2,849 for 10,000 contacts. Source: Campaigns tab, columns H–J.');

const s=sheets.Segments;setup(s,'Explore customer segments','Choose one campaign and one prior channel. This is exploratory: subgroup differences do not establish a targeting policy.','I');
s.getRange('B:B').format.columnWidth=27;s.getRange('C:C').format.columnWidth=25;
s.getRange('B6:B7').values=[['Campaign'],['Prior channel']];input(s,'C6',"Men's merchandise");input(s,'C7','Web');
s.getRange('C6').dataValidation={rule:{type:'list',values:["Men's merchandise","Women's merchandise"]}};
s.getRange('C7').dataValidation={rule:{type:'list',values:['Web','Phone','Multichannel']}};
header(s,'B10:F10',['Recency before email','Email customers','Email purchases','Control customers','Control purchases']);
header(s,'G10:I10',['Email conversion','Control conversion','Difference (pp)']);
['1–3 months','4–6 months','7–12 months'].forEach((band,i)=>{
const row=11+i;s.getRange(`B${row}`).values=[[band]];
for(const [col,source,arm] of [['C','F','$C$6'],['D','G','$C$6'],['E','F','"No email"'],['F','G','"No email"']])formula(s,`${col}${row}`,`=SUMIFS('Source data'!$${source}$7:$${source}$60,'Source data'!$B$7:$B$60,${arm},'Source data'!$C$7:$C$60,$C$7,'Source data'!$D$7:$D$60,B${row})`);
formula(s,`G${row}`,`=IFERROR(D${row}/C${row},0)`);formula(s,`H${row}`,`=IFERROR(F${row}/E${row},0)`);formula(s,`I${row}`,`=(G${row}-H${row})*100`);
});
s.getRange('C11:F13').setNumberFormat('#,##0');s.getRange('G11:H13').setNumberFormat('0.00%');s.getRange('I11:I13').setNumberFormat('0.00" pp"');
note(s,'B16:I19','These narrower cells can contain very few purchases. Use this table to form questions, not to select a winning segment. The website provides uncertainty intervals for broader, separately defined segments. Always divide summed purchases by summed customers; do not average percentages.');
header(s,'B22:C22',['Reconciliation check','Result']);
s.getRange('B23:B25').values=[['All source customers'],['All source purchases'],['Revenue total']];
formula(s,'C23',"=SUM('Source data'!F7:F60)");formula(s,'C24',"=SUM('Source data'!G7:G60)");formula(s,'C25',"=SUM('Source data'!I7:I60)");s.getRange('C25').setNumberFormat(money);

const g=sheets.Guide;setup(g,'Start here','A practical guide to the model, evidence and limitations. All monetary amounts are US dollars.','H');
const guide=[
['1. Read the evidence','Campaigns shows the three randomized groups. The no-email group tells us what customers would have done without an assigned email.'],
['2. Change the assumptions','Budget uses yellow input cells. Select an email, audience size, contribution margin, email cost and fixed cost. Formula cells update automatically.'],
['3. Explore carefully','Segments uses SUMIFS on the disjoint source cube. It supports exploratory cuts by prior channel and recency. Small cells have unstable rates.'],
['4. Interpret the results','The men’s email increased purchase conversion by 0.68 percentage points versus no email in this historical experiment. That is about 6.8 extra purchases per 1,000 customers.'],
['5. Understand uncertainty','Conversion tests use Fisher exact and Holm correction. Revenue intervals use 5,000 bootstrap resamples. Costs and margin were not supplied and are assumptions.'],
['6. Plan a current test','Use the project’s sample-size plan and protocol. Re-estimate today’s baseline, define a worthwhile effect, randomize, and wait for complete follow-up.'],
['Source and provenance','Kevin Hillstrom / MineThatData, March 2008 email challenge: https://blog.minethatdata.com/2008/03/ . Dataset: 64,000 past customers; two-week outcomes.'],
['What this project does not prove','No current business profit was observed. No email delivery, opens, unsubscribes, campaign costs or actual customer IDs were supplied. Creative labels do not identify recipient gender.'],
['Reproduce the workbook','Run scripts/analyze.py, scripts/prepare_excel_data.py, then scripts/build_workbook.mjs. Python generates inference; workbook formulas drive scenarios and segment summaries.'],
];
guide.forEach((x,i)=>{const row=6+i*5;g.getRange(`B${row}:H${row}`).merge();g.getRange(`B${row}`).values=[[x[0]]];g.getRange(`B${row}`).format.font.bold=true;note(g,`B${row+1}:H${row+3}`,x[1]);});

wb.recalculate();
const checks=[];
function check(name,condition){checks.push({check:name,passed:!!condition});if(!condition)throw Error(name);}
const near=(a,v)=>typeof a==='number'&&Math.abs(a-v)<1e-7;
check('Default scenario matches Python',near(b.getRange('C19').values[0][0],10000*(r.effects[0].incremental_revenue*.5-.05)-500));
input(b,'C9',0);wb.recalculate();check('Zero margin gives costs only',near(b.getRange('C19').values[0][0],-1000));
input(b,'C9',.5);input(b,'C8',0);wb.recalculate();check('Zero recipients retains fixed costs',near(b.getRange('C19').values[0][0],-500));
input(b,'C8',10000);input(b,'C7',"Women's merchandise");wb.recalculate();check('Campaign selection changes result',near(b.getRange('C19').values[0][0],10000*(r.effects[1].incremental_revenue*.5-.05)-500));
input(b,'C7',"Men's merchandise");wb.recalculate();
for(const sheet of Object.values(sheets)){
 const values=sheet.getUsedRange().values.flat();
 check(`${sheet.name}: no displayed formula errors`,!values.some(v=>typeof v==='string'&&/^#(REF!|DIV\/0!|VALUE!|N\/A|NAME\?|NUM!|SPILL!|CALC!)/.test(v)));
}
check('Workbook customer total',near(s.getRange('C23').values[0][0],64000));
check('Workbook revenue total',near(s.getRange('C25').values[0][0],67258.13));
await fs.writeFile(path.join(out,'workbook-validation.json'),JSON.stringify({engine:'artifact-tool',checks,defaultResult:b.getRange('C19').values[0][0]},null,2));
for(const [name,range] of [['Budget','A1:K47'],['Campaigns','A1:L32'],['Segments','A1:I27'],['Source data','A1:I20'],['Guide','A1:H51']]){
 const p=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(out,'previews',name.replaceAll(' ','_')+'.png'),new Uint8Array(await p.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(out,'Email_Campaign_Budget.xlsx'));
console.log(JSON.stringify({file:'artifacts/Email_Campaign_Budget.xlsx',checks:checks.length,defaultResult:b.getRange('C19').values[0][0]}));
