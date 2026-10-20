const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
const climate=require('../data/climate-tools.js');
const json=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const cases=json('data/cases-reviewed.json'),audit=json('data/case-audit.json'),refs=json('data/reference-audit.json');
assert.equal(cases.length,58);assert.equal(audit.cases.length,58);
assert.equal(new Set(cases.map(c=>c.id)).size,58);
assert.equal(cases.reduce((n,c)=>n+c.re.length,0),199);
assert.equal(cases.filter(c=>c.evidencePilot).length,12);
assert.equal(cases.filter(c=>c.evidencePilot).reduce((n,c)=>n+c.re.length,0),43);
assert.equal(cases.find(c=>c.id===5).re[0].mechanism,'Buffer');
assert.equal(cases.find(c=>c.id===5).re[3].mechanism,'Reduce dependency');
assert.equal(cases.find(c=>c.id===7).re[0].mechanism,'Ventilate');
const ids=new Set(refs.references.map(r=>r.id)),claims=new Set();
for(const c of cases){
 assert(!c.tax?.evidence,'Retired grade remains');
 for(const r of c.referenceRecords)assert(ids.has(r.id));
 for(const r of c.re){
  assert(!claims.has(r.claimId));claims.add(r.claimId);
  assert(r.mechanism&&r.strategyFamily&&r.evidence.conditions&&r.evidence.limitations);
  for(const id of r.evidence.source_ids)assert(ids.has(id));
  if(r.evidence.type==='mechanism_inference')assert.equal(r.evidence.value,null);
 }
}
const ctx={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'data/cases-reviewed.js'),'utf8'),ctx);
assert.equal(JSON.stringify(ctx.window.ATLAS_CASES),JSON.stringify(cases));
assert.equal(climate.mjToKwh(3.6),1);
assert.equal(climate.mean(Array(12).fill(0)),0);
assert.equal(climate.total(Array(12).fill(null)),null);
assert.equal(climate.total([1,2]),null);
assert.equal(climate.mean([0,...Array(11).fill(12)]),11);
const s=climate.summary({tmax:Array(12).fill(30),tmin:Array(12).fill(10),prec:Array(12).fill(100),sr:Array(12).fill(200),ah:Array(12).fill(null)});
assert.equal(s.annualPrecip,1200);assert.equal(s.annualSolar,2400);assert.equal(s.meanAH,null);assert.equal(s.diurnalRange,20);
const snapshot=json('data/climate_cache.json');
assert.equal(snapshot.model,'nasa_power');assert.equal(snapshot.start_date,'1991-01-01');assert.equal(snapshot.end_date,'2020-12-31');
for(const c of cases){
 const key=c.coords.map(v=>v.toFixed(3)).join(',');const d=snapshot.locations[key];
 assert(d,'Missing snapshot '+c.name);assert(climate.valid(d));
 for(const v of ['tmax','tmin','tmean','prec','ah','sr','srDaily'])assert(climate.complete(d[v]),'Incomplete '+key+' '+v);
 assert.equal(d.provenance.days,10958);
 assert(d.prec.every(v=>v>=0));assert(d.sr.every(v=>v>=0));
}
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))if(m[1].trim())new vm.Script(m[1]);
assert(!html.includes('17.8+0.31')&&!html.includes('function fetchFutureClimate'));
assert(html.includes('claimEvidenceHTML(r)')&&html.includes('1991–2020 · NASA POWER'));
console.log('PASS: corpus integrity, 43 pilot claims, references, browser JSON parity, missing/zero statistics, unit conversion, complete 58-case baseline and inline syntax.');
