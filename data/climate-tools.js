/* Monthly statistics for a fixed, versioned regional reanalysis snapshot. */
(function(root){
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  const complete = a => Array.isArray(a) && a.length === 12 && a.every(finite);
  const total = a => complete(a) ? a.reduce((s,v)=>s+v,0) : null;
  const mean = a => complete(a) ? total(a)/12 : null;
  const api = {
    finite, complete, total, mean,
    summary(d){
      const tx=mean(d.tmax),tn=mean(d.tmin);
      return {meanMax:tx,meanMin:tn,diurnalRange:tx!=null&&tn!=null?tx-tn:null,
        annualPrecip:total(d.prec),annualSolar:total(d.sr),meanAH:mean(d.ah),
        wettest:complete(d.prec)?Math.max(...d.prec):null};
    },
    mjToKwh(v){return finite(v)?v/3.6:null;},
    valid(d){return d&&['tmax','tmin','tmean','prec','ah','sr','srDaily'].every(k=>Array.isArray(d[k])&&d[k].length===12);}
  };
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  else root.AtlasClimate=api;
})(typeof window!=='undefined'?window:globalThis);
