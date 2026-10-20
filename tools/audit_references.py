"""Screen every distinct supplied reference against Crossref metadata.

Candidate retrieval is not publication verification or full-text claim validation.
Run after tools/review_cases.py. Preserves failed and unindexed references.
"""
import concurrent.futures
import difflib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'data/reference-audit.json'

def lookup(record):
    if record.get('status') != 'verification_pending':
        return record
    q = record['original_citation']
    if any(s in q for s in ['SHIFT ', 'UNESCO', 'Oliver, P.', 'Vellinga, M.', 'Fathy, H.', 'Press.', 'Birkhäuser', 'Routledge', 'Prestel', 'Springer.', 'Documentation']):
        record['lookup_note'] = 'Book, studio or heritage record: requires catalogue/archive and page-level verification.'
        return record
    try:
        url = 'https://api.crossref.org/works?' + urllib.parse.urlencode({'query.bibliographic': q, 'rows': 3})
        req = urllib.request.Request(url, headers={'User-Agent': 'ShiftAtlasReferenceAudit/1.0'})
        d = json.load(urllib.request.urlopen(req, timeout=25))
        record['candidates'] = [{'title': a.get('title', [''])[0], 'doi': a.get('DOI'),
            'authors': a.get('author', []), 'container': a.get('container-title', []),
            'year': a.get('published', {}).get('date-parts', [[]])[0], 'volume': a.get('volume'),
            'page': a.get('page'), 'article_number': a.get('article-number')}
            for a in d['message']['items']]
        record['lookup_note'] = 'Crossref search candidates only; identity and claim support require editorial comparison.'
    except Exception as e:
        record['lookup_note'] = f'Lookup unavailable: {type(e).__name__}. Not evidence of non-existence.'
    time.sleep(.5)
    return record

def main():
    audit = json.loads(PATH.read_text())
    records = list(audit['references'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for i, r in enumerate(pool.map(lookup, records)):
            audit['references'][i] = r
            PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2))
            print(i + 1, '/', len(records), r['id'], r['status'], flush=True)

if __name__ == '__main__':
    main()
