"""Standalone SVG of complete logged optimization curves, no corpus payload."""
from pathlib import Path
import json,html,csv
R=Path(__file__).resolve().parent
colors={'F2':'#1565c0','Transformer':'#c62828'}
series={}
for k in colors:
 p=R/'results'/(k+'-curve.jsonl')
 if p.exists():
  rows=[json.loads(s) for s in p.read_text().splitlines()]
  series[k]=[(g[-1]['targets_seen'],sum(r['loss']*(r['targets_seen']-(rows[max(0,i+j-1)]['targets_seen'] if i+j else 0)) for j,r in enumerate(g))/sum(r['targets_seen']-(rows[max(0,i+j-1)]['targets_seen'] if i+j else 0) for j,r in enumerate(g))) for i in range(0,len(rows),100) for g in [rows[i:i+100]]]
for kind,points in series.items():
 with (R/'results'/(kind+'-curve-100-updates.csv')).open('w') as out:
  writer=csv.writer(out);writer.writerow(['targets_seen','target_weighted_nll_100_updates']);writer.writerows(points)
assert series
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="900" height="460" viewBox="0 0 900 460"><rect width="900" height="460" fill="white"/><g font-family="sans-serif" font-size="14" fill="#222">','<text x="70" y="26">Training NLL: target-weighted groups of 100 updates</text>']
for i in range(6):
 x=70+i*154;svg+=[f'<path d="M{x},50V370" stroke="#eee"/><text x="{x-8}" y="395">{i}M</text>']
for y in range(4,10):
 yy=370-(y-4)*53.333;svg+=[f'<path d="M70,{yy}H840" stroke="#ddd"/><text x="35" y="{yy+5}">{y}</text>']
for i,(k,points) in enumerate(series.items()):
 coords=' '.join(f'{70+x/5e6*770:.2f},{370-(y-4)*53.333:.2f}' for x,y in points)
 svg+=[f'<polyline fill="none" stroke="{colors[k]}" stroke-width="2" points="{coords}"/>',f'<text x="{90+i*220}" y="430" fill="{colors[k]}">{html.escape(k)}</text>']
svg+=['<text x="520" y="430">Single seed; training loss is not dev NLL.</text></g></svg>']
(R/'results/learning-curves.svg').write_text('\n'.join(svg)+'\n')
