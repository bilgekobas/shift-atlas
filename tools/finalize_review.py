"""Regenerate browser data and review tables without accepting search candidates."""
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    cases = json.loads((ROOT/'data/cases-reviewed.json').read_text())
    refs = json.loads((ROOT/'data/reference-audit.json').read_text())['references']
    lookup = {r['id']: r for r in refs}
    # Keep the large retrieval candidate lists in the audit, outside the browser payload.
    for c in cases:
        c['referenceRecords'] = [{k:v for k,v in lookup[r['id']].items() if k not in ('candidates','lookup_note')} for r in c['referenceRecords']]
        c['refs'] = [r['citation'] for r in c['referenceRecords']]
    (ROOT/'data/cases-reviewed.json').write_text(json.dumps(cases, ensure_ascii=False, indent=2))
    (ROOT/'data/cases-reviewed.js').write_text('// Generated from cases-reviewed.json by tools/finalize_review.py.\nwindow.ATLAS_CASES='+json.dumps(cases, ensure_ascii=False, separators=(',',':'))+';\n')
    p = ROOT/'docs/research-audit.md'
    h=p.read_text().split('\n## Case dispositions')[0]
    h+='\n## Case dispositions\n\n| ID | Case | Responses | Evidence pilot | Remaining verification |\n|---|---|---:|---|---|\n'
    for c in cases:
        h+=f'| {c["id"]} | {c["name"]} | {len(c["re"])} | {"Yes" if c["evidencePilot"] else "No"} | Source text/locators, history, geometry and map-point precision |\n'
    counts=Counter(r['status'] for r in refs)
    h+='\n## Bibliography screening\n\n'+', '.join(f'{n} {k.replace("_"," ")}' for k,n in sorted(counts.items()))+'. Status concerns the reference record, not every associated claim.\n\n[Full reference table](reference-audit.md).\n'
    p.write_text(h)
    rows=['# Reference audit, 20 October 2026','',
          'All supplied reference strings are accounted for. Metadata verification is not claim validation. Candidate search results remain unaccepted leads. Original citations and complete candidate metadata are preserved in [the JSON audit](../data/reference-audit.json).','',
          '| Reference ID | Cases | Current citation | Status / disposition |','|---|---|---|---|']
    for r in refs:
        note=r['status'].replace('_',' ')
        if r.get('verification_url'):note+='; [verification record]('+r['verification_url']+')'
        elif r.get('candidates'):note+='; search leads retained, identity not accepted'
        else:note+='; catalogue/source text required'
        rows.append('| '+r['id']+' | '+', '.join(map(str,r['case_ids']))+' | '+r['citation'].replace('|','/')+' | '+note+' |')
    (ROOT/'docs/reference-audit.md').write_text('\n'.join(rows)+'\n')
    print(dict(counts))

if __name__=='__main__': main()
