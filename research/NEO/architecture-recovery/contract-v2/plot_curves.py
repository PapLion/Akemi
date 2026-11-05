"""Standalone SVG curves from executed logs, no smoothing or data selection."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parent/'results'
curves={p.stem.removesuffix('-curve'):json.loads(p.read_text()) for p in sorted(R.glob('[AC]-??-curve.json'))}
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640" viewBox="0 0 1000 640"><rect width="100%" height="100%" fill="white"/>']
colors=['#1565c0','#d84315','#2e7d32','#7b1fa2','#00695c','#5d4037']
for panel,key in enumerate(['lm','acceptance_bce','answer_accuracy']):
 x=70;y=30+panel*205;w=740;h=145;maximum=max(v[key] for vv in curves.values() for v in vv) if key!='answer_accuracy' else 1
 parts.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="15">{html.escape(key)} — raw training minibatch values</text><path d="M{x} {y+15}V{y+15+h}H{x+w}" stroke="black" fill="none"/>')
 for i,(tag,vv) in enumerate(curves.items()):
  pts=' '.join(f'{x+(v["step"]-1)/299*w:.2f},{y+15+h-(v[key]/maximum*h):.2f}' for v in vv)
  parts.append(f'<polyline points="{pts}" fill="none" stroke="{colors[i%len(colors)]}" stroke-width="1"/><text x="830" y="{y+25+i*18}" fill="{colors[i%len(colors)]}" font-family="sans-serif" font-size="13">{html.escape(tag)}</text>')
 parts.append(f'<text x="{x}" y="{y+15+h+18}" font-family="sans-serif" font-size="12">updates 1–300; y max={maximum:.4g}</text>')
parts.append('</svg>');(R/'learning-curves.svg').write_text(''.join(parts));print('SVG curves saved')
