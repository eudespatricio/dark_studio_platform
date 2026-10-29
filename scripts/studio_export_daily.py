"""Lê export do YouTube Studio (xlsx) e imprime a série diária por vídeo. Uso: python scripts/studio_export_daily.py arquivo.xlsx [N]

Fusos: "Video publish time" vem em UTC (Fábrica 19/10 21:30 BRT = 20/10 00:30 UTC aparece como Oct 20). A série diária NÃO está em UTC
(o pico da Fábrica cai em 19/10, antes do envio em UTC), então está em BRT ou PT. Ao cruzar com o ledger, converta o ledger para UTC e trate o dia da série como "local do Studio"."""
import sys, zipfile, collections, xml.etree.ElementTree as ET
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def load(f):
    z = zipfile.ZipFile(f)
    ss = [''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS)]
    def rows(n):
        for r in ET.fromstring(z.read(n)).findall('.//m:row', NS):
            o = []
            for c in r.findall('m:c', NS):
                v = c.find('m:v', NS)
                o.append('' if v is None else (ss[int(v.text)] if c.get('t') == 's' else v.text))
            yield o
    return list(rows('xl/worksheets/sheet1.xml')), list(rows('xl/worksheets/sheet2.xml')), list(rows('xl/worksheets/sheet3.xml'))
if __name__ == '__main__':
    t, g, tot = load(sys.argv[1]); n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    H = g[0]; print('metrica:', H[-1], '| videos na tabela:', len(t) - 2, '| videos no grafico:', len({r[1] for r in g[1:]}))
    iv = len(H) - 1
    d = collections.defaultdict(dict); ti = {}; pub = {}
    for r in g[1:]:
        d[r[1]][r[0]] = float(r[iv]); ti[r[1]] = r[2][:30]; pub[r[1]] = r[3]
    for k, v in sorted(d.items(), key=lambda kv: -sum(kv[1].values()))[:n]:
        print(ti[k], '|', pub[k], '|', int(sum(v.values())), {a[5:]: int(b) for a, b in v.items() if b > 0})
    print('TOTAL', {r[0][5:]: int(float(r[1])) for r in tot[1:] if float(r[1]) > 0})
